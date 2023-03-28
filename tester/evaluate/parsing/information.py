# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/10 21:18
from pandas import DataFrame
import numpy as np


class Info:
    """
    用于储存三个文件解析后的信息，分别为.csv、openDrive和openScenario
    .csv的信息分两部分储存：trajectory_info和replay_info
    openDrive信息储存在openDrive_info
    openScenario信息储存在openScenario_info
    本类的数据格式如下：
    trajectory_info:{"ego"：{"x":[],
                            "y":[],
                            "v":[],
                            "yaw":[],
                            "width":float,
                            "length":float
                            }
                    "vehicle_1":{},
                    "vehicle_2":{},
                    "vehicle_3":{},
                    ...
                    }
    replay_info:{"scenario_name":str,
                 "evaluation_type":str,
                 "scenario_source":str,
                 "t":[],
                 "dt":float,
                 "end_state":int,
                 "travel_direction": tuple('W','S'),
                 "stop_line": {}
                }  为了不破坏openDrive_info类中的结构，停止线信息，被存放在replay_info中
    light_info:[]
    openDrive_info:{}  后面看懂了可以详细写一下 TODO
    zone = {}
    openScenario_info:{"initial_x":float,
                       "initial_y":float,
                       "goal_x":list,
                       "goal_y":list
                        }
    """

    def __init__(self):
        self.trajectory_info = {
            "ego": {"x": [],
                    "y": [],
                    "v": [],
                    "yaw": [],
                    "width": 4.924,
                    "length": 1.872
                    }
        }
        self.replay_info = {
            "scenario_name": None,
            "evaluation_type": None,
            "scenario_source": None,
            "t": [],
            "dt": -1,
            "end_state": -1,
            "travel_direction": [],
            "target_travel_direction": (),
            "stop_line": {}}
        self.light_info = []
        self.openDrive_info = {}
        self.zone = {}
        self.openScenario_info = {
            "initial_x": None,
            "initial_y": None,
            "goal_x": [],
            "goal_y": []}
        self.map_dataformat = {
            "WI": {},
            "WO": {},
            "EI": {},
            "EO": {},
            "NI": {},
            "NO": {},
            "SI": {},
            "SO": {},
            "IN": {}
        }

    def add_trajectory(self, frame: DataFrame) -> None:
        vehicle_id = lambda x: x[-1:-(len(x) - x.rfind('_')): -1][::-1]  # 求出_后面的车辆id
        if vehicle_id(list(frame.columns)[0]) == "ego":
            vehicle = 'ego'
        else:
            vehicle = 'vehicle_' + vehicle_id(list(frame.columns)[0])
            self.trajectory_info[vehicle] = {}
        for key, value in zip(['x', 'y', 'v', 'a', 'yaw'], np.array(frame)[:, 0:5].T):
            if value is not None:
                self.trajectory_info[vehicle][key] = value
        for key, value in zip(['width', 'length'], [np.array(frame)[0, 5], np.array(frame)[0, 6]]):
            if value is not None:
                self.trajectory_info[vehicle][key] = value
        return

    def add_settings(self, scenario_name: str = None, evaluation_type: str = None, scenario_source: str = None,
                     t: list = None, dt: float = None, end_state: float = None) -> None:
        for key, value in zip(['scenario_name', 'evaluation_type', 'scenario_source', 't', 'dt', 'end_state'],
                              [scenario_name, evaluation_type, scenario_source, t, dt, end_state]):
            if value is not None:
                self.replay_info[key] = value
        return
