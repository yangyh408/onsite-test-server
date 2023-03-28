import os
import numpy as np
import pandas as pd
import xml.dom.minidom
import re
from onsite.controller import ReplayParser
#from evaluation_prepare.ego_and_forward_vehicle_relation import RelationJudgement



def parserzd(scenario_path):#判断匝道id和匝道起终点
    parser = ReplayParser()
    # 构造场景解析器
    replay_info = parser.parse(scenario_path)
    ##利用斜率判断哪条车道是匝道,以及匝道的终点x和y
    a=[]
    for i in range(0,np.shape(replay_info.road_info.discretelanes)[0]):
        x0=replay_info.road_info.discretelanes[i].center_vertices[0,0]
        y0=replay_info.road_info.discretelanes[i].center_vertices[0,1]
        x1=replay_info.road_info.discretelanes[i].center_vertices[-1,0]
        y1 = replay_info.road_info.discretelanes[i].center_vertices[-1, 1]
        a.append(abs((y1-y0)/(x1-x0)))
    amax=max(a)
    idnum=a.index(amax)
    zd_id=replay_info.road_info.discretelanes[idnum].lane_id
    desty=max(replay_info.road_info.discretelanes[idnum].left_vertices[:,1])
    destx=max(replay_info.road_info.discretelanes[idnum].left_vertices[:,0])
    #print(desty,destx)
    return replay_info,zd_id,destx,desty

scenario_path=r'D:\PycharmProjects\pythonProject\ramp\scenario\1cutin10'
parserzd(scenario_path)