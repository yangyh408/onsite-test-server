# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/10 21:23

import numpy as np


def zoning_first_id(entrance_road, exit_road):
    [WI, EI, NI, SI] = [[] for i in range(4)]
    [WO, EO, NO, SO] = [[] for i in range(4)]
    coordinate_list_in = []
    coordinate_list_out = []
    # 进入交叉口
    for i in entrance_road:
        (x, y), _ = i.planView.calc_geometry(0.1)
        coordinate_list_in.append((x, y))
    max_index = np.argmax(np.array(coordinate_list_in), axis=0)
    min_index = np.argmin(np.array(coordinate_list_in), axis=0)
    WI.append(entrance_road[min_index[0]])
    EI.append(entrance_road[max_index[0]])
    NI.append(entrance_road[max_index[1]])
    SI.append(entrance_road[min_index[1]])
    # 驶出交叉口
    for i in exit_road:
        (x, y), _ = i.planView.calc_geometry(0.1)
        coordinate_list_out.append((x, y))
    max_index = np.argmax(np.array(coordinate_list_out), axis=0)
    min_index = np.argmin(np.array(coordinate_list_out), axis=0)
    WO.append(exit_road[min_index[0]])
    EO.append(exit_road[max_index[0]])
    NO.append(exit_road[max_index[1]])
    SO.append(exit_road[min_index[1]])
    #print([WI, EI, NI, SI],[WO, EO, NO, SO])
    return [WI, EI, NI, SI], [WO, EO, NO, SO]


def zoning_other_id(in_, out_, outside_intersection_road):
    # for i in in_:
    #     print(i.id)
    # for idx_1 in in_:
    #     for idx_2 in idx_1:
    #         print(idx_2.id)
    # print(in_)
    for i in in_:
        #print(i[-1].link.successor)
        # if i[-1].link.successor:
        while i[-1].link.successor in outside_intersection_road:
              i.append(i[-1].link.successor)
    for i in out_:

        #if i[-1].link.successor:
        while i[-1].link.predecessor in outside_intersection_road:
            i.append(i[-1].link.predecessor)
    return in_, out_


if __name__ == "__main__":
    lis = [(5, 5), (10, 0), (15, 5), (10, 10)]
    max_index = np.argmax(np.array(lis), axis=0)
    min_index = np.argmin(np.array(lis), axis=0)
    print(max_index)
    print(min_index)
    print(lis.index((10, 0)))





