import os
import shutil
import datetime

from test_status import TestStatus
from connector import Connector
from docker_tool import DockerTool
from uploader import Uploader
from run_evaluator import RunEvaluator

class Tester():
    def __init__(self, output_dir: str, error_log_dir: str) -> None:
        self.output_root_dir = os.path.abspath(output_dir)
        self.error_log_dir = os.path.abspath(error_log_dir)
        
        self.db = Connector()

    def test(self, input_dir: str, submit_info: dict) -> dict:
        """
            根据dockerid进行测试，并返回该轮测试评分，流程为：
                1. docker处理： 拉取镜像、运行测试
                2. evaluator评分
                3. upyun打包上传outputs文件
        Args:
            submit_info (dict): 一次提交中数据库内所有字段的数据
        Returns:
            result (dict): 
                'status': 测试状态
                            "SUCCESS" -> 测试成功
                            "IMAGE NOT FOUND" -> 未找到镜像
                            "PULL ERROR" -> 镜像拉取失败
                            "CONTAINER ERROR" -> 镜像测试失败
                            'EVALUATE ERROR' -> 计算得分失败
                            'UPLOAD ERROR' ->  上传结果失败
                'score': 测试得分（仅在status为SUCCESS的情况下输出得分，否则为'-'）
                'testTime': 测试时间
                'resultLink': outputs文件夹又拍云下载链接（仅在status为SUCCESS的情况下有值，否则为None）
        """
        self.db.update(table = 'submit', info = {"status": "TESTING", "testTime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, logic = 'AND', submitId = submit_info['submitId'])
        
        output_dir = os.path.join(self.output_root_dir, submit_info['submitId'])
        self._reset_dir(output_dir)
        
        test_status = TestStatus(self.error_log_dir, submit_info['submitId'], self.db)
        docker = DockerTool(input_dir, output_dir)
        
        test_status.update('pull')
        pull_listen, (docker_status, pull_error) = docker._pull_docker(submit_info['dockerId'])
        if docker_status == 'SUCCESS': 
            test_status.update('pull', pull_listen)
            test_status.update('test')
            test_listen, (docker_status, test_error) = docker._test_docker(submit_info['dockerId'])
            if docker_status != 'SUCCESS':
                test_listen['status'] = 'ERROR'
                test_listen['error_msg'] = test_error
            test_status.update('test', test_listen)
            docker._delete_image(submit_info['dockerId'])
        else:
            pull_listen['status'] = 'ERROR'
            pull_listen['error_msg'] = pull_error
            test_status.update('pull', pull_listen)

        uploader = Uploader(self.output_root_dir, submit_info)

        if docker_status == 'SUCCESS':
            evaluator = RunEvaluator(submit_info['submitId'], save_record = True)
            score = evaluator.evaluate(self.input_dir, output_dir)
            if score == -1:
                upyun_link = uploader.upload(submit_info['competitionId'], submit_info['submitterId'], submit_info['submitTime'], output_dir)
                result = self._result('EVALUATE ERROR', None, upyun_link)
                return result
            
            upyun_link = uploader.upload(submit_info['competitionId'], submit_info['submitterId'], submit_info['submitTime'], output_dir)
            if upyun_link:
                result = self._result('SUCCESS', score, upyun_link)
            else:
                result = self._result('UPLOAD ERROR', score, None)
        else:
            upyun_link = uploader.upload(submit_info['competitionId'], submit_info['submitterId'], submit_info['submitTime'], output_dir)
            result = self._result(docker_status, None, upyun_link)
        return result
    
    def _result(self, status, score, resultLink):
        result = {
            'status': status,
            'score': score,
            'resultLink': resultLink,
        }
        return result

    def _reset_dir(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        else:
            shutil.rmtree(file_path)
            os.mkdir(file_path)
            
            
if __name__ == '__main__':
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    INPUT_ROOT_DIR = os.path.join(BASEDIR, 'scenes')
    OUTPUT_DIR = os.path.join(BASEDIR, 'temp')
    ERROR_LOG_DIR = os.path.join(BASEDIR, 'log/error_log')

    test_module = Tester(OUTPUT_DIR, ERROR_LOG_DIR)
    for submit_info in test_module.db.get_submits(submitId='s_20230331080127_20230307123639'):
        test_module.test(r"/home/ubuntu/onsite-test-server/scenes/A/test/inputs", submit_info)
    # import json
    # a = json.loads(test_module.db._get_value(table='submit', field='testDetail', logic='AND', submitId='s_20230331080127_20230307123639')[0][0])
    # print(a)
    # print(a['pull'])