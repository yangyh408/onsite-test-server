from atexit import register
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Pool
from flask import Flask
from flask import request
from flask import jsonify
from flask_cors import CORS
from flask_cors import cross_origin
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_jwt_extended import get_jwt_identity
import os
import sys

from connector import *
from tester import Tester
from logger import logger
from tester_pool import TesterPool

INPUT_DIR = os.path.join(os.path.dirname(__file__), '../inputs')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '../outputs')

app = Flask(__name__)

app.config["JWT_COOKIE_SECURE"] = True
app.config["JWT_SECRET_KEY"] = "ljdyaishijin**3nkjnj??"
app.config["JWT_IDENTITY_CLAIM"] = "username"
app.config["JWT_HEADER_NAME"] = "token"
app.config["JWT_HEADER_TYPE"] = ""

CORS(app)
jwt = JWTManager(app)
db = Connector()
# pool = TesterPool(INPUT_DIR, OUTPUT_DIR, db)
pool = ProcessPoolExecutor(2)
        
def run_tester(submit_info):
    logger.debug(f"[pid:{os.getpid()}] submitId:{submit_info['submitId']}  ==PUSH==> ProcessPool")
    try:
        db.update(table = 'submit', info = {"status": "TESTING"}, logic = 'AND', submitId = submit_info['submitId'])
        test_module = Tester(INPUT_DIR, OUTPUT_DIR)
        result = test_module.test(submit_info)
        logger.info(f"{submit_info['submitId']}: {result}")
        db.update(table = 'submit', info = result, logic = 'AND', submitId = submit_info['submitId'])
    except Exception as e:
        logger.exception(f"[main error]: run_tester collapse for submit:{submit_info}")
    finally:
        logger.debug(f"[pid:{os.getpid()}] submitId:{submit_info['submitId']}  <==POP== ProcessPool")

# @register
# def _onexit(e):
#     # tb_str = ''.join(traceback.format_exception(*sys.exc_info()))  # obtain traceback info
#     logger.critical("Flask Server is shut down!") 
        
@app.route('/submit', methods=['POST'])
@cross_origin()
@jwt_required(locations=["headers"])
def submit():
    username = get_jwt_identity()
    docker_id = request.args.get('dockerId')
    competition_name = request.args.get('competitionName')
    status, submit_info = db_insert(db, user=username, dockerid=docker_id, competition=competition_name)
    if status:
        # pool.submit(run_tester, submit_info)
        logger.info(f"Req({username}, {docker_id}, {competition_name}), Res({submit_info})")
        return jsonify(code=20000, data=submit_info, msg='success')
    else:
        logger.critical(f"Req({username}, {docker_id}, {competition_name}), Res({submit_info})")
        return jsonify(code=50000, data=submit_info, msg='fail') 

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)