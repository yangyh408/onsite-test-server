# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/29 21:52
import numpy as np
import pandas as pd
import operator
from parsing.parser import Parser
from util import segment_of_trajectory
from numpy import ndarray
from evaluation_prepare.utils import lane_type_in_map, trajectory_type_in_map


class EgoForwardVehicleInfo:
    """
    存放主车和前车的相关信息，包括坐标，速度，转向角，x-direction速度，y-direction速度
    以及x-direction加速度，y-direction加速度
    最终输出的数据格式为一个Dataframe
    通过RelationJudgement类获得两个ndarray，在本类中完成合并ndarray以及转换成一个Dataframe的操作
    两个ndarray分别存放了主车（-1*10）以及前车（-1*6）的信息
    """
    def __init__(self, trajectory_path: str, scenario_path: str):
        self.third_segment_length = None
        self.second_segment_length = None
        self.first_segment_length = None
        self.end_state = None
        self.front_vehicle_ndarray = None
        self.ego_vehicle_array = None
        self.ego_front_vehicle_info = None
        self.relation_judgement = RelationJudgement(trajectory_path, scenario_path)

    def init(self, interval: int):
        self.front_vehicle_ndarray, self.ego_vehicle_array = self.relation_judgement.make(interval)
        self.end_state = self.relation_judgement.info.replay_info['end_state']
        try:
            self.first_segment_length = self.relation_judgement.front_segment.shape[0]
            self.second_segment_length = self.relation_judgement.middle_segment.shape[0]
            self.third_segment_length = self.relation_judgement.latter_segment.shape[0]
        except AttributeError:
            self.first_segment_length = 0
            self.second_segment_length = 0
            self.third_segment_length = 0

    def merge_ndarray(self) -> ndarray:
        combination_array = np.hstack((self.ego_vehicle_array, self.front_vehicle_ndarray))
        return combination_array

    def ndarray_to_dataframe(self) -> None:
        if self.front_vehicle_ndarray is not None:####修改成ego
            combination_array = self.merge_ndarray()
            self.ego_front_vehicle_info = pd.DataFrame(combination_array, columns=['time', 'x_ego', 'y_ego', 'v_ego',
                                                                                   'yaw_ego', 'vx_ego', 'vy_ego', 'ax_ego',
                                                                                   'ay_ego', 'ego_lane_id', 'x_pre', 'y_pre', 'v_pre',
                                                                                   'yaw_pre', 'vx_pre', 'vy_pre'])
        else:
            self.ego_front_vehicle_info = None
        return None


class RelationJudgement:
    """
    该类用来判断主车和前车之间的关系，存在某一数据结构中，该结构还未设计 TODO
    """

    def __init__(self, trajectory_path: str, scenario_path: str):
        self.sut_lose_efficacy = None
        self.parse = Parser()
        self.info = None
        self.front_segment, self.middle_segment, self.latter_segment = [None for i in range(3)]
        self.info = self.parse.parse(trajectory_path, scenario_path)

    def init(self) -> None:
        # self.info = self.parse.parse(trajectory_path, scenario_path)
        self.front_segment, self.middle_segment, self.latter_segment, self.sut_lose_efficacy = segment_of_trajectory(
            self.info.trajectory_info['ego']['x'], self.info.trajectory_info['ego']['y'],
            self.info.replay_info['travel_direction'], self.info.zone)
        return

    @staticmethod
    def pnpoly(n_vert: int, vert_x: list, vert_y: list, test_x: float, test_y: float) -> bool:
        """
        用射线法判断点在多边形外部还是多边形内部，具体思路是从该测试点，向右引出一条射线，通过三角形比例关系计算
        该点在多边形两点间连线的哪一侧，具体可参考https://cloud.tencent.com/developer/article/1515808
        TODO 暂时未考虑车辆中心点正好位于多边形边界上的情况
        :param n_vert: 多变形的顶点点数
        :param vert_x: 多边形的顶点x坐标的列表
        :param vert_y: 多边形的顶点y坐标的列表
        :param test_x: 检测点x坐标
        :param test_y: 检测点y坐标
        :return: 是否在多边形内部， 是：True 否： False
        """
        c = 0
        for i in range(0, n_vert):
            if i == 0:
                j = n_vert - 1
            else:
                j = i - 1
            if operator.ne(operator.gt(vert_y[i], test_y), operator.gt(vert_y[j], test_y)) and operator.lt(test_x, (
                       vert_x[j] - vert_x[i]) * (test_y - vert_y[i]) / (vert_y[j] - vert_y[i]) + vert_x[i]):
                c = 1 - c
        return c

    @staticmethod
    def sampling_from_vertices_inside_intersection(discrete_lane, interval: int = 5) -> tuple:
        """
        车道边界线的轨迹点过多，为了减少对计算资源的消耗，节约评价时间，这里提供了一个可选择的轨迹点抽样因子
        :param discrete_lane:
        :param interval: 每个几个点抽样一个轨迹点作为顶点
        :return:
        """
        left_vert = discrete_lane.left_vertices[np.arange(0, discrete_lane.left_vertices.shape[0], interval), :]
        right_vert = discrete_lane.right_vertices[np.arange(0, discrete_lane.right_vertices.shape[0], interval), :]
        vertex_T = np.vstack((left_vert, right_vert[::-1]))
        vertex = vertex_T.T
        vert_x = list(vertex[0, :])
        vert_y = list(vertex[1, :])
        return vert_x, vert_y

    @staticmethod
    def take_the_vertex_of_straight_lane(discrete_lane) -> tuple:
        """
        求进口道的车道的顶点
        :param discrete_lane:
        :return:
        """
        vertex_T = np.array([discrete_lane.left_vertices[0], discrete_lane.left_vertices[-1],
                             discrete_lane.right_vertices[-1], discrete_lane.right_vertices[0]])
        vertex = vertex_T.T
        vert_x = list(vertex[0, :])
        vert_y = list(vertex[1, :])
        return vert_x, vert_y

    def judge_front_vehicle_id_version2(self, interval: int) -> tuple:  # (两个元素都为list)
        Directions = ['N', 'W', 'S', 'E']
        # 这地方可能会出问题，若出现车辆在多边形边界的情况则，ego_lane_id可能会少于轨迹点的个数
        # TODO
        ego_lane_id = []
        front_vehicle_id = []
        front_final_lane_id = None
        latter_start_lane_id = None
        x = self.front_segment[-1][0]
        y = self.front_segment[-1][1]
        for discrete_lane in self.info.openDrive_info.discretelanes:
            if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                    front_final_lane_id = discrete_lane.lane_id
                    break
        if self.latter_segment.size == 0:
            latter_start_lane_id = None
        else:
            x = self.latter_segment[0][0]
            y = self.latter_segment[0][1]
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                    vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                    if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                        latter_start_lane_id = discrete_lane.lane_id
                        break
        # 前半段
        for position in self.front_segment:
            inside_road = False
            x = position[0]
            y = position[1]
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                    vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                    if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                        inside_road = True
                        ego_lane_id.append(discrete_lane.lane_id)
                        front_vehicle_id.append(self.judge_front_vehicle_front_segment(vert_x, vert_y, ego_lane_id))
                        break
            if not inside_road:
                ego_lane_id.append(None)
                front_vehicle_id.append(None)
        # 交叉口内部
        if self.middle_segment.size == 0:
            pass
        else:
            for position in self.middle_segment:
                inside_road = False
                x = position[0]
                y = position[1]
                if latter_start_lane_id is not None:
                    for discrete_lane in self.info.map_dataformat["IN"].values():
                        vert_x, vert_y = self.sampling_from_vertices_inside_intersection(discrete_lane, interval)
                        if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                            temp_result = Directions.index(self.info.replay_info['travel_direction'][1]) - Directions.index(self.info.replay_info['travel_direction'][0])
                            if temp_result in [1, -3]:
                                direction_change = 'right_turn'
                            elif temp_result in [-1, 3]:
                                direction_change = 'left_turn'
                            elif temp_result in [2, -2]:
                                direction_change = 'straight'
                            else:
                                direction_change = 'unknown'  # 原则上不会出现
                            lane_type = lane_type_in_map(discrete_lane.center_vertices)
                            if lane_type == direction_change:
                                inside_road = True
                                ego_lane_id.append(discrete_lane.lane_id)
                                front_vehicle_id.append(self.judge_front_vehicle_middle_segment(vert_x, vert_y, ego_lane_id))
                                break
                    if not inside_road:
                        ego_lane_id.append(None)
                        front_vehicle_id.append(None)
                else:
                    for discrete_lane in self.info.map_dataformat["IN"].values():
                        vert_x, vert_y = self.sampling_from_vertices_inside_intersection(discrete_lane, interval)
                        if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                            direction_change = trajectory_type_in_map(list(self.middle_segment))
                            lane_type = lane_type_in_map(discrete_lane.center_vertices)
                            if direction_change == lane_type:
                                inside_road = True
                                ego_lane_id.append(discrete_lane.lane_id)
                                front_vehicle_id.append(
                                    self.judge_front_vehicle_middle_segment(vert_x, vert_y, ego_lane_id))
                                break
                            elif direction_change is None:
                                inside_road = True
                                ego_lane_id.append(discrete_lane.lane_id)
                                front_vehicle_id.append(
                                    self.judge_front_vehicle_middle_segment(vert_x, vert_y, ego_lane_id))
                                break
                    if not inside_road:
                        ego_lane_id.append(None)
                        front_vehicle_id.append(None)
        # 后半段
        if self.latter_segment.size == 0:
            pass
        else:
            for position in self.latter_segment:
                inside_road = False
                x = position[0]
                y = position[1]
                for discrete_lane in self.info.openDrive_info.discretelanes:
                    if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                        vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                        if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                            inside_road = True
                            ego_lane_id.append(discrete_lane.lane_id)
                            front_vehicle_id.append(self.judge_front_vehicle_latter_segment(vert_x, vert_y, ego_lane_id))
                            break
                if not inside_road:
                    ego_lane_id.append(None)
                    front_vehicle_id.append(None)
        return ego_lane_id, front_vehicle_id

    def judge_front_vehicle_id(self, interval: int) -> tuple:  # (两个元素都为list)
        # 这地方可能会出问题，若出现车辆在多边形边界的情况则，ego_lane_id可能会少于轨迹点的个数
        # TODO
        ego_lane_id = []
        front_vehicle_id = []
        front_final_lane_id = None
        latter_start_lane_id = None
        x = self.front_segment[-1][0]
        y = self.front_segment[-1][1]
        for discrete_lane in self.info.openDrive_info.discretelanes:
            if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                    front_final_lane_id = discrete_lane.lane_id
                    break
        if self.latter_segment.size == 0:
            latter_start_lane_id = None
        else:
            x = self.latter_segment[0][0]
            y = self.latter_segment[0][1]
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                    vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                    if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                        latter_start_lane_id = discrete_lane.lane_id
                        break
        # 前半段
        for position in self.front_segment:
            inside_road = False
            x = position[0]
            y = position[1]
            for discrete_lane in self.info.openDrive_info.discretelanes:
                if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                    vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                    if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                        inside_road = True
                        ego_lane_id.append(discrete_lane.lane_id)
                        front_vehicle_id.append(self.judge_front_vehicle_front_segment(vert_x, vert_y, ego_lane_id))
                        break
            if not inside_road:
                ego_lane_id.append(None)
                front_vehicle_id.append(None)
        # 交叉口内部
        if self.middle_segment.size == 0:
            pass
        else:
            for index, position in enumerate(self.middle_segment):
                inside_road = False
                x = position[0]
                y = position[1]
                if latter_start_lane_id is not None:
                    for discrete_lane in self.info.openDrive_info.discretelanes:
                        if not discrete_lane.predecessor or not discrete_lane.successor:
                            pass
                        else:
                            if discrete_lane.predecessor[0] == front_final_lane_id and discrete_lane.successor[0] == latter_start_lane_id:
                                vert_x, vert_y = self.sampling_from_vertices_inside_intersection(discrete_lane, interval)
                                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                                    inside_road = True
                                    ego_lane_id.append(discrete_lane.lane_id)
                                    front_vehicle_id.append(
                                        self.judge_front_vehicle_middle_segment(vert_x, vert_y, ego_lane_id))
                                    break
                    if not inside_road:
                        ego_lane_id.append(None)
                        front_vehicle_id.append(None)
                else:
                    for discrete_lane in self.info.openDrive_info.discretelanes:
                        if not discrete_lane.predecessor:
                            pass
                        else:
                            if discrete_lane.predecessor[0] == front_final_lane_id:
                                vert_x, vert_y = self.sampling_from_vertices_inside_intersection(discrete_lane, interval)
                                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                                    inside_road = True
                                    ego_lane_id.append(discrete_lane.lane_id)
                                    front_vehicle_id.append(
                                        self.judge_front_vehicle_middle_segment(vert_x, vert_y, ego_lane_id))
                                    break
                    if not inside_road:
                        ego_lane_id.append(None)
                        front_vehicle_id.append(None)
        # 后半段
        if self.latter_segment.size == 0:
            pass
        else:
            for position in self.latter_segment:
                inside_road = False
                x = position[0]
                y = position[1]
                for discrete_lane in self.info.openDrive_info.discretelanes:
                    if self.parse.open_drive_xml.getRoad(float(discrete_lane.lane_id.split('.')[0])).junction is None:
                        vert_x, vert_y = self.take_the_vertex_of_straight_lane(discrete_lane)
                        if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                            inside_road = True
                            ego_lane_id.append(discrete_lane.lane_id)
                            front_vehicle_id.append(self.judge_front_vehicle_latter_segment(vert_x, vert_y, ego_lane_id))
                            break
                if not inside_road:
                    ego_lane_id.append(None)
                    front_vehicle_id.append(None)
        #print(ego_lane_id)
        return ego_lane_id, front_vehicle_id

    def fixed_background_vehicle_speed(self) -> None:
        for vehicle in list(self.info.trajectory_info.keys()):
            if vehicle == 'ego':
                self.info.trajectory_info['ego']['vx'] = list(np.array(self.info.trajectory_info['ego']['v']) *
                                                              np.cos(np.array(self.info.trajectory_info['ego']['yaw'])))
                self.info.trajectory_info['ego']['vy'] = list(np.array(self.info.trajectory_info['ego']['v']) *
                                                              np.sin(np.array(self.info.trajectory_info['ego']['yaw'])))
            else:
                x_copy = self.info.trajectory_info[vehicle]['x']
                y_copy = self.info.trajectory_info[vehicle]['y']
                self.info.trajectory_info[vehicle]['vx'] = []
                self.info.trajectory_info[vehicle]['vy'] = []
                self.info.trajectory_info[vehicle]['v'] = np.array([])
                for i in range(len(x_copy) - 1):
                    diff_x = x_copy[i + 1] - x_copy[i]
                    diff_y = y_copy[i + 1] - y_copy[i]
                    self.info.trajectory_info[vehicle]['vx'].append(diff_x/self.info.replay_info['dt'])
                    self.info.trajectory_info[vehicle]['vy'].append(diff_y/self.info.replay_info['dt'])
                    self.info.trajectory_info[vehicle]['v'] = np.append(self.info.trajectory_info[vehicle]['v'],
                                                                        np.sqrt((diff_x / self.info.replay_info[
                                                                            'dt']) ** 2 + (diff_y / self.info.replay_info['dt']) ** 2))
                self.info.trajectory_info[vehicle]['vx'].append(self.info.trajectory_info[vehicle]['vx'][-1])
                self.info.trajectory_info[vehicle]['vy'].append(self.info.trajectory_info[vehicle]['vy'][-1])
                self.info.trajectory_info[vehicle]['v'] = np.append(self.info.trajectory_info[vehicle]['v'],
                                                                    self.info.trajectory_info[vehicle]['v'][-1])
        return

    def judge_front_vehicle_front_segment(self, vert_x: list, vert_y: list, lane_id_list: list) -> str:
        distance_min = 100000
        vehicle_id = None
        for vehicle in list(self.info.trajectory_info.keys()):
            if vehicle == 'ego':
                pass
            else:
                x = self.info.trajectory_info[vehicle]['x'][len(lane_id_list) - 1]
                y = self.info.trajectory_info[vehicle]['y'][len(lane_id_list) - 1]
                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                    if self.info.replay_info['travel_direction'][0] == 'W':
                        distance = x - self.info.trajectory_info['ego']['x'][len(lane_id_list) - 1]
                        if 0 < distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][0] == 'E':
                        distance = x - self.info.trajectory_info['ego']['x'][len(lane_id_list) - 1]
                        if distance < 0 and abs(distance) < distance_min:
                            distance_min = abs(distance)
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][0] == 'N':
                        distance = y - self.info.trajectory_info['ego']['y'][len(lane_id_list) - 1]
                        if distance < 0 and abs(distance) < distance_min:
                            distance_min = abs(distance)
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][0] == 'S':
                        distance = y - self.info.trajectory_info['ego']['y'][len(lane_id_list) - 1]
                        if 0 < distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
        return vehicle_id

    def judge_front_vehicle_middle_segment(self, vert_x: list, vert_y: list, lane_id_list: list) -> str:
        distance_min = 100000
        vehicle_id = None
        for vehicle in list(self.info.trajectory_info.keys()):
            if vehicle == 'ego':
                pass
            else:
                x = self.info.trajectory_info[vehicle]['x'][len(lane_id_list) - 1]
                y = self.info.trajectory_info[vehicle]['y'][len(lane_id_list) - 1]
                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                    distance_x = x - self.info.trajectory_info['ego']['x'][len(lane_id_list) - 1]
                    distance_y = y - self.info.trajectory_info['ego']['y'][len(lane_id_list) - 1]
                    distance = np.sqrt(distance_x ** 2 + distance_y ** 2)
                    if self.info.replay_info['travel_direction'] == ['W', 'N']:
                        if distance_x > 0 and distance_y > 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['W', 'E']:
                        if 0 < distance_x < distance_min:
                            distance_min = distance_x
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['W', 'S']:
                        if distance_x > 0 and distance_y < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['N', 'W']:
                        if distance_x < 0 and distance_y < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['N', 'S']:
                        if distance_y < 0 and abs(distance_y) < distance_min:
                            distance_min = abs(distance_y)
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['N', 'E']:
                        if distance_x > 0 and distance_y < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['E', 'N']:
                        if distance_y > 0 and distance_x < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['E', 'W']:
                        if distance_x < 0 and abs(distance_x) < distance_min:
                            distance_min = abs(distance_x)
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['E', 'S']:
                        if distance_x < 0 and distance_y < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['S', 'W']:
                        if distance_x < 0 and distance_y > 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['S', 'N']:
                        if 0 < distance_y < distance_min:
                            distance_min = distance_y
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['S', 'E']:
                        if distance_x > 0 and distance_y > 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['W', 'IN']:
                        if distance_x > 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['E', 'IN']:
                        if distance_x < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['N', 'IN']:
                        if distance_y < 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'] == ['S', 'IN']:
                        if distance_y > 0 and distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
        return vehicle_id

    def judge_front_vehicle_latter_segment(self, vert_x: list, vert_y: list, lane_id_list: list) -> str:
        distance_min = 100000
        vehicle_id = None
        for vehicle in list(self.info.trajectory_info.keys()):
            if vehicle == 'ego':
                pass
            else:
                x = self.info.trajectory_info[vehicle]['x'][len(lane_id_list) - 1]
                y = self.info.trajectory_info[vehicle]['y'][len(lane_id_list) - 1]
                if self.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                    if self.info.replay_info['travel_direction'][1] == 'W':
                        distance = x - self.info.trajectory_info['ego']['x'][len(lane_id_list) - 1]
                        if distance < 0 and abs(distance) < distance_min:
                            distance_min = abs(distance)
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][1] == 'E':
                        distance = x - self.info.trajectory_info['ego']['x'][len(lane_id_list) - 1]
                        if 0 < distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][1] == 'N':
                        distance = y - self.info.trajectory_info['ego']['y'][len(lane_id_list) - 1]
                        if 0 < distance < distance_min:
                            distance_min = distance
                            vehicle_id = vehicle
                    elif self.info.replay_info['travel_direction'][1] == 'S':
                        distance = y - self.info.trajectory_info['ego']['y'][len(lane_id_list) - 1]
                        if distance < 0 and abs(distance) < distance_min:
                            distance_min = abs(distance)
                            vehicle_id = vehicle
        return vehicle_id

    def make_front_vehicle_ndarray(self, front_vehicle_id_list: list) -> ndarray:
        front_vehicle_x = []
        front_vehicle_y = []
        front_vehicle_v = []
        front_vehicle_vx = []
        front_vehicle_vy = []
        front_vehicle_yaw = []
        for vehicle, t in zip(front_vehicle_id_list, range(len(self.info.trajectory_info['ego']['x']))):
            if vehicle is None:
                front_vehicle_x.append(10000)
                front_vehicle_y.append(10000)
                front_vehicle_v.append(10000)
                front_vehicle_vx.append(10000)
                front_vehicle_vy.append(10000)
                front_vehicle_yaw.append(10000)
            else:
                front_vehicle_x.append(self.info.trajectory_info[vehicle]['x'][t])
                front_vehicle_y.append(self.info.trajectory_info[vehicle]['y'][t])
                front_vehicle_v.append(self.info.trajectory_info[vehicle]['v'][t])
                front_vehicle_yaw.append(self.info.trajectory_info[vehicle]['yaw'][t])
                front_vehicle_vx.append(self.info.trajectory_info[vehicle]['vx'][t])
                front_vehicle_vy.append(self.info.trajectory_info[vehicle]['vy'][t])
        front_vehicle_array = np.array([np.array(front_vehicle_x),
                                        np.array(front_vehicle_y),
                                        np.array(front_vehicle_v),
                                        np.array(front_vehicle_yaw),
                                        np.array(front_vehicle_vx),
                                        np.array(front_vehicle_vy)])
        front_vehicle_array = front_vehicle_array.T
        return front_vehicle_array

    def make_ego_vehicle_ndarray(self, ego_lane_id: list) -> ndarray:
        #    print(np.array(self.info.replay_info['t']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['x']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['y']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['v']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['yaw']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['vx']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['vy']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['ax']).shape)
        #    print(np.array(self.info.trajectory_info['ego']['ay']).shape)
        #    print(np.array(ego_lane_id).shape)
        ego_vehicle_array = np.array([np.array(self.info.replay_info['t']),
                                      np.array(self.info.trajectory_info['ego']['x']),
                                      np.array(self.info.trajectory_info['ego']['y']),
                                      np.array(self.info.trajectory_info['ego']['v']),
                                      np.array(self.info.trajectory_info['ego']['yaw']),
                                      np.array(self.info.trajectory_info['ego']['vx']),
                                      np.array(self.info.trajectory_info['ego']['vy']),
                                      np.array(self.info.trajectory_info['ego']['ax']),
                                      np.array(self.info.trajectory_info['ego']['ay']),
                                      np.array(ego_lane_id)])
        ego_vehicle_array = ego_vehicle_array.T
        return ego_vehicle_array

    def calc_ego_vehicle_acc(self) -> None:
        vx_copy = self.info.trajectory_info['ego']['vx']
        vy_copy = self.info.trajectory_info['ego']['vy']
        self.info.trajectory_info['ego']['ax'] = []
        self.info.trajectory_info['ego']['ay'] = []
        for i in range(len(vx_copy) - 1):
            diff_vx = vx_copy[i + 1] - vx_copy[i]
            diff_vy = vy_copy[i + 1] - vy_copy[i]
            self.info.trajectory_info['ego']['ax'].append(diff_vx / self.info.replay_info['dt'])
            self.info.trajectory_info['ego']['ay'].append(diff_vy / self.info.replay_info['dt'])
        self.info.trajectory_info['ego']['ax'].append(self.info.trajectory_info['ego']['ax'][-1])
        self.info.trajectory_info['ego']['ay'].append(self.info.trajectory_info['ego']['ay'][-1])
        return None

    def make(self, interval: int) -> tuple:
        self.init()
        if self.sut_lose_efficacy:
            front_vehicle_array, ego_vehicle_array = [None, None]
        else:
            ego_lane_id, front_vehicle_id = self.judge_front_vehicle_id_version2(interval)
            self.fixed_background_vehicle_speed()
            front_vehicle_array = self.make_front_vehicle_ndarray(front_vehicle_id)
            self.calc_ego_vehicle_acc()
            ego_vehicle_array = self.make_ego_vehicle_ndarray(ego_lane_id)
        return front_vehicle_array, ego_vehicle_array


if __name__ == "__main__":
    vertices_x = [1, 2, 2, 1]
    vertices_y = [1, 1, 2, 2]
    print(RelationJudgement.pnpoly(4, vertices_x, vertices_y, 3, 5))
    print(RelationJudgement.pnpoly(4, vertices_x, vertices_y, 1.5, 1.5))