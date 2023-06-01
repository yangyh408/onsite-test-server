import sys
sys.path.append('..')
from connector import Connector
import pandas as pd

database = Connector()

# Export all users
users = database._get_value(table='user', field='userName, mobile, email, school, supervisorName', logic='AND')
user_df = pd.DataFrame(users, columns=['姓名', '手机号', '邮箱', '学校', '指导老师'])
user_df.to_csv('users.csv', index=False, encoding='gbk')