import os
from configparser import ConfigParser

def load_conf(conf_path):
    competition_info = {}
    
    config = ConfigParser()
    config.read(conf_path)

    tracks = config.get('competitions', 'track').split(',')

    for track in tracks:
        track = track.strip()
        competitions = config.get(track, 'competition_id')
        for competitionId in competitions.split(','):
            competition_info[competitionId.strip()] = track
        
    return competition_info

if __name__ == '__main__':
    print(load_conf())