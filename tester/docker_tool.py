import os
import shlex
import subprocess
from test_status import listen

class DockerTool:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
    
    def run(self, docker_id: str, test_status: object) -> str:
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
        test_status.update('pull')
        pull_listen, (docker_status, pull_error) = self._pull_docker(docker_id)
        if docker_status == 'SUCCESS': 
            test_status.update('pull', pull_listen)
            test_status.update('test')
            test_listen, (docker_status, test_error) = self._test_docker(docker_id)
            if docker_status != 'SUCCESS':
                test_listen['status'] = 'ERROR'
                test_listen['error_msg'] = test_error
            test_status.update('test', test_listen)
            self._delete_image(docker_id)
        else:
            pull_listen['status'] = 'ERROR'
            pull_listen['error_msg'] = pull_error
            test_status.update('pull', pull_listen)
        return docker_status

    @listen
    def _pull_docker(self, docker_id: str) -> str:
        res = 'SUCCESS'
        stderr = ''
        # print("  - [Pull] Pulling: ", docker_id)
        command = f"docker pull {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            if 'not found' in stderr:
                res = 'IMAGE NOT FOUND'
            else:
                res = 'PULL ERROR'
            # logger.error(f"[{res}]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
            with open(os.path.join(self.output_path, 'error.txt'), 'w') as f:
                f.write(str(stderr))
        # print(f"  - [Pull] Done with status '{res}'")
        return res, stderr

    @listen
    def _test_docker(self, docker_id: str) -> str:
        res = 'SUCCESS'
        stderr = ''
        # print('  - [Test] Testing: ', docker_id)
        command = f"docker run --volume {self.input_path}:/inputs --volume {self.output_path}:/outputs {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            res = "CONTAINER ERROR"
            # logger.error(f"[{res}]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
            with open(os.path.join(self.output_path, 'error.txt'), 'w') as f:
                f.write(stderr)
        else:
            stdout = result.stdout.decode()
            with open(os.path.join(self.output_path, 'container_logs.txt'), 'w') as f:
                f.write(stdout)
        # print(f"  - [Test] Done with status '{res}'")
        return res, stderr
    
    def _delete_image(self, docker_id: str) -> str:
        command = f"docker rmi -f {docker_id}"
        result = self._run_command(command)
        if result.returncode != 0:
            stderr = result.stderr.decode()
            # logger.error(f"[DELETE IMAGE FAIL]:\n{(stderr).strip()}", extra={'submitId': self.submitId})
    
    def _run_command(self, command: str):
        return subprocess.run(shlex.split(command), capture_output=True)

if __name__ == '__main__':
    input_path = r"/home/ubuntu/onsite-test-server/scenes/A/test/inputs"
    output_path = r"/home/ubuntu/onsite-test-server/temp/test_docker_outputs"
    d = DockerTool(input_path, output_path)
    print(d.run("huangyan520/test-image-for-onsite:0.1.6"))
    print(d.run("123456"))

