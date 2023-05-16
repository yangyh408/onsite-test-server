import os
import time
import traceback
import json
from functools import wraps

def listen(func):
    @wraps(func)  
    def wrapper(func_cls, *args, **kwargs):
        status = {
            'status': 'SUCCESS',
            'cost': time.time(),
            'error_msg': '',
        }
        try:
            result = func(func_cls, *args, **kwargs)
        except Exception as e:
            result = None
            status['status'] = 'ERROR'
            status['error_msg'] = traceback.format_exc()
            # traceback.print_exc(file=open(error_path, 'w+'))
        finally:
            status['cost'] = time.time() - status['cost']
            return status, result
    return wrapper

class TestStatus:
    def __init__(self, record_dir, submitId, pid, database):
        self.error_path = os.path.join(record_dir, "error.txt")
        self.submitId = submitId
        self.database = database
        self.record = {
            'pid': pid,
            'pull': {'status': 'WAITING', 'cost': ''},
            'test': {'status': 'WAITING', 'cost': ''},
            'evaluate': {'status': 'WAITING', 'cost': ''},
            'upload': {'status': 'WAITING', 'cost': ''},
        }
        self._update_database()
        
    def update(self, module, listen_result=None):
        if listen_result:
            self.record[module]['status'] = listen_result['status']
            self.record[module]['cost'] = f"{listen_result['cost']:.2f}"
            if listen_result['error_msg']:
                with open(self.error_path, 'a') as f:
                    f.write(listen_result['error_msg'])
        else:
            self.record[module]['status'] = 'RUNNING'
        self._update_database()
    
    def _update_database(self):
        self.database.update(table = 'submit', info = {"testDetail": json.dumps(self.record)}, logic = 'AND', submitId = self.submitId)
        
    