# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/2/23 20:23
import numpy as np
import pandas as pd
import math


def heading_fix_inside(heading_np, str2judge):
    # 把heading正坐标方向旋转，x轴正方向取决于heading数组的初始值

    pi = math.pi
    heading_np_fixed = np.zeros((len(heading_np),))
    if str2judge == "lane":
        heading_start = heading_np[0]
    else:
        heading_start = (heading_np[0:5]).sum() / 5

    for heading_idx in range(len(heading_np)):
        heading_np_fixed[heading_idx] = heading_np[heading_idx] - heading_start
        if pi < heading_np_fixed[heading_idx] <= 2 * pi:
            heading_np_fixed[heading_idx] = heading_np_fixed[heading_idx] - 2 * pi
        elif -2 * pi <= heading_np_fixed[heading_idx] < - pi:
            heading_np_fixed[heading_idx] = heading_np_fixed[heading_idx] + 2 * pi

    #     print(heading_np_fixed)
    return heading_np_fixed


def judge_direction_of_lane_or_trajectory(heading, str2judge):
    pi = math.pi
    heading_np = np.array(heading)
    heading_np_fixed = heading_fix_inside(heading_np, str2judge)
    heading_dif_np = heading_np_fixed - heading_np_fixed[0]

    # 全程转向角变化 [1/3 * pi,2/3 * pi]

    if ((1 / 6 * pi) <= heading_dif_np[
                        len(heading_dif_np) - 3:len(heading_dif_np)]).all() and \
            ((heading_dif_np[
              len(heading_dif_np) - 3:len(heading_dif_np)]) <= (2 / 3 * pi)).all():

        #         heading_everydif_np = heading_dif_np[1:]-heading_dif_np[0:-1]
        #         # heading_everydif_np>0.01的比例大于0.1？
        #         if ((heading_everydif_np>0.01).sum()/len(heading_everydif_np)) >= 0.1:
        track_type = 'left_turn'
    elif ((-1 / 6 * pi) < heading_dif_np[
                          len(heading_dif_np) - 3:len(heading_dif_np)]).all() and \
            ((heading_dif_np[
              len(heading_dif_np) - 3:len(heading_dif_np)]) < (1 / 6 * pi)).all():
        track_type = 'straight'
    elif (-(2 / 3 * pi) <= heading_dif_np[
                           len(heading_dif_np) - 3:len(heading_dif_np)]).all() and \
            ((heading_dif_np[
              len(heading_dif_np) - 3:len(heading_dif_np)]) < (-1 / 4 * pi)).all():
        track_type = 'right_turn'
    # 后添加-报错可删
    elif ((1 / 6 * pi) < heading_dif_np[
                         len(heading_dif_np) - 3:len(heading_dif_np)]).all() and \
            ((heading_dif_np[
              len(heading_dif_np) - 3:len(heading_dif_np)]) <= pi).all():
        track_type = 'maybe_left_turn'
    else:
        # 小角度的转向轨迹，因为场景没有采集完全
        # 根据section判断
        track_type = 'unknown'
    return track_type


def lane_type_in_map(trajectory):
    # 求intersection内部路段的航向角，判断车道方向
    lane_heading = []
    for i in range(len(trajectory) - 1):
        a = trajectory[i + 1] - trajectory[i]
        arctan2_ = np.arctan2(a[1], a[0])
        lane_heading.append(arctan2_)
    if judge_direction_of_lane_or_trajectory(lane_heading, 'lane') == 'left_turn' or \
            judge_direction_of_lane_or_trajectory(lane_heading, 'lane') == 'maybe_left_turn':
        lane_flag = 'left_turn'
    elif judge_direction_of_lane_or_trajectory(lane_heading, 'lane') == 'right_turn':
        lane_flag = 'right_turn'
    elif judge_direction_of_lane_or_trajectory(lane_heading, 'lane') == 'straight':
        lane_flag = 'straight'
    else:
        lane_flag = None
    return lane_flag


def trajectory_type_in_map(trajectory):
    # 求未驶出交叉口的轨迹的行驶方向
    if len(trajectory) < 5:
        return None
    trajectory_heading = []
    for i in range(len(trajectory) - 1):
        a = trajectory[i + 1] - trajectory[i]
        arctan2_ = np.arctan2(a[1], a[0])
        trajectory_heading.append(arctan2_)
    if judge_direction_of_lane_or_trajectory(trajectory_heading, 'trajectory') == 'left_turn' or \
            judge_direction_of_lane_or_trajectory(trajectory_heading, 'trajectory') == 'maybe_left_turn':
        trajectory_flag = 'left_turn'
    elif judge_direction_of_lane_or_trajectory(trajectory_heading, 'trajectory') == 'right_turn':
        trajectory_flag = 'right_turn'
    elif judge_direction_of_lane_or_trajectory(trajectory_heading, 'trajectory') == 'straight':
        trajectory_flag = 'straight'
    else:
        trajectory_flag = None
    return trajectory_flag
