import os
import time
import shutil
import zipfile

import upyun
from test_status import listen

class Uploader:
    def __init__(self, output_root_dir, submit_info):
        self.zip_file_name = self._update_zip_file_name(submit_info['submitterId'], submit_info['submitTime'])
        self.zip_file_path = os.path.join(output_root_dir, self.zip_file_name)
        self.output_dir = os.path.join(output_root_dir, submit_info['submitId'])
        self.remote_dir = rf"/results/{submit_info['competitionId']}/"
        
    def _connect(self, username = "zhouhuajun", password = "q9ieC21p1yRaHYGqFo0N5x7OoedsDVla"):
        self.up = upyun.UpYun('onsite', username=username, password=password, endpoint=upyun.ED_AUTO)
    
    def upload(self):
        retry_times = 10
        while retry_times := retry_times - 1:
            upload_listen, _ = self._upload_file()
            if upload_listen['status'] == 'SUCCESS':
                break
            else:
                time.sleep(5)
        
        if upload_listen['status'] == 'SUCCESS':
            self._delete_file(self.zip_file_path)
            # shutil.rmtree(self.output_dir)
            return upload_listen, 'https://resource.onsite.run' + self.remote_dir + self.zip_file_name
        else:
            return upload_listen, None
    
    @listen
    def _upload_file(self):
        self._connect()
        self._zip_dir(self.output_dir, self.zip_file_path)
        self._to_upyun(self.zip_file_path)

    def _update_zip_file_name(self, userid, submit_time):
        return f"{userid}&{submit_time}.zip".replace(":", "-").replace(" ", "_")

    def _zip_dir(self, output_path, zip_file):
        # print(f"    --> zipping: {output_path} -zip-> {zip_file}")
        zip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(output_path):
            fpath = path.replace(output_path, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    def _to_upyun(self, zip_file):
        with open(zip_file, 'rb') as f:
            self.up.put(self.remote_dir + self.zip_file_name, f, checksum=True)
    
    def _delete_file(self, file_name):
        # print(f"    --> delete_temp: {self.zip_file_dir, self.zip_file_name}")
        os.remove(file_name)


if __name__ == "__main__":
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    INPUT_ROOT_DIR = os.path.join(BASEDIR, 'scenes')
    OUTPUT_DIR = os.path.join(BASEDIR, 'temp')
    ERROR_LOG_DIR = os.path.join(BASEDIR, 'log/error_log')
    
    from tester import Tester
    test_module = Tester(OUTPUT_DIR, ERROR_LOG_DIR)
    for submit_info in test_module.db.get_submits(submitId='s_20230331080127_20230307123639'):
        uploader = Uploader(test_module.output_root_dir, submit_info)
        print(uploader.upload())
        # test_module.test(r"/home/ubuntu/onsite-test-server/scenes/A/test/inputs", submit_info)