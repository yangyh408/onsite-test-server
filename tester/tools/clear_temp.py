import os

BASE_DIR = r"/home/ubuntu/onsite-test-server/temp"

for i in os.listdir(BASE_DIR):
    if i[0] == 's':
        dir_path = os.path.join(BASE_DIR, i)
        os.system(f"sudo rm -rf {dir_path}")