# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/11 15:20
import json
import os
import re
import xml.dom.minidom

import numpy as np
import pandas as pd
import shapely.geometry
from lxml import etree
from shapely.geometry import MultiPolygon

import parsing.test
import parsing.utils
from parsing.information import Info
from opendrive2discretenet.network import Network
from opendrive2discretenet.opendriveparser.parser import parse_opendrive
import matplotlib.pyplot as plt
import alphashape
from descartes import PolygonPatch
import warnings
from opendrive2discretenet.utils import encode_road_section_lane_width_id
warnings.filterwarnings("ignore")
from shapely.geometry import Polygon


class Parser:
    """
    该类用来解析所有文件，这里一共解析了三个文件，分别是trajectory_csv、openDrive和openScenario三个文件，
    最后返回一个储存好所有信息的Info类，直接调用该信息，即可用于评价。
    至此，信息解析部分完成，进入评价模块。
    """

    def __init__(self):
        self.root = None
        self.open_drive_xml = None
        self.loadedRoadNetwork = None
        self.info = Info()

    def parse_openScenario(self, scenario_path: str) -> None:
        """
        解析openScenario地图信息，存储到self.info.openScenario_info
        :param scenario_path: 存放比赛试题的文件位置
        :return:
        """
        scenario_file = os.path.join(scenario_path, str(self.info.replay_info['scenario_name']))
        path_openScenario = None
        try:
            for file in os.listdir(scenario_file):
                if file[0] != '.' and file[-5:] == '.xosc':
                    path_openScenario = os.path.join(scenario_file, file)
            assert path_openScenario is not None
        except FileNotFoundError:
            raise FileNotFoundError("未找到对应的openScenario地图文件，请检查路径是否正确")
        opens = xml.dom.minidom.parse(path_openScenario).documentElement

        # 读取主车起点信息
        ego_node = opens.getElementsByTagName('Private')[0]
        ego_init = ego_node.childNodes[3].data
        ego_v, ego_x, ego_y, ego_head = [
            float(i.split('=')[1]) for i in ego_init.split(',')]
        for key, value in zip(["initial_x", "initial_y"], [ego_x, ego_y]):
            self.info.openScenario_info[key] = value

        # 获取行驶目标, goal
        goal_init = ego_node.childNodes[5].data
        goal = [float(i) for i in re.findall('-*\d+\.\d+', goal_init)]
        for key, value in zip(["goal_x", "goal_y"], [goal[:2], goal[2:]]):
            self.info.openScenario_info[key] = value
        return

    def parse_openDrive(self, scenario_path: str) -> None:
        """
        解析openDrive路网的信息，存储到self.info.openDrive_info。
        Parameters
        :param scenario_path: 存放比赛试题的文件位置
        """
        # 解析该场景地图文件
        scenario_file = os.path.join(scenario_path, str(self.info.replay_info['scenario_name']))
        path_openDrive = None
        try:
            for file in os.listdir(scenario_file):
                #print(file)
                if file[0] != '.' and file[-5:] == '.xodr':
                    path_openDrive = os.path.join(scenario_file, file)
            assert path_openDrive is not None
        except FileNotFoundError:
            raise FileNotFoundError("未找到对应的openDrive地图文件，请检查路径是否正确")
        fh = open(path_openDrive, "r")
        # 返回解析之后的对象
        self.root = etree.ElementTree(file=path_openDrive).getroot()
        self.open_drive_xml = parse_opendrive(etree.parse(fh).getroot())
        fh.close()

        # 将OpenDrive类对象进一步解析为参数化的Network类对象，以备后续转化为DiscreteNetwork路网并可视化
        self.loadedRoadNetwork = Network()
        self.loadedRoadNetwork.load_opendrive(self.open_drive_xml)

        '''将解析完成的Network类对象转换为DiscreteNetwork路网，其中使用的只有路网中各车道两侧边界的散点坐标
        车道边界点通过线性插值的方式得到，坐标点储存在<DiscreteNetwork.discretelanes.left_vertices/right_vertices> -> List
        '''
        open_drive_info = self.loadedRoadNetwork.export_discrete_network(
            filter_types=["driving", "onRamp", "offRamp", "exit", "entry"])  # -> <class> DiscreteNetwork
        self.info.openDrive_info = open_drive_info
        return

    def parse_trajectory_csv(self, csv_file_path: str) -> None:
        """
        读取csv文件，提取文件名，找到对应的openDrive和openScenario的位置
        :return:
        """
        trajectory_frame = pd.read_csv(csv_file_path)
        trajectory_frame.rename(columns={"Unnamed: 0": "t"}, inplace=True)

        # 准备add_settings需要的信息
        scenario_name = os.path.basename(csv_file_path)[:-11]
        t = list(np.array(trajectory_frame['t']))
        dt = trajectory_frame.loc[1, 't'] - trajectory_frame.loc[0, 't']
        end_state = trajectory_frame.loc[trajectory_frame.shape[0] - 1, 'end']
        self.info.add_settings(scenario_name, None, None, t, dt, end_state)

        # 准备add_trajectory需要的信息
        for col in range(1, len(list(trajectory_frame.columns)) - 1, 7):
            self.info.add_trajectory(trajectory_frame[list(trajectory_frame.columns)[col:col + 7]])

        return

    def parse_JSON(self, scenario_path: str) -> None:
        scenario_file = os.path.join(scenario_path, str(self.info.replay_info['scenario_name']))
        path_json = None
        try:
            for file in os.listdir(scenario_file):
                if file[0] != '.' and file[-5:] == '.json':
                    path_json = os.path.join(scenario_file, file)
            assert path_json is not None
        except FileNotFoundError:
            raise FileNotFoundError("未找到对应的JSON文件，请检查路径是否正确，如路径正确则该场景未提供信控文件")
        with open(path_json, 'r') as read_f:
            light_info = json.load(read_f)
        time = []
        for key in list(light_info.keys()):
            time.append(key)
        time = list(map(float, time))
        time.sort()
        for t in time:
            self.info.light_info.append(light_info[str(t)])
        # print(self.info.light_info)
        return

    # 判断车辆目标形式方向
    def judge_target_direction(self):
        start_x = self.info.openScenario_info['initial_x']
        start_y = self.info.openScenario_info['initial_y']

        end_x = self.info.openScenario_info['goal_x'][-1]
        end_y = self.info.openScenario_info['goal_y'][-1]
        # print(start_x,start_y)
        # print(self.info.replay_info['stop_line']['W'][3])
        if start_x <= self.info.replay_info['stop_line']['W'][3]:
            #print("W")
            if end_y >= self.info.replay_info['stop_line']['N'][3]:
                self.info.replay_info['target_travel_direction'] = ('W', 'N')
            elif end_y <= self.info.replay_info['stop_line']['S'][3]:
                self.info.replay_info['target_travel_direction'] = ('W', 'S')
            elif end_x >= self.info.replay_info['stop_line']['E'][3]:
                self.info.replay_info['target_travel_direction'] = ('W', 'E')
            elif end_x <= self.info.replay_info['stop_line']['W'][3]:
                self.info.replay_info['target_travel_direction'] = ('W', 'W')
        elif start_x >= self.info.replay_info['stop_line']['E'][3]:
            if end_y >= self.info.replay_info['stop_line']['N'][3]:
                self.info.replay_info['target_travel_direction'] = ('E', 'N')
            elif end_y <= self.info.replay_info['stop_line']['S'][3]:
                self.info.replay_info['target_travel_direction'] = ('E', 'S')
            elif end_x <= self.info.replay_info['stop_line']['W'][3]:
                self.info.replay_info['target_travel_direction'] = ('E', 'W')
            elif end_x >= self.info.replay_info['stop_line']['E'][3]:
                self.info.replay_info['target_travel_direction'] = ('E', 'E')
        elif start_y <= self.info.replay_info['stop_line']['S'][3]:
            if end_x >= self.info.replay_info['stop_line']['E'][3]:
                self.info.replay_info['target_travel_direction'] = ('S', 'E')
            elif end_x <= self.info.replay_info['stop_line']['W'][3]:
                self.info.replay_info['target_travel_direction'] = ('S', 'W')
            elif end_y >= self.info.replay_info['stop_line']['N'][3]:
                self.info.replay_info['target_travel_direction'] = ('S', 'N')
            elif end_y <= self.info.replay_info['stop_line']['S'][3]:
                self.info.replay_info['target_travel_direction'] = ('S', 'S')
        elif start_y >= self.info.replay_info['stop_line']['N'][3]:
            if end_x >= self.info.replay_info['stop_line']['E'][3]:
                self.info.replay_info['target_travel_direction'] = ('N', 'E')
            elif end_x <= self.info.replay_info['stop_line']['W'][3]:
                self.info.replay_info['target_travel_direction'] = ('N', 'W')
            elif end_y <= self.info.replay_info['stop_line']['S'][3]:
                self.info.replay_info['target_travel_direction'] = ('N', 'S')
            elif end_y >= self.info.replay_info['stop_line']['N'][3]:
                self.info.replay_info['target_travel_direction'] = ('N', 'N')
        pass

    # 判断车辆行驶方向
    def judge_travel_direction(self):
        start_x = self.info.trajectory_info['ego']['x'][0]
        start_y = self.info.trajectory_info['ego']['y'][0]
        start_point = shapely.geometry.Point(start_x, start_y)

        end_x = self.info.trajectory_info['ego']['x'][-1]
        end_y = self.info.trajectory_info['ego']['y'][-1]
        end_point = shapely.geometry.Point(end_x, end_y)
        #print(start_x,start_y,end_x,end_y)
        # print(start_point.coords.xy)
        for key in self.info.zone.keys():
            if self.info.zone[key].intersects(start_point):
                #print(self.info.zone[key])
                # print('------------------------------')
                if key[-1] == 'I':
                    self.info.replay_info['travel_direction'].append(key[0])

        if len(self.info.replay_info['travel_direction']) != 1:
            raise ValueError('场景{0}存在问题'.format(self.info.replay_info["scenario_name"]))
        for key in self.info.zone.keys():
            if self.info.zone[key].buffer(0.001).intersects(end_point):
                if key[-1] == 'O':
                    self.info.replay_info['travel_direction'].append(key[0])
                elif key == 'IN':
                    self.info.replay_info['travel_direction'].append(key)
                elif key[-1] == 'I':
                    self.info.replay_info['travel_direction'].append(key[0])

        if len(self.info.replay_info['travel_direction']) == 1:
            end_x1 = self.info.trajectory_info['ego']['x'][-10]
            end_y1 = self.info.trajectory_info['ego']['y'][-10]
            end_point1 = shapely.geometry.Point(end_x1, end_y1)
            for key in self.info.zone.keys():
                if self.info.zone[key].buffer(0.001).intersects(end_point1):
                    if key[-1] == 'O':
                        self.info.replay_info['travel_direction'].append(key[0])
                    elif key == 'IN':
                        self.info.replay_info['travel_direction'].append(key)
                    elif key[-1] == 'I':
                        self.info.replay_info['travel_direction'].append(key[0])
        if len(self.info.replay_info['travel_direction']) == 1:
            self.info.replay_info['travel_direction'].append(
                self.info.replay_info['target_travel_direction'][1])
            # 这里是说，如果最后一个点时，规控器失效的话，轨迹点可能不在任何一个区域中，而在其他地方，这时另行驶方向与目标行驶方向一致
        if len(self.info.replay_info['travel_direction']) != 2:
            if 'IN' in self.info.replay_info['travel_direction']:
                self.info.replay_info['travel_direction'].remove('IN')
            self.info.replay_info['travel_direction'] = self.info.replay_info['travel_direction'][:2]
        if len(self.info.replay_info['travel_direction']) != 2:
            raise ValueError('场景{0}存在问题'.format(self.info.replay_info["scenario_name"]))

        #print(self.info.replay_info['target_travel_direction'])
        return

    def judge_stop_line(self) -> None:
        roads = self.root.findall('road')
        entrance_roads_id = parsing.utils.find_entrance_road(roads)
        # 两种确定停止线的方法，首先确定使用哪种方法
        # 方法一的应用场景为opendrive中包含停止线信息
        # 方法二的应用场景为opendrive中不包含停止线信息
        method = None
        for road in roads:
            if road.attrib['id'] in entrance_roads_id:
                objects = road.find("objects")
                if not objects:
                    method = 'method_two'
                else:
                    method = 'method_one'
                break
        if method == 'method_one':
            stop_line_list = self.judge_stop_line_method_one(roads, entrance_roads_id)
        elif method == 'method_two':
            stop_line_list = self.judge_stop_line_method_two(roads, entrance_roads_id)
        """
        TODO 找到每个进口道的stopline，然后将其转换为（x,y）,同时存一下宽度
        stop_line = {'W':[tuple,tuple,float,average],'E':[]...} 每个方向上存的分别是停止线起点和终点的(x,y)坐标以及停止线长度
        """
        # [[(x1,y), (x2,y2), width],[],[],[]]
        ravel_list = [coor for direction in stop_line_list for coor in direction]
        filter_list = [coor for coor in ravel_list if type(coor) is tuple]
        x, y = zip(*filter_list)
        self.info.replay_info['stop_line']['E'] = stop_line_list[x.index(max(x)) // 2]
        self.info.replay_info['stop_line']['W'] = stop_line_list[x.index(min(x)) // 2]
        self.info.replay_info['stop_line']['N'] = stop_line_list[y.index(max(y)) // 2]
        self.info.replay_info['stop_line']['S'] = stop_line_list[y.index(min(y)) // 2]
        self.info.replay_info['stop_line']['E'].append(
            (self.info.replay_info['stop_line']['E'][0][0] + self.info.replay_info['stop_line']['E'][1][0]) / 2)
        self.info.replay_info['stop_line']['W'].append(
            (self.info.replay_info['stop_line']['W'][0][0] + self.info.replay_info['stop_line']['W'][1][0]) / 2)
        self.info.replay_info['stop_line']['N'].append(
            (self.info.replay_info['stop_line']['N'][0][1] + self.info.replay_info['stop_line']['N'][1][1]) / 2)
        self.info.replay_info['stop_line']['S'].append(
            (self.info.replay_info['stop_line']['S'][0][1] + self.info.replay_info['stop_line']['S'][1][1]) / 2)
        # print(self.info.replay_info['stop_line'])
        return

    def judge_stop_line_method_one(self, roads, entrance_roads_id: list) -> list:
        stop_line_list = []
        for road in roads:
            if road.attrib['id'] in entrance_roads_id:
                xml_road = self.open_drive_xml.getRoad(float(road.attrib['id']))
                end_s = xml_road.planView.length
                coordinate_one, angle_one = xml_road.planView.calc_geometry(end_s)
                objects = road.find('objects').findall('object')
                for object_ in objects:
                    if object_.attrib['name'] == "stopLocation":
                        width = float(object_.attrib['length'])
                        ortho = angle_one - np.pi / 2
                        coordinate_two = np.array(coordinate_one) + np.array(
                            [width * np.cos(ortho), width * np.sin(ortho)]
                        )
                stop_line_list.append([tuple(coordinate_one), tuple(coordinate_two), width])
        return stop_line_list

    def judge_stop_line_method_two(self, roads, entrance_roads_id: list) -> list:
        stop_line_list = []
        for road in roads:
            if road.attrib['id'] in entrance_roads_id:
                xml_road = self.open_drive_xml.getRoad(float(road.attrib['id']))
                end_s = xml_road.planView.length
                coordinate_one, angle_one = xml_road.planView.calc_geometry(end_s)
                s_section = float(road.find('lanes').findall('laneSection')[-1].attrib['s'])
                right = road.find('lanes').findall('laneSection')[-1].find('right')
                lanes = right.findall('lane')
                total_width = 0
                for lane in lanes:
                    width = lane.find('width')
                    roadMark = lane.find('roadMark')
                    lane_width = parsing.utils.calc_width(width, roadMark, end_s - s_section)
                    total_width += lane_width
                total_width = float(total_width)
                ortho = angle_one - np.pi / 2
                coordinate_two = np.array(coordinate_one) + np.array(
                    [total_width * np.cos(ortho), total_width * np.sin(ortho)]
                )
                stop_line_list.append([tuple(coordinate_one), tuple(coordinate_two), total_width])
        return stop_line_list

    def judge_evaluation_system(self, scenario_path: str) -> None:
        # 优先读取场景来源，目前只有highway和NDS两种来源（且NDS的来源为空），后续增加新场景库后，再补充
        scenario_source = self.open_drive_xml.header.name
        # 根据场景来源分析场景类型（场景类型主要用于判断使用哪种评价体系）
        if scenario_source in ['highD', 'highway']:
            self.info.replay_info['scenario_source'] = scenario_source
            #print('{0}场景来源于highway数据集，使用高速公路评价体系'.format(self.info.replay_info['scenario_name']))
            self.info.replay_info['evaluation_type'] = 'scheme_one'
            pass
        elif scenario_source == "":
            self.info.replay_info['scenario_source'] = "NDS"
            if not self.open_drive_xml.junctions:
                #print('{0}场景来源于NDS数据集，其中不存在交叉口场景，使用高速公路评价体系'.format(self.info.replay_info['scenario_name']))
                self.info.replay_info['evaluation_type'] = 'scheme_one'
                pass
            else:
                """
                场景中存在交叉口，因此可以读取目标行驶方向，依据目标行驶方向判断，使用哪个评价体系
                """
                self.judge_stop_line()
                self.judge_target_direction()
                if self.info.replay_info['target_travel_direction'].count(
                        self.info.replay_info['target_travel_direction'][0]) == len(
                    self.info.replay_info['target_travel_direction']):
                    #print('{0}场景来源于NDS数据集，存在交叉口，车辆的目标行驶轨迹并未通过交叉口，使用高速公路评价体系'.format(self.info.replay_info['scenario_name']))
                    self.info.replay_info['evaluation_type'] = "scheme_one"
                else:
                    #print("{0}场景来源于NDS数据集，存在交叉口，车辆的目标行驶轨迹通过交叉口，使用交叉口评价体系".format(self.info.replay_info['scenario_name']))
                    self.info.replay_info['evaluation_type'] = "scheme_two"
                    self.parse_JSON(scenario_path)
                    self.get_each_zone_polygon()
                    self.judge_travel_direction()
        elif scenario_source == "SinD":
            self.info.replay_info['scenario_source'] = "SinD"
            if not self.open_drive_xml.junctions:
                #print('{0}场景来源于SinD数据集，其中不存在交叉口场景，使用高速公路评价体系'.format(
                    # self.info.replay_info['scenario_name']))
                self.info.replay_info['evaluation_type'] = 'scheme_one'
                pass
            else:
                """
                场景中存在交叉口，因此可以读取目标行驶方向，依据目标行驶方向判断，使用哪个评价体系
                """
                self.judge_stop_line()
                self.judge_target_direction()
                if self.info.replay_info['target_travel_direction'].count(
                        self.info.replay_info['target_travel_direction'][0]) == len(
                    self.info.replay_info['target_travel_direction']):
                    #print(
                        # '{0}场景来源于SinD数据集，存在交叉口，车辆的目标行驶轨迹并未通过交叉口，使用高速公路评价体系'.format(
                        #     self.info.replay_info['scenario_name']))
                    self.info.replay_info['evaluation_type'] = "scheme_one"
                else:
                    #print("{0}场景来源于SinD数据集，存在交叉口，车辆的目标行驶轨迹通过交叉口，使用交叉口评价体系".format(
                        # self.info.replay_info['scenario_name']))
                    self.info.replay_info['evaluation_type'] = "scheme_two"
                    self.parse_JSON(scenario_path)
                    self.get_each_zone_polygon()
                    self.judge_travel_direction()
            pass
        elif scenario_source == "NDS_ramp":
            self.info.replay_info['scenario_source'] = "NDS_ramp"
            #print('{0}场景来源于NDS数据集，使用汇入汇出体系'.format(self.info.replay_info['scenario_name']))
            self.info.replay_info['evaluation_type'] = 'scheme_three'
            pass
        else:
            self.info.replay_info['scenario_source'] = scenario_source
            #print("{0}场景来源于{1}数据集，使用其他评价体系".format(self.info.replay_info['scenario_name'], scenario_source))
            self.info.replay_info['evaluation_type'] = "scheme_four"
            pass
        return

    def parse(self, trajectory_path: str, scenario_path: str) -> Info:
        """
        完成对三个文件的解析，分别为.csv、openDrive和openScenario文件，将信息存在self.info中
        noted:所有场景都需要读取的为csv，openDrive和openScenario
        随后通过，scenario_source来判断场景来源以及是否存在交叉口，
        若有交叉口，可以读取JSON文件，同时读取停止线和目标行驶方向
        最后通过驾驶目标选择评价体系
        :param trajectory_path: 轨迹文件位置
        :param scenario_path: 场景文件位置
        :return:
        """
        self.parse_trajectory_csv(trajectory_path)
        self.parse_openDrive(scenario_path)
        self.parse_openScenario(scenario_path)
        self.judge_evaluation_system(scenario_path)

        return self.info

    """------以下均是一些工具函数，不影响理解解析的整体思路，不想看可以不看"""
    def get_each_zone_road_id(self):
        outside_intersection_road = []
        inside_intersection_road = []
        entrance_road = []
        exit_road = []
        for road in self.open_drive_xml.roads:
            if road.junction is None:
                outside_intersection_road.append(road)
                if road.link.predecessor is None:
                    entrance_road.append(road)
                if road.link.successor is None:
                    exit_road.append(road)
            else:
                inside_intersection_road.append(road)
        in_, out_ = parsing.test.zoning_first_id(entrance_road, exit_road)
        in_, out_ = parsing.test.zoning_other_id(in_, out_, outside_intersection_road)
        self.create_dict_of_lane_id_and_discretelane(in_road=in_, out_road=out_, inside_intersection_road=inside_intersection_road)
        '把每部分的lane_id取出'
        [WI, EI, NI, SI] = [[] for i in range(4)]
        [WO, EO, NO, SO] = [[] for i in range(4)]
        in_id = [WI, EI, NI, SI]
        out_id = [WO, EO, NO, SO]
        for i in in_:
            for j in i:
                in_id[in_.index(i)].append(j.id)
        for i in out_:
            for j in i:
                out_id[out_.index(i)].append(j.id)
        # (in_id)
        # print(out_id)
        return in_id, out_id, inside_intersection_road

    def get_each_zone_polygon(self) -> None:
        in_id, out_id, inside_intersection_road = self.get_each_zone_road_id()
        IN = ['WI', 'EI', 'NI', 'SI']
        OUT = ['WO', 'EO', 'NO', 'SO']
        for zone_id, zone in zip(IN, in_id):
            self.info.zone[zone_id] = self.get_single_zone_bord(zone)
        for zone_id, zone in zip(OUT, out_id):
            self.info.zone[zone_id] = self.get_single_zone_bord(zone)
        self.info.zone['IN'] = self.intersection_zone_version3()
        return

    def intersection_zone_version3(self):
        poly_shape_list = []
        for key in self.info.map_dataformat["IN"].keys():
            bord_point_array = np.array([]).reshape(-1, 2)
            bord_point_array = np.vstack((bord_point_array, self.info.map_dataformat["IN"][key].left_vertices))
            bord_point_array = np.vstack((bord_point_array, self.info.map_dataformat["IN"][key].right_vertices[::-1]))
            bord_point_array.reshape(-1, 2)
            try:
                poly_shape = alphashape.alphashape(bord_point_array, 0.001)
            except ValueError:
                poly_shape = alphashape.alphashape(bord_point_array, 0.0001)
            if isinstance(poly_shape, MultiPolygon):
                for poly_index in range(len(poly_shape.geoms)):
                    poly_shape_list.append(poly_shape.geoms[poly_index])
            else:
                poly_shape_list.append(poly_shape)
        multipolygon = MultiPolygon(poly_shape_list)
        return multipolygon

    def intersection_zone_version2(self, inside_intersection_road):
        poly_shape_list = []
        for discrete_lane in self.info.openDrive_info.discretelanes:
            bord_point_array = np.array([]).reshape(-1, 2)
            if float(discrete_lane.lane_id.split('.')[0]) in [road.id for road in inside_intersection_road]:
                bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices))
                bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices[::-1]))
                bord_point_array.reshape(-1, 2)
                try:
                    poly_shape = alphashape.alphashape(bord_point_array, 0.001)
                except ValueError:
                    poly_shape = alphashape.alphashape(bord_point_array, 0.0001)
                poly_shape_list.append(poly_shape)
        multipolygon = MultiPolygon(poly_shape_list)
        return multipolygon

    def intersection_zone(self, inside_intersection_road):
        bord_point_array = np.array([]).reshape(-1, 2)
        for discrete_lane in self.info.openDrive_info.discretelanes:
            if float(discrete_lane.lane_id.split('.')[0]) in [road.id for road in inside_intersection_road]:
                bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices))
                bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices))
        bord_point_array.reshape(-1, 2)
        try:
            poly_shape = alphashape.alphashape(bord_point_array, 0.01)
        except ValueError:
            poly_shape = alphashape.alphashape(bord_point_array, 0.0001)
        # edges = parsing.utils.alpha_shape(bord_point_array, alpha=200, only_outer=True)
        # edges_ = np.array(list(edges)).ravel()
        # polygon_points = [list(bord_point_array[idx]) for idx in edges_]
        # poly_shape = shapely.geometry.Polygon(polygon_points)
        return poly_shape

    def get_single_zone_bord(self, zone):
        bord_list = []
        bord_point_array = np.array([]).reshape(-1, 2)
        for road_id in zone:
            for lane_section in self.open_drive_xml.getRoad(road_id).lanes.lane_sections:
                lane_id_list = []
                for lane in lane_section.allLanes:
                    lane_id_list.append(lane)
                lane_id_list.sort(key=lambda x: x.id)
                # print(len(lane_id_list))
                bord_list.append('.'.join((str(road_id), str(lane_section.idx), str(lane_id_list[0].id), str(-1))))
                bord_list.append('.'.join((str(road_id), str(lane_section.idx), str(lane_id_list[-2].id), str(-1))))
        '''
        for discrete_lane in self.info.openDrive_info.discretelanes:
            if discrete_lane.lane_id in bord_list:
                bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices))
                bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices))
        bord_point_array.reshape(-1,2)
        '''
        for even in range(0, len(bord_list), 2):
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if discrete_lane.lane_id == bord_list[even]:
                    bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices))
        for odd in range(1, len(bord_list), 2):
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if discrete_lane.lane_id == bord_list[odd]:
                    bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices[::-1]))
        bord_point_array.reshape(-1, 2)
        '''
        for discrete_lane in self.info.openDrive_info.discretelanes:
            if discrete_lane.lane_id in bord_list:
                if bord_list.count(bord_list[0]) == len(bord_list):
                    if discrete_lane.lane_id == bord_list[0]:
                        bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices))
                        bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices[::-1]))
                else:
                    if discrete_lane.lane_id == bord_list[0]:
                        bord_point_array = np.vstack((bord_point_array, discrete_lane.right_vertices))
                    elif discrete_lane.lane_id == bord_list[1]:
                        bord_point_array = np.vstack((bord_point_array, discrete_lane.left_vertices[::-1]))
        bord_point_array.reshape(-1, 2)
        '''
        # print(bord_point_array)
        try:
            # print(bord_point_array.shape)
            # print(bord_point_array)
            poly_shape = alphashape.alphashape(bord_point_array, 0.0)
        except ValueError:
            poly_shape = alphashape.alphashape(bord_point_array, 0.0001)
            # print('------------------------------------------------------------------------------------')
        # edges = parsing.utils.alpha_shape(bord_point_array, alpha=200, only_outer=True)
        # edges_ = np.array(list(edges)).ravel()
        # polygon_points = [list(bord_point_array[idx]) for idx in edges_]
        # poly_shape = shapely.geometry.Polygon(polygon_points)
        return poly_shape

    def create_dict_of_lane_id_and_discretelane(self, in_road: list, out_road: list, inside_intersection_road:list) -> None:
        """
        data_format = {
                        'WI': {'lane_id_1':discretelane_1, 'lane_id_2':discretelane_2, 'lane_id_3':discretelane_3}
                        'WO': {'lane_id_4':discretelane_4, 'lane_id_5':discretelane_5, 'lane_id_6':discretelane_6}
                    }
        """
        in_road_order = ['WI', 'EI', 'NI', 'SI']
        out_road_order = ['WO', 'EO', 'NO', 'SO']
        # 进口道
        for direction in in_road:
            for single_road in direction:
                for lane_section in single_road.lanes.lane_sections:
                    for lane_id in lane_section.allLanes:
                        try:
                            encoding_lane_id = encode_road_section_lane_width_id(roadId=single_road.id, sectionId=lane_section.idx, laneId=lane_id.id, widthId=-1)
                            self.info.map_dataformat[in_road_order[in_road.index(direction)]][encoding_lane_id] = [discrete_lane for discrete_lane in self.info.openDrive_info.discretelanes if discrete_lane.lane_id == str(encoding_lane_id)][0]
                        except IndexError:
                            pass
        # 出口道
        for direction in out_road:
            for single_road in direction:
                for lane_section in single_road.lanes.lane_sections:
                    for lane_id in lane_section.allLanes:
                        try:
                            encoding_lane_id = encode_road_section_lane_width_id(roadId=single_road.id, sectionId=lane_section.idx, laneId=lane_id.id, widthId=-1)
                            self.info.map_dataformat[out_road_order[out_road.index(direction)]][encoding_lane_id] = [discrete_lane for discrete_lane in self.info.openDrive_info.discretelanes if discrete_lane.lane_id == str(encoding_lane_id)][0]
                        except IndexError:
                            pass
        # 交叉口内部
        for single_road in inside_intersection_road:
            for lane_section in single_road.lanes.lane_sections:
                for lane_id in lane_section.allLanes:
                    try:
                        encoding_lane_id = encode_road_section_lane_width_id(roadId=single_road.id, sectionId=lane_section.idx, laneId=lane_id.id, widthId=-1)
                        self.info.map_dataformat['IN'][encoding_lane_id] = [discrete_lane for discrete_lane in self.info.openDrive_info.discretelanes if discrete_lane.lane_id == str(encoding_lane_id)][0]
                    except IndexError:
                        pass
        pass


if __name__ == "__main__":
    from pathlib import Path
    Scenario_path = r"E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\scenario_new"
    Trajectory_path = r"E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\trajectory\1rush19_exam.csv"
    parser = Parser()
    parser.parse(Trajectory_path, Scenario_path)
    # print(parser.info.zone)
    fig, ax = plt.subplots()
    for index, item in enumerate(['WI', 'EI', 'NI', 'SI', 'WO', 'EO', 'NO', 'SO', 'IN']):
        ax.add_patch(PolygonPatch(parser.info.zone[item], alpha=0.3))
    plt.scatter(parser.info.openScenario_info['goal_x'][-1], parser.info.openScenario_info['goal_y'][-1], c='r')
    ax.set(xlim=(-50, 450),
           ylim=(-50, 75)
           )
    # plt.show()
    Trajectory_path_path = Path(Trajectory_path)
    plt.savefig('E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\map_fig\{0}.png'.format(Trajectory_path_path.name),dpi=600)
    point = shapely.geometry.Point(parser.info.openScenario_info['goal_x'][-1], parser.info.openScenario_info['goal_y'][-1])
    for i in ['WI', 'EI', 'NI', 'SI', 'WO', 'EO', 'NO', 'SO', 'IN']:
        print(parser.info.zone[i].intersects(point))
    print(parser.info.replay_info['travel_direction'])
    print(parser.info.replay_info['target_travel_direction'])
    print(parser.info.map_dataformat)
    import sys
    sys.path.append('../..')
    from onsite_intersection_evaluation_version_2.utils import segment_of_trajectory
    front_segment, middle_segment, latter_segment, sut_lose_efficacy = segment_of_trajectory(parser.info.trajectory_info['ego']['x'], parser.info.trajectory_info['ego']['y'],
            parser.info.replay_info['travel_direction'], parser.info.zone)
    print("--------first_segment------------")
    print(front_segment)
    print(front_segment.shape)
    print("--------second_segment-----------------")
    print(middle_segment)
    print(middle_segment.shape)
    print("------------third_segment--------------")
    print(latter_segment)
    print(latter_segment.shape)
    """
    如果目标行驶方向与实际行驶方向一致，则没问题正常评价
    如果目标行驶方向与实际行驶方向不一致：
    （1）终点在地图中，规控器走错方向，该种情况下不可能完成任务，因此效率得分归0，分段按目标方向分
    （2）终点不在地图中，在实际行驶方向判断中，会将终点方向给一个值，正常评价就好
    （3）终点在交叉口内，则只有两段轨迹（也可能只有一段轨迹）

    entrance_id = []
    exit_id = []
    for discrete_lane in parser.info.openDrive_info.discretelanes:
        print(discrete_lane.lane_id)
        print(discrete_lane.predecessor)
        print(discrete_lane.successor)
        print(discrete_lane.center_vertices)
        if not discrete_lane.predecessor:
            entrance_id.append(discrete_lane.lane_id)
        if not discrete_lane.successor:
            exit_id.append(discrete_lane.lane_id)
    print(entrance_id)
    print(exit_id)
    """



