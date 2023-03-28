# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/26 20:17
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import shapely.geometry
import shapely


def segment_of_trajectory(x: list, y: list, travel_direction: tuple, zone: dict) -> tuple:
    """
    将轨迹分成三部分进行评价，分别为进口道，交叉口内部，出口道
    :param x:
    :param y:
    :param stop_line:
    :param travel_direction:
    :return:
    """
    position = np.vstack((np.array(x), np.array(y))).T  # [[x1,y1],[x2,y2]]
    sut_lose_efficacy = False
    front_segment = None
    middle_segment = None
    latter_segment = None
    if travel_direction.count(travel_direction[0]) == len(travel_direction):
        front_segment = position
        middle_segment = np.array([]).reshape(-1, 2)
        latter_segment = np.array([]).reshape(-1, 2)
        sut_lose_efficacy = False
    elif travel_direction[1] == 'IN':
        for i in range(position.shape[0]-1):
            if i < (position.shape[0] - 4):
                point_one = shapely.geometry.Point(position[i][0], position[i][1])
                point_two = shapely.geometry.Point(position[i+1][0], position[i+1][1])
                point_three = shapely.geometry.Point(position[i+2][0], position[i+3][1])
                point_four = shapely.geometry.Point(position[i+4][0], position[i+4][1])
                if zone[travel_direction[0] + 'I'].intersects(point_one) and zone[travel_direction[0] + 'I'].intersects(point_two) and zone[travel_direction[1]].buffer(0.001).intersects(point_three) and zone[travel_direction[1]].buffer(0.001).intersects(point_four):
                    front_segment = position[0:i+2, :]
                    middle_segment = position[i+2:, :]
                    latter_segment = np.array([]).reshape(-1, 2)
                    sut_lose_efficacy = False
                    break
            else:
                point_one = shapely.geometry.Point(position[i][0], position[i][1])
                point_two = shapely.geometry.Point(position[i + 1][0], position[i + 1][1])
                if zone[travel_direction[0] + 'I'].intersects(point_one) and zone[travel_direction[1]].buffer(0.001).intersects(point_two):
                    front_segment = position[0:i+1, :]
                    middle_segment = position[i+1:, :]
                    latter_segment = np.array([]).reshape(-1, 2)
                    sut_lose_efficacy = False
                    break
        if front_segment is None:
            sut_lose_efficacy = True
    else:
        for i in range(position.shape[0]-1):
            point_one = shapely.geometry.Point(position[i][0], position[i][1])
            point_two = shapely.geometry.Point(position[i+1][0], position[i+1][1])
            if zone[travel_direction[0] + 'I'].intersects(point_one) and zone['IN'].buffer(0.001).intersects(point_two):
                front_segment = position[0:i+1, :]
                for j in range(i+1, position.shape[0]-1):
                    point_one = shapely.geometry.Point(position[j][0], position[j][1])
                    point_two = shapely.geometry.Point(position[j + 1][0], position[j + 1][1])
                    if zone['IN'].buffer(0.001).intersects(point_one) and zone[travel_direction[1] + 'O'].intersects(point_two):
                        middle_segment = position[i+1:j+1, :]
                        latter_segment = position[j+1:, :]
                        sut_lose_efficacy = False
                        break
        if front_segment is None or middle_segment is None or latter_segment is None:
            sut_lose_efficacy = True
    return front_segment, middle_segment, latter_segment, sut_lose_efficacy


if __name__ == "__main__":
    # print(([True, False, True, False] and [True, True, False, False]))
    x = list(range(1, 18))
    y = list([-5, -5, -5, -5, -5, -5, -5, -5, -3, -1, 2, 5, 7, 11, 14, 17, 19])
    stop_line = {"W": 10, "E": 20, "N": 15, "S": -15}
    travel_direction = ('W', 'N')
    a = 1
    if a < 2:
        print(2)
    elif a < 3:
        print(3)
    a = np.array([[1,2],[3,4],[5,6],[7,8]])
    b = pd.DataFrame(a)
    print(b.iloc[0:2])
    a = pd.Series([1,2,3])
    a[a>1] = 5
    print(a)
    for i in range(10):
        print(i)
        for j in range(5):
            print('inner')
            if j == 2:
                break
    """
    first_segment, second_segment, third_segment = segment_of_trajectory(x, y, stop_line, travel_direction)
    print("--------first_segment------------")
    print(first_segment)
    print(first_segment.shape)
    print("--------second_segment-----------------")
    print(second_segment)
    print(second_segment.shape)
    print("------------third_segment--------------")
    print(third_segment)
    print(third_segment.shape)
    a = ('a','b')
    print(a.count('a'))
    print(np.array([]).reshape(-1, 2))
    """


