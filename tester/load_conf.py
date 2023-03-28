import os
from configparser import ConfigParser

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONF_PATH = os.path.join(BASEDIR, 'conf/test_server.conf')

def load_conf():
    competition_info = {}
    
    config = ConfigParser()
    config.read(CONF_PATH)

    tracks = config.get('competitions', 'track').split(',')

    for track in tracks:
        track = track.strip()
        competitions = config.get(track, 'competition_id')
        for competitionId in competitions.split(','):
            competition_info[competitionId.strip()] = track
        
    return competition_info

if __name__ == '__main__':
    print(load_conf())