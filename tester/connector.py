import datetime
import time
import pymysql
from dbutils.pooled_db import PooledDB
from logger import db_logger

HOSTNAME = "sh-cynosdbmysql-grp-lqu1mnle.sql.tencentcdb.com"
PORT = 23574
USERNAME = "root"
PASSWORD = "Ljq20020717"
DATABASE = "onsite"

class Connector():
    def __init__(self) -> None:
        self.mysql_pool = PooledDB(creator=pymysql,
                                   blocking=True,
                                   ping=4,
                                   host=HOSTNAME, 
                                   port=PORT, 
                                   user=USERNAME,
                                   password=PASSWORD,
                                   db=DATABASE,
                                   charset='utf8'
                                   )
        self.columns = []
        self._get_col_name("submit")
    
    def _connect(self):
        conn = self.mysql_pool.connection()
        cur = conn.cursor()
        return conn, cur
    
    def _close_connection(self, conn, cur):
        cur.close()
        conn.close()
    
    def insert(self, *, table, info):
        key = str(list(info.keys()))[1:-1].replace('\'', '')
        val = str(list(info.values()))[1:-1]
        script = f"INSERT INTO {table} ({key}) VALUES ({val})"
        db_logger.info(script)
        return self._db_commit(script)
    
    def update(self, *, table, info, logic, **kwargs):
        check_lst = self._restyle_dict(kwargs)
        update_lst = self._restyle_dict(info)
        script = (f"UPDATE {table} SET {', '.join(update_lst)} WHERE {f' {logic} '.join(check_lst)}")
        db_logger.info(script)
        return self._db_commit(script)
    
    def get_submits(self, *, submitId = None, refresh = False):
        if submitId:
            for row_info in self._get_value(table='submit', field='*', logic='AND', submitId=submitId):
                yield dict(zip(self.columns, row_info))
        else:
            while True:
                submits = self._get_value(table='submit', field='*', logic='AND', status="QUEUING")
                for row_info in submits:
                    yield dict(zip(self.columns, row_info))
                if refresh:
                    time.sleep(5)
                else:
                    break
    
    def _get_value(self, *, table, field, logic, **kwargs):
        if kwargs:
            check_lst = self._restyle_dict(kwargs)
            script = f"SELECT {field} FROM {table} WHERE {f' {logic} '.join(check_lst)}"
        else:
            script = f"SELECT {field} FROM {table}"
        return self._db_fetch(script)
        
    def _restyle_dict(self, dict_info):
        res = []
        for k, v in dict_info.items():
            if type(v) == str:
                res.append(f"{k}='{v}'")
            elif v is None:
                res.append(f"{k}=NULL")
            else:
                res.append(f"{k}={v}")
        return res
        
    def _get_col_name(self, table):
        script = f"show columns from {table}"
        for row_info in self._db_fetch(script):
            self.columns.append(row_info[0])

    def _db_fetch(self, script):
        conn, cur = self._connect()
        try:
            cur.execute(script)
            return cur.fetchall()
        except Exception as e:
            db_logger.exception(script)
            return []
        finally:
            self._close_connection(conn, cur)
    
    def _db_commit(self, script):
        conn, cur = self._connect()
        try:
            cur.execute(script)
            conn.commit()
            return True
        except Exception as e:
            db_logger.exception(script)
            return False
        finally:
            self._close_connection(conn, cur)
    
def get_submitterId(connector, username):
    res = connector._get_value(table='user', field='userId', logic='AND', userName=username)
    if res:
        return res[0][0]
    else:
        return None

def get_competition_info(connector, competition_name):
    res = connector._get_value(table='competition', field='competitionId, switchTime', logic='AND', competitionName=competition_name)
    if res:
        competitionId, switchTime = res[0]
        if datetime.datetime.now() <= switchTime:
            return competitionId, 'A'
        else:
            return competitionId, 'B'
    else:
        return None, None
    
def db_insert(connector, *, user, dockerid, competition):
    if dockerid is None or competition is None:
        err = f"Please provide complete parameters: 'dockerId', 'competitionName'"
        return False, err
    submitterId = get_submitterId(connector, user)
    if submitterId is None:
        err = f"Cannot find user {user} in database!"
        return False, err
    competitionId, paperType = get_competition_info(connector, competition)
    if competitionId is None:
        err = f"Cannot find competition {competition} in database!"
        return False, err
    cur_time = datetime.datetime.now()
    submit_info = {
        'submitId': f"s_{cur_time.strftime('%Y%m%d%H%M%S')}_{submitterId}",
        'submitterId': submitterId,
        'competitionId': competitionId,
        'paperType': paperType,
        'submitTime': cur_time.strftime('%Y-%m-%d %H:%M:%S'),
        'dockerId': dockerid,
        'status': 'QUEUING',
    }
    try:
        connector.insert(table = 'submit', info = submit_info)
    except Exception as e:
        return False, repr(e)
    
    return True, submit_info
    
if __name__ == '__main__':
    c = Connector()
    # submit_info = {
    #     'submitId': 'test1',
    #     'submitterId': 'test_user1',
    #     'competitionId': 'com1',
    #     'submitTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #     'dockerId': 123
    # }
    # print(c.insert('submit', submit_info))
    # import datetime
    # update_info = {
    #     'score': 12.34,
    #     'testTime': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #     'resultLink': None,
    # }
    # print(c.update(table = 'submit', info = update_info, logic = 'AND', submitId = 's_20230316035938_20230307123639'))
    # for submit_info in c.get_submits(refresh=True):
    #     print(submit_info)
    for x in c.get_submits(submitId='s_20230316035938_20230307123639'):
        print(x)