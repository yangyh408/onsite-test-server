# from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool, Manager

import os
import json
import datetime
from tester import Tester
from connector import Connector
from logger import logger, print_logger
from load_conf import load_conf
        
def run_tester(cpu_cores, submit_info, input_dir):
    try:
        core_num = cpu_cores.get()
        os.sched_setaffinity(os.getpid(), [core_num])
        
        test_module = Tester(OUTPUT_DIR, RECORD_DIR)
        logger.debug(f"[pid:{os.getpid()} core_num:{core_num}] {submit_info}", extra={'submitId': submit_info['submitId']})
        
        test_module.db.update(table = 'submit', info = {"status": "TESTING", "testTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, logic = 'AND', submitId = submit_info['submitId'])
        result = test_module.test(input_dir, submit_info, core_num)
        test_module.db.update(table = 'submit', info = result, logic = 'AND', submitId = submit_info['submitId'])
    except Exception as e:
        logger.exception(f"[CRITICAL]: run_tester collapse for submit:{submit_info}", extra={'submitId': submit_info['submitId']})
    finally:
        # logger.debug(f"|pid:{os.getpid()}| submitId:{submit_info['submitId']}  <==POP== ({len(pool_pids)}/{pool._max_workers})ProcessPool{pool_pids}")
        cpu_cores.put(core_num)
        
def run_evaluator(cpu_cores, submit_info, input_dir):
    try:
        core_num = cpu_cores.get()
        os.sched_setaffinity(os.getpid(), [core_num])
        
        test_module = Tester(OUTPUT_DIR, RECORD_DIR)
        logger.debug(f"[pid:{os.getpid()} core_num:{core_num}] {submit_info}", extra={'submitId': submit_info['submitId']})
        
        result = test_module.evaluate(input_dir, submit_info, core_num)
        test_module.db.update(table = 'submit', info = result, logic = 'AND', submitId = submit_info['submitId'])
    except Exception as e:
        logger.exception(f"[CRITICAL]: run_tester collapse for submit:{submit_info}", extra={'submitId': submit_info['submitId']})
    finally:
        cpu_cores.put(core_num)

if __name__ == '__main__':
    DEBUG_MODE = False

    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    INPUT_ROOT_DIR = os.path.join(BASEDIR, 'scenes')
    OUTPUT_DIR = os.path.join(BASEDIR, 'temp')
    RECORD_DIR = os.path.join(BASEDIR, 'record')

    # pool = ProcessPoolExecutor()
    pool = Pool()
    cpu_cores = Manager().Queue()
    for i in range(os.cpu_count()):
        cpu_cores.put(i)

    database = Connector()
    if DEBUG_MODE:
        competition_info = load_conf(os.path.join(BASEDIR, 'conf/test_server_2.conf'))
        for submit_info in database.get_submits(submitId='', refresh=True):
            if submit_info['competitionId'] not in ['2023031405', '2023031901', '2023031902', '2023031903']:
                input_dir = os.path.join(INPUT_ROOT_DIR, submit_info['paperType'], competition_info[submit_info['competitionId']], 'inputs')
                print(f"Detect new submition: {submit_info['submitId']} (DockerId:{submit_info['dockerId']})")
                pool.apply_async(func=run_tester, args=(cpu_cores, submit_info, input_dir), error_callback=lambda e: print(e))
    else:
        competition_info = load_conf(os.path.join(BASEDIR, 'conf/test_server.conf'))
        for row_info in database._get_value(table='submit', field='*', logic='AND', status="TESTING"):
            submit_info = dict(zip(database.columns, row_info))
            test_detail = json.loads(submit_info["testDetail"])
            if test_detail["evaluate"]["status"] == "RUNNING":
                input_dir = os.path.join(INPUT_ROOT_DIR, submit_info['paperType'], competition_info[submit_info['competitionId']], 'inputs')
                output_dir = os.path.join(OUTPUT_DIR, submit_info['submitId'])
                if os.path.exists(input_dir) and os.path.exists(output_dir):
                    print(f"Continue evaluating: {submit_info['submitId']} (DockerId:{submit_info['dockerId']})")
                    pool.apply_async(func=run_evaluator, args=(cpu_cores, submit_info, input_dir))
        
        competition_info = load_conf(os.path.join(BASEDIR, 'conf/test_server_2.conf'))
        for submit_info in database.get_submits(submitId='', refresh=True):
            if submit_info['competitionId'] in competition_info.keys():
                input_dir = os.path.join(INPUT_ROOT_DIR, submit_info['paperType'], competition_info[submit_info['competitionId']], 'inputs')
                if os.path.exists(input_dir):
                    print_logger.info(f"Detect new submition: {submit_info['submitId']} (DockerId:{submit_info['dockerId']})")
                    # pool.submit(run_tester, submit_info, input_dir)
                    database.update(table = 'submit', info = {"status": "WAITING"}, logic = 'AND', submitId = submit_info['submitId'])
                    pool.apply_async(func=run_tester, args=(cpu_cores, submit_info, input_dir))
                else:
                    print_logger.error(f"Invalid input dir: {input_dir}!")