from concurrent.futures import ProcessPoolExecutor
import os
from tester import Tester
from logger import logger, print_logger
from load_conf import load_conf

select_submitId = ""                # Keep it "" unless you want to test a specific submitId
competition_info = load_conf()

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_ROOT_DIR = os.path.join(BASEDIR, 'scenes')
OUTPUT_DIR = os.path.join(BASEDIR, 'temp')
ERROR_LOG_DIR = os.path.join(BASEDIR, 'log/error_log')

pool = ProcessPoolExecutor()
test_module = Tester(OUTPUT_DIR, ERROR_LOG_DIR)
        
def run_tester(submit_info, input_dir):
    try:
        # db.update(table = 'submit', info = {"status": "TESTING", "testTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, logic = 'AND', submitId = submit_info['submitId'])
        test_module = Tester(input_dir, OUTPUT_DIR, db)
        result = test_module.test(submit_info)
        # db.update(table = 'submit', info = result, logic = 'AND', submitId = submit_info['submitId'])
        logger.info(f"{result}", extra={'submitId': submit_info['submitId']})
    except Exception as e:
        logger.exception(f"[CRITICAL]: run_tester collapse for submit:{submit_info}", extra={'submitId': submit_info['submitId']})
    # finally:
        # logger.debug(f"|pid:{os.getpid()}| submitId:{submit_info['submitId']}  <==POP== ({len(pool_pids)}/{pool._max_workers})ProcessPool{pool_pids}")


for submit_info in db.get_submits(submitId=select_submitId, refresh=True):
# for submit_info in db.get_submits(submitId='s_20230316035938_20230307123639'):
    if submit_info['competitionId'] in competition_info.keys():
        input_dir = os.path.join(INPUT_ROOT_DIR, submit_info['paperType'], competition_info[submit_info['competitionId']], 'inputs')
        if os.path.exists(input_dir):
            print_logger.info(f"Detect new submition: {submit_info['submitId']} (DockerId:{submit_info['dockerId']})")
            pool.submit(run_tester, submit_info, input_dir)
        else:
            print_logger.error(f"Invalid input dir: {input_dir}!")
    else:
        print_logger.error(f"Competition(id:{submit_info['competitionId']}) is not in test list!")