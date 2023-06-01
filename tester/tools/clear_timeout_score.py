import sys
sys.path.append('..')
from connector import Connector

timeouts = []

database = Connector()

for submitId in timeouts:
    database.update(table = 'submit', info = {"score": None}, logic = 'AND', submitId = submitId)