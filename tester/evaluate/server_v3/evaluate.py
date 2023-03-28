from unittest import result
import pandas as pd
from tqdm import tqdm
from tqdm import trange
import os
import numpy as np
import math

def write_answerSheet(file_path,recording_path,start_destpath,scenario):
    '''
    生成标准答题卡，重点是前车信息的生成
    input：参赛者轨迹outputs、输出的标准答题卡路径
    output：标准答题卡
    '''
    outputs= pd.read_csv(file_path)
    df_recording = pd.read_csv(recording_path)# 各类场景信息
    highD_index = 0
    start_dest = pd.read_csv(start_destpath)
    start_dest = np.array(start_dest)
    num_scenario = np.shape(start_dest)[0]
    #file_path = file_path.split("\\")[-1]
    #scenario = file_path[0:-9]
    for i in range(0, num_scenario):
        if start_dest[i][0] == str(scenario):
            highD_index = start_dest[i][1]

    answersheet = pd.DataFrame(columns=["time","x_ego","y_ego","v_ego","yaw_ego","vx_ego","vy_ego","ax_ego","ay_ego","aax_ego","aay_ego","width_ego","length_ego","laneId"],index=None)
    answersheet['time']=outputs.iloc[:,0]
    answersheet['x_ego'] = outputs['x_ego']
    answersheet['y_ego'] = outputs['y_ego']
    answersheet['v_ego'] = outputs['v_ego']
    answersheet['yaw_ego'] = outputs['yaw_ego']

    vx_egodata=np.array(outputs.iloc[:,3])*np.cos(outputs.iloc[:,5])
    answersheet['vx_ego'] = pd.DataFrame(vx_egodata)
    vy_egodata=np.array(outputs.iloc[:,3])*np.sin(outputs.iloc[:,5])
    answersheet['vy_ego'] = pd.DataFrame(vy_egodata)
    # ax_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    # ay_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    #ax_egodata =[999 for x in range(0,np.shape(vx_egodata)[0])]
    #ay_egodata = [999 for x in range(0, np.shape(vx_egodata)[0])]
    # for i in range(0, np.shape(vx_egodata)[0] - 1):
    #     ax_egodata[i + 1] = (vx_egodata[i + 1] - vx_egodata[i]) / 0.04
    #     ay_egodata[i + 1] = (vy_egodata[i + 1] - vy_egodata[i]) / 0.04
    # answersheet['ax_ego'] = pd.DataFrame(ax_egodata)
    # answersheet['ay_ego'] = pd.DataFrame(ay_egodata)

    a_ego = outputs['a_ego']
    ax_egodata=np.array(a_ego)*np.cos(outputs.iloc[:,5])
    answersheet['ax_ego'] = pd.DataFrame(ax_egodata)
    ay_egodata = np.array(a_ego) * np.sin(outputs.iloc[:, 5])
    answersheet['ay_ego'] = pd.DataFrame(ay_egodata)
    aax_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    aay_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    for i in range(0, np.shape(vx_egodata)[0] - 1):
        aax_egodata[i + 1] = (ax_egodata[i + 1] - ax_egodata[i]) / 0.04
        aay_egodata[i + 1] = (ay_egodata[i + 1] - ay_egodata[i]) / 0.04
    answersheet['aax_ego'] = pd.DataFrame(aax_egodata)
    answersheet['aay_ego'] = pd.DataFrame(aay_egodata)
    answersheet['width_ego'] = outputs['width_ego']
    answersheet['length_ego'] = outputs['length_ego']
    y_ego = outputs['y_ego'].values.tolist()
    height=answersheet['width_ego'].values.tolist()[0]
    laneid = [] #判断主车车道，生成laneid
    for y in y_ego:
        upper_marking = str(df_recording[df_recording['id'] == int(highD_index)]['upperLaneMarkings'][
                                int(highD_index) - 1]).split(';')
        upper_marking = [float(i) for i in upper_marking]
        lower_marking = str(df_recording[df_recording['id'] == int(highD_index)]['lowerLaneMarkings'][
                                int(highD_index) - 1]).split(';')
        lower_marking = [float(i) for i in lower_marking]
        y_bias = upper_marking[-1] + \
                 (lower_marking[0] - upper_marking[-1]) / 2
        y_highD = y_bias - y   # 将车辆纵坐标还原至HighD坐标系
        temp = upper_marking + lower_marking
        temp.append(y_highD)
        temp.sort()
        if len(upper_marking) == 3:  # 双车道场景
            if temp.index(y_highD) == 1:
                laneid.append(2)
            elif temp.index(y_highD) == 2:
                laneid.append(3)
            elif temp.index(y_highD) == 4:
                laneid.append(5)
            elif temp.index(y_highD) == 5:
                laneid.append(6)
            else:  # 驶出行车道
                laneid.append(-999)
        elif len(upper_marking) == 4:  # 三车道场景
            if temp.index(y_highD) == 1:
                laneid.append(2)
            elif temp.index(y_highD) == 2:
                laneid.append(3)
            elif temp.index(y_highD) == 3:
                laneid.append(4)
            elif temp.index(y_highD) == 5:
                laneid.append(6)
            elif temp.index(y_highD) == 6:
                laneid.append(7)
            elif temp.index(y_highD) == 7:
                laneid.append(8)
            else:
                laneid.append(-999)
        else:  # 4+3场景
            if temp.index(y_highD) == 1:
                laneid.append(2)
            elif temp.index(y_highD) == 2:
                laneid.append(3)
            elif temp.index(y_highD) == 3:
                laneid.append(4)
            elif temp.index(y_highD) == 4:
                laneid.append(5)
            elif temp.index(y_highD) == 6:
                laneid.append(7)
            elif temp.index(y_highD) == 7:
                laneid.append(8)
            elif temp.index(y_highD) == 8:
                laneid.append(9)
            else:
                laneid.append(-999)  #
    answersheet['laneId'] = pd.DataFrame(laneid)

    #处理非主车数据：重点是判断laneid
    nonego=outputs.iloc[:,8:-1]
    nonego_arr=np.array(nonego)
    num_nonego=(np.shape(nonego_arr)[1])//7
    for i in range(1,num_nonego+1):
        y_nonego = nonego.iloc[:,7*i-6]
        y_nonego = y_nonego.values.tolist()
        laneid_nonego = []
        for y in y_nonego:
            upper_marking = str(df_recording[df_recording['id'] == int(highD_index)]['upperLaneMarkings'][
                                    int(highD_index) - 1]).split(';')
            upper_marking = [float(i) for i in upper_marking]
            lower_marking = str(df_recording[df_recording['id'] == int(highD_index)]['lowerLaneMarkings'][
                                    int(highD_index) - 1]).split(';')
            lower_marking = [float(i) for i in lower_marking]
            y_bias = upper_marking[-1] + \
                     (lower_marking[0] - upper_marking[-1]) / 2
            y_highD = y_bias - y  # 将车辆纵坐标还原至HighD坐标系
            temp = upper_marking + lower_marking
            temp.append(y_highD)
            temp.sort()
            if len(upper_marking) == 3:  # 双车道场景
                if temp.index(y_highD) == 1:
                    laneid_nonego.append(2)
                elif temp.index(y_highD) == 2:
                    laneid_nonego.append(3)
                elif temp.index(y_highD) == 4:
                    laneid_nonego.append(5)
                elif temp.index(y_highD) == 5:
                    laneid_nonego.append(6)
                else:  # 驶出行车道
                    laneid_nonego.append(-999)
            elif len(upper_marking) == 4:  # 三车道场景
                if temp.index(y_highD) == 1:
                    laneid_nonego.append(2)
                elif temp.index(y_highD) == 2:
                    laneid_nonego.append(3)
                elif temp.index(y_highD) == 3:
                    laneid_nonego.append(4)
                elif temp.index(y_highD) == 5:
                    laneid_nonego.append(6)
                elif temp.index(y_highD) == 6:
                    laneid_nonego.append(7)
                elif temp.index(y_highD) == 7:
                    laneid_nonego.append(8)
                else:
                    laneid_nonego.append(-999)
            else:  # 4+3场景
                if temp.index(y_highD) == 1:
                    laneid_nonego.append(2)
                elif temp.index(y_highD) == 2:
                    laneid_nonego.append(3)
                elif temp.index(y_highD) == 3:
                    laneid_nonego.append(4)
                elif temp.index(y_highD) == 4:
                    laneid_nonego.append(5)
                elif temp.index(y_highD) == 6:
                    laneid_nonego.append(7)
                elif temp.index(y_highD) == 7:
                    laneid_nonego.append(8)
                elif temp.index(y_highD) == 8:
                    laneid_nonego.append(9)
                else:
                    laneid_nonego.append(-999)
        laneid_nonego=pd.DataFrame(laneid_nonego)
        nonego=pd.concat([nonego,laneid_nonego],axis=1)

    #筛选主车的近邻前车
    x_ego=answersheet['x_ego'].values.tolist()
    nonego=nonego.values.tolist()
    pre_x=[]
    pre_y=[]
    pre_v=[]
    pre_yaw=[]
    pre_width=[]
    pre_length=[]
    if np.shape(x_ego)[0]>1:
       if x_ego[0]<x_ego[1]: #下行方向
        for t in range(0,np.shape(vx_egodata)[0]):
           distance = []
           for i in range(0,num_nonego-1):
              distance.append(nonego[t][7*i]-x_ego[t])
              if distance[i]<0 or laneid[t]!=nonego[t][7*num_nonego+i]:
                distance[i]=9999
           if distance:
               pre_index=distance.index(min(distance))
               if distance[pre_index]==9999:
                  pre_x.append(-9999)
                  pre_y.append(-9999)
                  pre_v.append(-9999)
                  pre_yaw.append(-9999)
                  pre_width.append(-9999)
                  pre_length.append(-9999)
               else:
                  pre_x.append(nonego[t][7*pre_index])
                  pre_y.append(nonego[t][7*pre_index+1])
                  pre_v.append(nonego[t][7*pre_index+2])
                  pre_yaw.append(nonego[t][7*pre_index+4])
                  pre_width.append(nonego[t][7*pre_index+5])
                  pre_length.append(nonego[t][7*pre_index+6])
           else:
               pre_x.append(-9999)
               pre_y.append(-9999)
               pre_v.append(-9999)
               pre_yaw.append(-9999)
               pre_width.append(-9999)
               pre_length.append(-9999)
       else: #上行方向
        for t in range(0, np.shape(vx_egodata)[0] ):
            distance = []
            for i in range(0, num_nonego - 1):
                distance.append(-nonego[t][7 * i] + x_ego[t])
                if distance[i] < 0 or laneid[t]!=nonego[t][7*num_nonego+i]:
                    distance[i] = 9999
            if distance:
                pre_index = distance.index(min(distance))
                if distance[pre_index] == 9999:
                    pre_x.append(-9999)
                    pre_y.append(-9999)
                    pre_v.append(-9999)
                    pre_yaw.append(-9999)
                    pre_width.append(-9999)
                    pre_length.append(-9999)
                else:
                    pre_x.append(nonego[t][7 * pre_index])
                    pre_y.append(nonego[t][7 * pre_index + 1])
                    pre_v.append(nonego[t][7 * pre_index + 2])
                    pre_yaw.append(nonego[t][7 * pre_index + 4])
                    pre_width.append(nonego[t][7 * pre_index + 5])
                    pre_length.append(nonego[t][7 * pre_index + 6])
            else:
                pre_x.append(-9999)
                pre_y.append(-9999)
                pre_v.append(-9999)
                pre_yaw.append(-9999)
                pre_width.append(-9999)
                pre_length.append(-9999)
    else:
        for t in range(0, np.shape(vx_egodata)[0]):
           pre_x.append(-9999)
           pre_y.append(-9999)
           pre_v.append(-9999)
           pre_yaw.append(-9999)
           pre_width.append(-9999)
           pre_length.append(-9999)

    #把前车信息写入answersheet
    pre_x=pd.DataFrame(pre_x)
    pre_y = pd.DataFrame(pre_y)
    pre_v = pd.DataFrame(pre_v)
    pre_yaw = pd.DataFrame(pre_yaw)
    pre_width = pd.DataFrame(pre_width)
    pre_length = pd.DataFrame(pre_length)
    col_name = answersheet.columns.tolist()
    col_name.append('x_pre')
    col_name.append('y_pre')
    col_name.append('v_pre')
    col_name.append('yaw_pre')
    col_name.append('vx_pre')
    col_name.append('vy_pre')
    col_name.append('width_pre')
    col_name.append('length_pre')
    col_name.append('lanenum')
    col_name.append('reward')
    answersheet= answersheet.reindex(columns=col_name)
    answersheet['x_pre']=pre_x
    answersheet['y_pre'] = pre_y
    answersheet['v_pre'] = pre_v
    answersheet['yaw_pre'] = pre_yaw
    pre_x = np.array(pre_x)
    pre_y = np.array(pre_y)
    vx_predata = np.zeros(shape=(np.shape(pre_x)[0], 1))
    vy_predata = np.zeros(shape=(np.shape(pre_y)[0], 1))
    lane_num = np.zeros(shape=(np.shape(pre_x)[0], 1))
    for i in range(0, np.shape(pre_x)[0] - 1):
        vx_predata[i + 1] = (pre_x[i + 1] - pre_x[i]) / 0.04
        vy_predata[i + 1] = (pre_y[i + 1] - pre_y[i]) / 0.04
    for i in range(0, np.shape(pre_x)[0] ):
        lane_num[i]=len(upper_marking)
    #vx_predata=np.array(pre_v.iloc[:,0])*np.cos(pre_yaw.iloc[:,0])
    answersheet['vx_pre'] = pd.DataFrame(vx_predata)
    #vy_predata=np.array(pre_v.iloc[:,0])*np.sin(pre_yaw.iloc[:,0])
    answersheet['vy_pre'] = pd.DataFrame(vy_predata)
    answersheet['width_pre'] = pre_width
    answersheet['length_pre'] = pre_length
    answersheet['lanenum']=pd.DataFrame(lane_num)
    answersheet['reward'] = outputs['end']

    #导出answersheet.csv
    #answersheet.to_csv("answersheet.csv", index=False)
    # print(answersheet)
    return answersheet

def Evaluation(list_HAV,start_destpath,scenario,area=5,safety=50,efficiency=30,comfort=20,dt=0.04,output_type='details'):
    #读取起终点
    start=0
    destination=0
    start_dest=pd.read_csv(start_destpath)
    start_dest=np.array(start_dest)
    num_scenario=np.shape(start_dest)[0]
    #file1_path = file_path.split("\\")[-1]
    #scenario = file1_path[0:-9]
    for i in range(0,num_scenario):
       if start_dest[i][0]==str(scenario):
           start=start_dest[i][2]
           destination=start_dest[i][3]
    if start < destination:
        dest = destination - area  # 设置终点范围
    else:
        dest = destination + area

    #到达终点之前的片段提取（也可取消）
    if start > dest:
        List_HAV = list_HAV[list_HAV[:, 1] > dest, :]
    else:
        List_HAV = list_HAV[list_HAV[:, 1] < dest, :]
    # 安全得分
    reward=np.array(list_HAV)[:, -1]
    List_HAVx = List_HAV[:, 1]
    HAVx_num = np.shape(List_HAVx)[0]
    mean_TTC = 0
    lane_ornot = 0
    lanenum = List_HAV[1, -2]
    lanestart = List_HAV[1, 13]
    lanerror = []
    List_HAVlane=[]
    if (2 in reward) or (3 in reward):  # 碰撞0分
        score_safe = 0
    else:
        List_HAV0 = List_HAV[List_HAV[:, 14] > -999, :]
        if np.shape(List_HAV0)[0] == 0:
            score_safe = 50
        else:  # TTC<1扣分
            if min(abs(List_HAV0[:, 14] - List_HAV0[:, 1])) > 5:
                TTC_HAV = (List_HAV0[:, 14] - List_HAV0[:, 1]) / (
                            List_HAV0[:, 5] - List_HAV0[:, 18])
                TTC_HAV = TTC_HAV[TTC_HAV > 0]
                if len(TTC_HAV) != 0:
                    mean_TTC = sum(TTC_HAV) / len(TTC_HAV)
                TTC_HAV = TTC_HAV[TTC_HAV < 1]
                score_safe = safety - np.shape(TTC_HAV)[0] / np.shape(List_HAV)[0] * safety
            else:
                score_safe = 0
        List_HAVlane = List_HAV[:, 13].tolist()  # 驶出行车道扣分
        lane999_num = List_HAVlane.count(-999)
        if lane999_num > 0:
            lane_ornot = 1
            score_safe = score_safe - 50*lane999_num/np.shape(List_HAV)[0]

        #驶入对向车道扣分
        if lanenum==3:
            if lanestart<4:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]>4 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
            else:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]<4 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
                        #print("yes")
        elif lanenum==4:
            if lanestart<5:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]>5 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
            else:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]<5 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
        else:
            if lanestart<6:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]>6 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
            else:
                for i in range(0,np.shape(List_HAV)[0]):
                    if List_HAVlane[i]<6 and List_HAVlane[i]!=-999:
                        lanerror.append(i)
        # if np.shape(lanerror)[0]>0:
        #     print("驶入对向车道")
        score_safe=score_safe-25*np.shape(lanerror)[0]/np.shape(List_HAV)[0]
        score_safe = min(50, score_safe)
        score_safe = max(0, score_safe)



    HAV = list_HAV[:, 1]
    start_HAV = List_HAV[0, 1]
    dest_HAV = list_HAV[-1, 1]
    distance_HAV = abs(start_HAV - dest_HAV)
    distance_tar=abs(start-dest)
    time_cost = distance_HAV /33.33

    if start > dest:
        if dest_HAV > dest:
            done_ornot = 1
            distance_todest = dest_HAV - dest
            score_efficiency1 = min(10, 10 * distance_HAV / distance_tar)
        else:
            done_ornot = 0
            distance_todest = 0
            score_efficiency1 = 10
    else:
        if dest_HAV < dest:
            done_ornot = 1
            distance_todest = dest - dest_HAV
            score_efficiency1 = min(10, 10 * distance_HAV / distance_tar)
        else:
            score_efficiency1 = 10
            done_ornot = 0
            distance_todest = 0
        # print("距离：",distance_todest)
    time_cost_HAV = np.shape(HAV)[0] * dt
    score_efficiency2 = min(20, time_cost / time_cost_HAV * efficiency)
    score_efficiency = min(efficiency, score_efficiency1 + score_efficiency2)
    mean_vy = abs(sum(List_HAV[:, 5]) / len(List_HAV[:, 5]))

    # comfortable
    UncomfortAcc = List_HAV[List_HAV[:, 7] > 3, 7]
    UncomfortDec = List_HAV[List_HAV[:, 7] < -3, 7]
    UncomfortAcc_lateral = List_HAV[List_HAV[:, 8] > 0.5, 8]
    UncomfortDec_lateral = List_HAV[List_HAV[:, 8] < -0.5, 8]
    UncomfortAAcc = List_HAV[List_HAV[:, 9] > 6, 9]
    UncomfortDDec = List_HAV[List_HAV[:, 9] < -6, 9]
    UncomfortAAcc_lateral = List_HAV[List_HAV[:, 10] > 1, 10]
    UncomfortDDec_lateral = List_HAV[List_HAV[:, 10] < -1, 10]

    Uncomfort_num = np.shape(UncomfortAcc)[0] + np.shape(UncomfortDec)[0]
    Uncomfort_numlateral = np.shape(UncomfortAcc_lateral)[0] + np.shape(UncomfortDec_lateral)[0]
    Uncomfort_numAAcc = np.shape(UncomfortAAcc)[0] + np.shape(UncomfortDDec)[0]
    Uncomfort_numlateralAAcc = np.shape(UncomfortAAcc_lateral)[0] + np.shape(UncomfortDDec_lateral)[0]
    all_num = np.shape(List_HAV)[0]
    score_comfort = comfort - Uncomfort_num / all_num * 5 - Uncomfort_numlateral / all_num * 5 - Uncomfort_numAAcc / all_num * 5 - Uncomfort_numlateralAAcc / all_num * 5
    score_comfort = max(0, score_comfort)
    score_comfort = min(comfort, score_comfort)

    ##增加规控器失效判断
    v_yaw = np.zeros(shape=(np.shape(List_HAV)[0], 1))
    for i in range(0, np.shape(List_HAV)[0] - 1):
        v_yaw[i + 1] = abs((List_HAV[i + 1, 4] - List_HAV[i, 4]) / 0.04)
    v_yaw = v_yaw[v_yaw > 500]
    if start > dest:
        v_err = List_HAV[List_HAV[:, 5] > 1, 5]
    else:
        v_err = List_HAV[List_HAV[:, 5] < -1, 5]
    # print(np.shape(v_err)[0])
    if (np.shape(v_yaw)[0] != 0) or (len(List_HAV[abs(List_HAV[:, 7]) > 200, 7]) != 0) or (
            len(List_HAV[abs(List_HAV[:, 8]) > 200, 8]) != 0) or (np.shape(List_HAV)[0] == 1) or (
            np.shape(v_err)[0] != 0):
        score_safe = 0
        score_efficiency = 0
        score_comfort = 0


    if len(List_HAV[List_HAV[:, 7] > 0, 7]) != 0:
        mean_ACCx = sum(List_HAV[List_HAV[:, 7] > 0, 7]) / len(List_HAV[List_HAV[:, 7] > 0, 7])
    else:
        mean_ACCx = 0
    if len(List_HAV[List_HAV[:, 7] < 0, 7]) != 0:
        mean_DECx = sum(List_HAV[List_HAV[:, 7] < 0, 7]) / len(List_HAV[List_HAV[:, 7] < 0, 7])
    else:
        mean_DECx = 0
    if len(List_HAV[List_HAV[:, 8] > 0, 8]) != 0:
        mean_ACCy = sum(List_HAV[List_HAV[:, 8] > 0, 8]) / len(List_HAV[List_HAV[:, 8] > 0, 8])
    else:
        mean_ACCy = 0
    if len(List_HAV[List_HAV[:, 8] < 0, 8]) != 0:
        mean_DECy = sum(List_HAV[List_HAV[:, 8] < 0, 8]) / len(List_HAV[List_HAV[:, 8] < 0, 8])
    else:
        mean_DECy = 0

    if len(List_HAV[List_HAV[:, 9] > 0, 9]) != 0:
        mean_AACCx = sum(List_HAV[List_HAV[:, 9] > 0, 9]) / len(List_HAV[List_HAV[:, 9] > 0, 9])
    else:
        mean_AACCx = 0
    if len(List_HAV[List_HAV[:, 9] < 0, 9]) != 0:
        mean_DDECx = sum(List_HAV[List_HAV[:, 9] < 0, 9]) / len(List_HAV[List_HAV[:, 9] < 0, 9])
    else:
        mean_DDECx = 0
    if len(List_HAV[List_HAV[:, 10] > 0, 10]) != 0:
        mean_AACCy = sum(List_HAV[List_HAV[:, 10] > 0, 10]) / len(List_HAV[List_HAV[:, 10] > 0, 10])
    else:
        mean_AACCy = 0
    if len(List_HAV[List_HAV[:, 10] < 0, 10]) != 0:
        mean_DDECy = sum(List_HAV[List_HAV[:, 10] < 0, 10]) / len(List_HAV[List_HAV[:, 10] < 0, 10])
    else:
        mean_DDECy = 0

    #分数输出
    if output_type == 'default':
        score = score_safe + score_efficiency + score_comfort
        return ([score,score_safe,score_efficiency,score_comfort])
    elif output_type == 'details':
        return ( [score_safe + score_efficiency + score_comfort, score_safe, score_efficiency, score_comfort,lane_ornot,done_ornot,distance_todest,mean_TTC,mean_vy,\
                mean_ACCx,mean_DECx,mean_ACCy,mean_DECy,mean_AACCx,mean_DDECx,mean_AACCy,mean_DDECy])
    else:
        raise AttributeError("output_type do not accept!")




class Evaluator:
    def __init__(self,outputs_path,database):
        self.outputs_path = outputs_path
        self.database = database
    def evaluate(self, output_type='default'):
        all_score = []
        all_scenarios = []
        output_files = list(os.listdir(self.outputs_path))
        for i in trange(len(output_files)):
            # 跳过日志文件
            file = output_files[i]
            if file.split('.')[-1] == 'txt':
                continue
            scenario = file[:-11]
            file_path = os.path.join(self.outputs_path, file)
            recording_path = self.database + '/recording.csv'
            start_destpath = self.database + '/start_dest.csv'
            #answersheet_path = os.path.join("answersheet/"+str(scenario)+"_answer.csv" )
            #if ~('answerSheet.csv' in files): ##修改
            answersheet=write_answerSheet(file_path,recording_path,start_destpath,scenario)
            list_HAV = answersheet.values
            list_HAV = np.array(list_HAV)
            list_HAV = list_HAV.astype(np.float64)
            score = Evaluation(list_HAV,start_destpath,scenario,area=5,safety=50,efficiency=30,comfort=20,dt=0.04,output_type=output_type)
            # print('score', score)
            all_score.append(score)
            all_scenarios.append(scenario)

        if output_type == 'default':
            return np.array(all_score)
        elif output_type == 'details':
            return all_scenarios, np.array(all_score)

if __name__ == '__main__':
     eva = Evaluator(r"C:\Users\Administrator\Desktop\实验\outputs_v2","./database")
     score = eva.evaluate()
     print(score)
    # file_path=r"C:\Users\Administrator\Desktop\实验\outputs_v2\0000follow1_result.csv"
    # recording_path=r"D:\PycharmProjects\pythonProject\server_v3\database\recording.csv"
    # start_destpath=r"D:\PycharmProjects\pythonProject\server_v3\database\start_dest.csv"
    # scenario="0000follow1"
    # answersheet=write_answerSheet(file_path, recording_path, start_destpath, scenario)
    # print(answersheet)
