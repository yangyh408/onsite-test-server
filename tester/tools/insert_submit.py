import datetime
import sys
import time
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from connector import Connector

SUBMITTER_ID = '20230307123639'
PAPER_TYPE = 'C'
COMPETITION_IDS = ['2023031602', '2023031603', '2023031601']
DOCKER_IDS = [
    ['reshweici/kp487cmtf8mzxv:0.0.3', 'sssusheng/effigy-trophy-gypsy-thump:0.0.1', 'anbc/31c18sampr4-workflow-test:v4'],
    ['sssusheng/effigy-trophy-gypsy-thump:0.0.1'],
    ['huzhilong/test:1.0.1'],
]

if __name__ == '__main__':
    connector = Connector()
    for cometitionId, dockerIds in zip(COMPETITION_IDS, DOCKER_IDS):
        for dockerId in dockerIds:
            cur_time = datetime.datetime.now()
            submit_info = {
                'submitId': f"s_{cur_time.strftime('%Y%m%d%H%M%S')}_{SUBMITTER_ID}",
                'submitterId': SUBMITTER_ID,
                'competitionId': cometitionId,
                'paperType': PAPER_TYPE,
                'submitTime': cur_time.strftime('%Y-%m-%d %H:%M:%S'),
                'dockerId': dockerId,
                'status': 'QUEUING',
            }
            try:
                connector.insert(table = 'submit', info = submit_info)
                print(f"Successfully insert {submit_info['submitId']}, {submit_info['competitionId']}, {submit_info['paperType']}, {submit_info['dockerId']}")
                time.sleep(5)
            except Exception as e:
                print(f"Failed to insert {submit_info['submitId']}, with error: {repr(e)}")
        