import os
import shlex
import subprocess
from logger import debugger, logger

class DockerTool:
    def __init__(self, input_path, output_path, submitId):
        self.input_path = input_path
        self.output_path = output_path
        self.submitId = submitId
    
    def run(self, docker_id: str, pull=True) -> str:
        """
            测试docker_id对应的镜像
        Args:
            docker_id (str): 用户提交的待测试dockerid
            pull (bool, optional): 是否拉取得镜像. Defaults to True.
        Returns:
            str: 返回dockerid对应镜像的拉取和测试状态
                 "SUCCESS" -> 测试成功
                 "No such image" -> 无对应镜像
                 "Pull error" -> 拉取镜像失败
                 "Container error" -> 被测物测试时出错
        """
        if pull:
            status = self._pull_docker(docker_id)
        if status == 'SUCCESS': 
            status = self._test_docker(docker_id)
            self._delete_image(docker_id)
        return status

    @debugger('cls')
    def _pull_docker(self, docker_id: str) -> str:
        res = 'SUCCESS'
        # print("  - [Pull] Pulling: ", docker_id)
        command = f"docker pull {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            if 'not found' in stderr:
                res = 'IMAGE NOT FOUND'
            else:
                res = 'PULL ERROR'
            logger.error(f"[{res}]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
            with open(os.path.join(self.output_path, 'error.txt'), 'w') as f:
                f.write(str(stderr))
        # print(f"  - [Pull] Done with status '{res}'")
        return res

    @debugger('cls')
    def _test_docker(self, docker_id: str) -> str:
        res = 'SUCCESS'
        # print('  - [Test] Testing: ', docker_id)
        command = f"docker run --volume {self.input_path}:/inputs --volume {self.output_path}:/outputs {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            res = "CONTAINER ERROR"
            logger.error(f"[{res}]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
            with open(os.path.join(self.output_path, 'error.txt'), 'w') as f:
                f.write(stderr)
        else:
            stdout = result.stdout.decode()
            with open(os.path.join(self.output_path, 'container_logs.txt'), 'w') as f:
                f.write(stdout)
        # print(f"  - [Test] Done with status '{res}'")
        return res
    
    def _delete_image(self, docker_id: str) -> str:
        command = f"docker rmi -f {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            logger.error(f"[DELETE IMAGE FAIL]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
    
    def _run_command(self, command: str):
        return subprocess.run(shlex.split(command), capture_output=True)

if __name__ == '__main__':
    input_path = r"/media/yangyh408/YangYH408/test_scenario/inputs"
    output_path = r"/media/yangyh408/YangYH408/onsite-develop/onsite-test-server/temp"
    d = DockerTool(input_path, output_path)
    d.run("huangyan520/test-image-for-onsite:0.1.6")

