import os
import shutil
import zipfile

import upyun
from logger import debugger, logger

class Uploader:
    def __init__(self, zip_dir, submitId):
        self.remote_dir = r"/results/"
        self.zip_file_name = None
        
        self.zip_file_dir = zip_dir
        self.submitId = submitId
        
        
    def _connect(self, username = "zhouhuajun", password = "q9ieC21p1yRaHYGqFo0N5x7OoedsDVla"):
        self.up = upyun.UpYun('onsite', username=username, password=password, endpoint=upyun.ED_AUTO)
    
    @debugger('cls')
    def upload(self, competitionid, userid, submit_time, output_path):
        # print('  - [Upload] Uploading: ')
        try:
            self._connect()
            self._update_remote_dir(competitionid)
            self._update_zip_file_name(userid, submit_time)

            self._zip_dir(output_path, os.path.join(self.zip_file_dir, self.zip_file_name))
            self._upload_score()

            self._delete_file(os.path.join(self.zip_file_dir, self.zip_file_name))
            # print('  - [Upload] Done!')
            shutil.rmtree(output_path)
            return 'https://resource.onsite.run' + self.remote_dir + self.zip_file_name
        except Exception as e:
            logger.exception(f"[UPLOAD ERROR]:{repr(e)}", extra={'submitId': self.submitId})
            return None
    
    def _update_remote_dir(self, dirname):
        self.remote_dir += rf"{dirname}/"

    def _update_zip_file_name(self, userid, submit_time):
        self.zip_file_name = f"{userid}&{submit_time}.zip"
        self.zip_file_name = self.zip_file_name.replace(":", "-")
        self.zip_file_name = self.zip_file_name.replace(" ", "_")

    def _zip_dir(self, output_path, zip_file):
        # print(f"    --> zipping: {output_path} -zip-> {zip_file}")
        zip = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED)
        for path, dirnames, filenames in os.walk(output_path):
            fpath = path.replace(output_path, '')
            for filename in filenames:
                zip.write(os.path.join(path, filename), os.path.join(fpath, filename))
        zip.close()

    def _upload_score(self):
        # print(f"    --> to_upyun: {self.remote_dir + self.zip_file_name}")
        with open(os.path.join(self.zip_file_dir, self.zip_file_name), 'rb') as f:
            self.up.put(self.remote_dir + self.zip_file_name, f, checksum=True)
    
    def _delete_file(self, file_name):
        # print(f"    --> delete_temp: {self.zip_file_dir, self.zip_file_name}")
        os.remove(file_name)


if __name__ == "__main__":
    output_path = r"/media/yangyh408/YangYH408/test_scenario/outputs"
    uploader = Uploader(output_path)
    competitionid = "test_exam_1"
    userid = "yangyh408"
    submit_time = "2023-03-04 22:24:26"
    uploader.upload(competitionid, userid, submit_time)
    # uploader._zip_res(output_path, r"C:\Users\89525\Desktop\test_zip.zip")
    # uploader._upload_score(r"C:\Users\89525\Desktop\test_zip.zip")