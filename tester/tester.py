import os
import shutil
import datetime

from docker_tool import DockerTool
from uploader import Uploader
from run_evaluator import RunEvaluator

class Tester():
    def __init__(self, input_dir: str, output_dir: str) -> None:
        self.input_dir = os.path.abspath(input_dir)
        self.output_root_dir = os.path.abspath(output_dir)
        self.run_status = {
            'pull': None,
            'test': None,
            'evaluate': None,
            'upload': None,
            'errMsg': None,
        }

    def test(self, submit_info: dict) -> dict:
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
        output_dir = os.path.join(self.output_root_dir, submit_info['submitId'])
        self._reset_dir(output_dir)
        # print("Run testing:")
        # print(f"  - [config]: {submit_info['competitionId']}-{submit_info['submitterId']}-{submit_info['submitTime']}-{submit_info['dockerId']}")
        
        docker = DockerTool(self.input_dir, output_dir, submit_info['submitId'])
        docker_status = docker.run(submit_info['dockerId'])
        
        uploader = Uploader(self.output_root_dir, submit_info['submitId'])

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