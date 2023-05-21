# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/30 11:43
import numpy as np
import pandas as pd
from pandas import DataFrame
from pandas import Series
from evaluation_prepare.ego_and_forward_vehicle_relation import EgoForwardVehicleInfo, RelationJudgement


class SafetyCriteria:
    """
    这里定义了与安全相关指标的评价方法，包括：碰撞、TTC、PET等指标的计算
    """

    def __init__(self, EgoForwardVehicleInfo):
        self.deducted_score = None
        self.info_table = EgoForwardVehicleInfo

    @staticmethod
    def cal_ttc_out_intersection(ego_pos: float, forward_pos: float, ego_v: float, forward_v: float) -> float:
        ttc = (forward_pos - ego_pos) / (ego_v - forward_v)
        return ttc

    def penalty_for_collision(self) -> None:
        if self.info_table.end_state == 2:
            self.deducted_score = 50
        else:
            self.deducted_score = 0
        return None

    def cal_ttc(self) -> None:
        front_segment = self.info_table.ego_front_vehicle_info.iloc[0:self.info_table.first_segment_length, :]
        middle_segment = self.info_table.ego_front_vehicle_info.iloc[
                         self.info_table.first_segment_length:self.info_table.first_segment_length + self.info_table.second_segment_length,
                         :]
        latter_segment = self.info_table.ego_front_vehicle_info.iloc[
                         self.info_table.first_segment_length + self.info_table.second_segment_length:, :]
        front_segment = front_segment.loc[front_segment['x_pre'] != 10000, :]
        front_ttc,front_ttc_all = self.front_segment_ttc(front_segment)
        middle_segment = middle_segment.loc[middle_segment['x_pre'] != 10000, :]
        middle_ttc,middle_ttc_all = self.middle_segment_ttc(middle_segment)
        latter_segment = latter_segment.loc[latter_segment['x_pre'] != 10000, :]
        latter_ttc,latter_ttc_all = self.latter_segment_ttc(latter_segment)
        self.deducted_score = self.deducted_score + (front_ttc.shape[0] + middle_ttc.shape[0] + latter_ttc.shape[0]) / \
                              self.info_table.ego_front_vehicle_info.shape[0] * 50
        # print(self.deducted_score)
        mean_ttc=0
        if self.info_table.ego_front_vehicle_info.shape[0]!=0:
            mean_ttc = (sum(front_ttc_all[front_ttc_all>0]) + sum(middle_ttc_all[middle_ttc_all>0]) + sum(
                latter_ttc_all[latter_ttc_all>0])) / self.info_table.ego_front_vehicle_info.shape[0]
            #mean_ttc=(sum(~np.isnan(front_ttc_all))+sum(~np.isnan(middle_ttc_all))+sum(~np.isnan(latter_ttc_all)))/self.info_table.ego_front_vehicle_info.shape[0]
        return mean_ttc

    def front_segment_ttc(self, front_segment: DataFrame) -> Series:
        ttc = None
        if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'E' or 'W':
            ttc = (front_segment['x_pre'].astype(float) - front_segment['x_ego'].astype(float)) / (
                    front_segment['vx_ego'].astype(float) - front_segment['vx_pre'].astype(float))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
            ttc = (front_segment['y_pre'].astype(float) - front_segment['y_ego'].astype(float)) / (
                    front_segment['vy_ego'].astype(float) - front_segment['vy_pre'].astype(float))
        ttc = np.array(ttc)
        ttc1 = ttc[0 < ttc]
        ttc1 = ttc1[ttc1 < 1]
        return ttc1,ttc

    def latter_segment_ttc(self, latter_segment: DataFrame) -> Series:
        ttc = None
        if self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'E' or 'W':
            ttc = (latter_segment['x_pre'].astype(float) - latter_segment['x_ego'].astype(float)) / (
                    latter_segment['vx_ego'].astype(float) - latter_segment['vx_pre'].astype(float))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'N' or 'S':
            ttc = (latter_segment['y_pre'].astype(float) - latter_segment['y_ego'].astype(float)) / (
                    latter_segment['vy_ego'].astype(float) - latter_segment['vy_pre'].astype(float))
        else:
            ttc = pd.Series()
        ttc = np.array(ttc)
        ttc1 = ttc[0 < ttc]
        ttc1 = ttc1[ttc1 < 1]
        return ttc1,ttc

    def middle_segment_ttc(self, middle_segment: DataFrame) -> Series:
        ttc = None
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ['E', 'W'] or ['W', 'E']:
            ttc = (middle_segment['x_pre'].astype(float) - middle_segment['x_pre'].astype(float)) / (
                    middle_segment['vx_ego'].astype(float) - middle_segment['vx_pre'].astype(float))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ['N', 'S'] or ['S', 'N']:
            ttc = (middle_segment['y_pre'].astype(float) - middle_segment['y_pre'].astype(float)) / (
                    middle_segment['vy_ego'].astype(float) - middle_segment['vy_pre'].astype(float))
        else:
            v_diff = middle_segment['v_ego'].astype(float) - middle_segment['v_pre'].astype(float)
            dis = np.sqrt((middle_segment['x_pre'].astype(float) - middle_segment['x_pre'].astype(float)) ** 2 + (
                    middle_segment['y_pre'].astype(float) - middle_segment['y_pre'].astype(float)) ** 2)
            v_diff[v_diff < 0] = 0.000001
            ttc = dis / v_diff
        ttc = np.array(ttc)
        ttc1 = ttc[0 < ttc]
        ttc1 = ttc1[ttc1 < 1]
        return ttc1,ttc

    def penalty_for_outside_road(self, interval=1) -> None:
        front_segment = self.info_table.ego_front_vehicle_info.iloc[0:self.info_table.first_segment_length, :]
        middle_segment = self.info_table.ego_front_vehicle_info.iloc[
                         self.info_table.first_segment_length:self.info_table.first_segment_length + self.info_table.second_segment_length,
                         :]
        latter_segment = self.info_table.ego_front_vehicle_info.iloc[
                         self.info_table.first_segment_length + self.info_table.second_segment_length:, :]
        # 只计算进口道和出口道的驶出车道，优先判断是否驶出对应的进口道和出口道，随后判断是否驶出车道
        # 进口道
        un_tolerable_out_num = 0
        tolerable_out_num = 0
        front_values = front_segment['ego_lane_id'].value_counts()
        for idx in front_values.index.values:
            if idx not in self.info_table.relation_judgement.info.map_dataformat[self.info_table.relation_judgement.info.replay_info['travel_direction'][0] + 'I'].keys():
                if idx in self.info_table.relation_judgement.info.map_dataformat[self.info_table.relation_judgement.info.replay_info['travel_direction'][0] + 'O'].keys():
                    tolerable_out_num += front_values[idx]
                else:
                    un_tolerable_out_num += front_values[idx]
        # 交叉口内部，仅考虑是否驶出交叉口边界
        if middle_segment.empty:
            middle_values = []
        else:
            middle_values = []
            for x, y in zip(list(middle_segment['x_ego'].astype(float)), list(middle_segment['y_ego'].astype(float))):
                inside_road = False
                for discrete_lane in self.info_table.relation_judgement.info.map_dataformat["IN"].values():
                    vert_x, vert_y = RelationJudgement.sampling_from_vertices_inside_intersection(discrete_lane, interval)
                    if RelationJudgement.pnpoly(len(vert_x), vert_x, vert_y, x, y):
                        middle_values.append('in')
                        inside_road = True
                        break
                if not inside_road:
                    middle_values.append('out')
            un_tolerable_out_num += middle_values.count('out')
        # 出口道，首先判断第三段是否有轨迹，若没有轨迹则不需要计数，若有轨迹继续计数
        if latter_segment.empty:
            pass
        else:
            latter_values = latter_segment['ego_lane_id'].value_counts()
            for idx in latter_values.index.values:
                if idx not in self.info_table.relation_judgement.info.map_dataformat[self.info_table.relation_judgement.info.replay_info['travel_direction'][1] + 'O'].keys():
                    if idx in self.info_table.relation_judgement.info.map_dataformat[self.info_table.relation_judgement.info.replay_info['travel_direction'][1] + 'I'].keys():
                        tolerable_out_num += latter_values[idx]
                    else:
                        un_tolerable_out_num += latter_values[idx]
        # if tolerable_out_num == 0 and un_tolerable_out_num == 0:
        #     return None
        # else:
        self.deducted_score = self.deducted_score + 50 * un_tolerable_out_num/(front_segment.shape[0] + latter_segment.shape[0] + middle_segment.shape[0]) + 25 * tolerable_out_num/(front_segment.shape[0] + latter_segment.shape[0])
        # if tolerable_out_num>0:
        #     print("驶入对向车道")
        # if un_tolerable_out_num>0:
        #     print("驶出行车道")
        oppo_lane_rate =0
        out_area_rate=0
        if (front_segment.shape[0] + latter_segment.shape[0])!=0:
            oppo_lane_rate=tolerable_out_num/(front_segment.shape[0] + latter_segment.shape[0])
        if (front_segment.shape[0] + latter_segment.shape[0] + middle_segment.shape[0])!=0:
            out_area_rate=un_tolerable_out_num/(front_segment.shape[0] + latter_segment.shape[0] + middle_segment.shape[0])

        return oppo_lane_rate,out_area_rate

    def penalty_for_running_red_light(self) -> None:
        run_red=0
        x_coordinate = list(self.info_table.ego_front_vehicle_info.loc[:, 'x_ego'])
        y_coordinate = list(self.info_table.ego_front_vehicle_info.loc[:, 'y_ego'])
        coordinate = list(zip(x_coordinate, y_coordinate))
        if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' and self.info_table.relation_judgement.info.replay_info['travel_direction']!=('W','S'):
            for index, (x, y) in enumerate(coordinate):
                if (float(x) < float(self.info_table.relation_judgement.info.replay_info['stop_line']['W'][3])) and (
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['S'][3]) < float(y) <
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['N'][3])):
                    if index == len(coordinate) - 1:
                        pass
                    else:
                        if (float(coordinate[index + 1][0]) > float(
                                self.info_table.relation_judgement.info.replay_info['stop_line'][
                                    'W'][3])) and (
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['S'][3]) <
                                float(coordinate[index + 1][1]) <
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['N'][3])):
                            if self.info_table.relation_judgement.info.light_info[index] == 'red' and \
                                    self.info_table.relation_judgement.info.light_info[index + 1] == 'red':
                                self.deducted_score += 10
                                #print("闯红灯")
                                run_red=1
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'E' and self.info_table.relation_judgement.info.replay_info['travel_direction']!=('E','N'):
            for index, (x, y) in enumerate(coordinate):
                if (float(x) > float(self.info_table.relation_judgement.info.replay_info['stop_line']['E'][3])) and (
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['S'][3]) < float(y) <
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['N'][3])):
                    if index == len(coordinate) - 1:
                        pass
                    else:
                        if (float(coordinate[index + 1][0]) < float(
                                self.info_table.relation_judgement.info.replay_info['stop_line'][
                                    'E'][3])) and (
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['S'][3]) <
                                float(coordinate[index + 1][1]) <
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['N'][3])):
                            if self.info_table.relation_judgement.info.light_info[index] == 'red' and \
                                    self.info_table.relation_judgement.info.light_info[index + 1] == 'red':
                                self.deducted_score += 10
                                #print("闯红灯")
                                run_red = 1
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' and self.info_table.relation_judgement.info.replay_info['travel_direction']!=('N','W'):
            for index, (x, y) in enumerate(coordinate):
                if (float(y) > float(self.info_table.relation_judgement.info.replay_info['stop_line']['N'][3])) and (
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['W'][3]) < float(x) <
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['E'][3])):
                    if index == len(coordinate) - 1:
                        pass
                    else:
                        if (float(coordinate[index + 1][1]) < float(
                                self.info_table.relation_judgement.info.replay_info['stop_line'][
                                    'N'][3])) and (
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['W'][3]) <
                                float(coordinate[index + 1][0]) <
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['E'][3])):
                            if self.info_table.relation_judgement.info.light_info[index] == 'red' and \
                                    self.info_table.relation_judgement.info.light_info[index + 1] == 'red':
                                self.deducted_score += 10
                                #print("闯红灯")
                                run_red = 1
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'S' and self.info_table.relation_judgement.info.replay_info['travel_direction']!=('S','E'):
            for index, (x, y) in enumerate(coordinate):
                if (float(y) < float(self.info_table.relation_judgement.info.replay_info['stop_line']['S'][3])) and (
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['W'][3]) < float(x) <
                        float(self.info_table.relation_judgement.info.replay_info['stop_line']['E'][3])):
                    if index == len(coordinate) - 1:
                        pass
                    else:
                        if (float(coordinate[index + 1][1]) > float(
                                self.info_table.relation_judgement.info.replay_info['stop_line'][
                                    'S'][3])) and (
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['W'][3]) <
                                float(coordinate[index + 1][0]) <
                                float(self.info_table.relation_judgement.info.replay_info['stop_line']['E'][3])):
                            if self.info_table.relation_judgement.info.light_info[index] == 'red' and \
                                    self.info_table.relation_judgement.info.light_info[index + 1] == 'red':
                                self.deducted_score += 10
                                #print("闯红灯")
                                run_red = 1
        return run_red

    def safety_evaluation(self) -> float:
        oppo_lane_rate=0
        out_area_rate=0
        run_red=0
        mean_ttc=0
        if self.info_table.ego_front_vehicle_info is None:
            self.deducted_score = 50
        elif self.info_table.ego_front_vehicle_info.loc[
            abs(self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float')) > 200, 'ax_ego'].shape[0] != 0:
            self.deducted_score = 50
        elif self.info_table.ego_front_vehicle_info.loc[
            abs(self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float')) > 200, 'ay_ego'].shape[0] != 0:
            self.deducted_score = 50
        else:
            self.penalty_for_collision()
            if self.deducted_score != 50:
                mean_ttc=self.cal_ttc()
                oppo_lane_rate,out_area_rate=self.penalty_for_outside_road()
                run_red=self.penalty_for_running_red_light()
                self.deducted_score = np.clip(self.deducted_score, 0, 50)
        return self.deducted_score,mean_ttc,oppo_lane_rate,out_area_rate,run_red


if __name__ == "__main__":
    Trajectory_path = r''
    Scenario_path = r''
    Interval = 5
    ego_front_vehicle_info = EgoForwardVehicleInfo(Trajectory_path, Scenario_path, Interval)
    ego_front_vehicle_info.ndarray_to_dataframe()
    safety_deduct = SafetyCriteria(ego_front_vehicle_info)
    safety_deduct_score = safety_deduct.safety_evaluation()
    print(safety_deduct_score)
