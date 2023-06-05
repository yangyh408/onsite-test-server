import datetime
import sys
import time
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from connector import Connector

SUBMITTER_ID = '20230430094609'
PAPER_TYPE = 'B'
COMPETITION_ID = '2023031405'
DOCKER_ID = 'yzbyx/atjhyt7txlebsfbcmzh:1.0.1'

if __name__ == '__main__':
    connector = Connector()
    # cur_time = datetime.datetime.now()
    cur_time = date = datetime.datetime(2023, 5, 31, 23, 59, 59)
    submit_info = {
        'submitId': f"s_{cur_time.strftime('%Y%m%d%H%M%S')}_{SUBMITTER_ID}",
        'submitterId': SUBMITTER_ID,
        'competitionId': COMPETITION_ID,
        'paperType': PAPER_TYPE,
        'submitTime': cur_time.strftime('%Y-%m-%d %H:%M:%S'),
        'dockerId': DOCKER_ID,
        'status': 'QUEUING',
    }
    try:
        connector.insert(table = 'submit', info = submit_info)
        print(f"Successfully insert {submit_info['submitId']}, {submit_info['competitionId']}, {submit_info['paperType']}, {submit_info['dockerId']}")
        # time.sleep(5)
    except Exception as e:
        print(f"Failed to insert {submit_info['submitId']}, with error: {repr(e)}")
        