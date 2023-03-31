# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/30 11:43
import numpy as np
import pandas as pd
from evaluation_prepare.ego_and_forward_vehicle_relation import EgoForwardVehicleInfo


class EfficiencyCriteria:
    """
            这里定义了与效率相关的指标，包括任务完成和任务耗时
    """
    def __init__(self, EgoForwardVehicleInfo):
        self.deducted_score = None
        self.info_table = EgoForwardVehicleInfo

    def penalty_for_unfinished_task(self) -> None:
        distance_todest=0
        if self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'N':
            if float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego) < (min(self.info_table.relation_judgement.info.openScenario_info['goal_y']) - 5):
                self.deducted_score = 10
                #print("距离：",min(self.info_table.relation_judgement.info.openScenario_info['goal_y'])-float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego))
                distance_todest=min(self.info_table.relation_judgement.info.openScenario_info['goal_y'])-float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego)
            else:
                self.deducted_score = 0
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'S':
            if (max(self.info_table.relation_judgement.info.openScenario_info['goal_y']) + 5) < float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego):
                self.deducted_score = 10
                #print("距离：",float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego)-max(self.info_table.relation_judgement.info.openScenario_info['goal_y']))
                distance_todest=float(self.info_table.ego_front_vehicle_info.iloc[-1, :].y_ego)-max(self.info_table.relation_judgement.info.openScenario_info['goal_y'])
            else:
                self.deducted_score = 0
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'W':
            if (max(self.info_table.relation_judgement.info.openScenario_info['goal_x']) + 5) < float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego):
                self.deducted_score = 10
                #print("距离：",float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego)-max(self.info_table.relation_judgement.info.openScenario_info['goal_x']))
                distance_todest=float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego)-max(self.info_table.relation_judgement.info.openScenario_info['goal_x'])
            else:
                self.deducted_score = 0
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'E':
            if float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego) < (min(self.info_table.relation_judgement.info.openScenario_info['goal_x']) - 5):
                self.deducted_score = 10
                #print("距离：",min(self.info_table.relation_judgement.info.openScenario_info['goal_x'])-float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego))
                distance_todest=min(self.info_table.relation_judgement.info.openScenario_info['goal_x'])-float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego)
            else:
                self.deducted_score = 0
        return distance_todest

    def penalty_for_time_consuming(self) -> None:
        speed_limited = 9
        distance = []
        middle_segment = self.info_table.ego_front_vehicle_info.iloc[
                         self.info_table.first_segment_length:self.info_table.first_segment_length + self.info_table.second_segment_length,
                         :]
        middle_segment_x = list(middle_segment['x_ego'])
        middle_segment_y = list(middle_segment['y_ego'])
        if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
            travel_time_one = abs(self.info_table.relation_judgement.info.replay_info['stop_line']
                                  [self.info_table.relation_judgement.info.replay_info['travel_direction'][0]][3] -
                                  float(self.info_table.ego_front_vehicle_info.loc[0, 'x_ego'])) / speed_limited
        else:
            travel_time_one = abs(self.info_table.relation_judgement.info.replay_info['stop_line']
                                  [self.info_table.relation_judgement.info.replay_info['travel_direction'][0]][3] -
                                  float(self.info_table.ego_front_vehicle_info.loc[0, 'y_ego'])) / speed_limited
        for i in range(len(middle_segment_x) - 1):
            diff_x = float(middle_segment_x[i + 1]) - float(middle_segment_x[i])
            diff_y = float(middle_segment_y[i + 1]) - float(middle_segment_y[i])
            distance.append(np.sqrt(diff_x**2+diff_y**2))
        distance_sum = sum(distance)
        travel_time_two = distance_sum / speed_limited
        try:
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'W' or 'E':
                travel_time_three = abs(self.info_table.relation_judgement.info.replay_info['stop_line']
                                        [self.info_table.relation_judgement.info.replay_info['travel_direction'][1]][3] -
                                        float(self.info_table.ego_front_vehicle_info.iloc[-1, :].x_ego)) / speed_limited
            else:
                travel_time_three = abs(self.info_table.relation_judgement.info.replay_info['stop_line']
                                        [self.info_table.relation_judgement.info.replay_info['travel_direction'][1]][3] -
                                        float(self.info_table.ego_front_vehicle_info.loc[-1, :].y_ego)) / speed_limited
        except KeyError:
            travel_time_three = 0
        expected_time = travel_time_one + travel_time_two + travel_time_three + 5*self.info_table.relation_judgement.info.replay_info['dt']
        temporary_score = expected_time/float(self.info_table.ego_front_vehicle_info.iloc[-1, :].time) * 20
        temporary_score = np.clip(temporary_score, 0, 20)
        self.deducted_score = self.deducted_score + 20 - temporary_score
        #print("平均速度：", expected_time / float(self.info_table.ego_front_vehicle_info.iloc[-1, :].time) * 9)
        mean_vy=expected_time / float(self.info_table.ego_front_vehicle_info.iloc[-1, :].time)* 9
        return mean_vy

    def efficiency_evaluation(self) -> float:
        done_ornot=0
        mean_vy=0
        distance_todest =0
        if self.info_table.ego_front_vehicle_info is None:
            self.deducted_score = 30
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') )> 200, 'ax_ego'].shape[0]!=0:
            self.deducted_score = 30
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') )> 200, 'ay_ego'].shape[0]!=0:
            self.deducted_score = 30
        else:
            if self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
                    self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(self.info_table.relation_judgement.info.replay_info['travel_direction']):
                self.deducted_score = 10
                #print("行驶方向错误")# 未完成任务的10分
                done_ornot = 1
                mean_vy=self.penalty_for_time_consuming()
                self.deducted_score = np.clip(self.deducted_score, 0, 30)
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
                self.deducted_score = 10
                #print("未驶出交叉口")# 未完成任务的10分
                done_ornot = 1
                mean_vy=self.penalty_for_time_consuming()
                self.deducted_score = np.clip(self.deducted_score, 0, 30)
            elif tuple(self.info_table.relation_judgement.info.replay_info['travel_direction']) != self.info_table.relation_judgement.info.replay_info['target_travel_direction']:
                self.deducted_score = 10
                #print("行驶方向错误")
                done_ornot = 1
                mean_vy=self.penalty_for_time_consuming()
                self.deducted_score = np.clip(self.deducted_score, 0, 30)
            else:
                distance_todest=self.penalty_for_unfinished_task()
                mean_vy=self.penalty_for_time_consuming()
                self.deducted_score = np.clip(self.deducted_score, 0, 30)
        return self.deducted_score,done_ornot,mean_vy,distance_todest

if __name__ == "__main__":
    Trajectory_path = r''
    Scenario_path = r''
    Interval = 5
    ego_front_vehicle_info = EgoForwardVehicleInfo(Trajectory_path, Scenario_path, Interval)
    ego_front_vehicle_info.ndarray_to_dataframe()
    efficiency_deduct = EfficiencyCriteria(ego_front_vehicle_info)
    efficiency_deduct_score = efficiency_deduct.efficiency_evaluation()
    print(efficiency_deduct_score)