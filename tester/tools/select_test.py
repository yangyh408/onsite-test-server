import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from connector import Connector

import shlex
import subprocess

c = Connector()
remote_file_path = os.path.join(os.path.dirname(__file__), 'sign_up.csv')
local_dir = "/Users/yangyh408/Desktop"

with open(remote_file_path, 'w', encoding='gbk') as f:
    f.write(f'userName,school,supervisorName,competitionName\n')
    for id_, name, school, sup in c._get_value(table='user', field='userId, userName, school, supervisorName', logic='AND'):
        competition_name = []
        for competition in c._get_value(table='entry', field='competitionId', logic='AND', participantId=id_):
            try:
                competition_name.append(c._get_value(table='competition', field='competitionName', logic='AND', competitionId=competition[0])[0][0])
            except Exception as e:
                pass
        f.write(f'{name},{school},{sup},{",".join(competition_name)}\n')
        print(name, school, sup, competition_name)
        
command = f"scp -r ubuntu@test_server:{remote_file_path} {local_dir}"
subprocess.run(shlex.split(command), capture_output=True)