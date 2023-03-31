import os
import numpy as np
import pandas as pd
import xml.dom.minidom
import re
from onsite.controller import ReplayParser
from evaluation_prepare.ego_and_forward_vehicle_relation import RelationJudgement
from tqdm import trange
from onsite.scenarioOrganizer import ScenarioOrganizer
from opendrive2discretenet.network import Network
from lxml import etree
from opendrive2discretenet.opendriveparser.parser import parse_opendrive

def parse_openScenario(path_openScenario):##读取试题起终点信息
    """
    解析openScenario地图信息，存储到self.info.openScenario_info
    :param scenario_path: 存放比赛试题的文件位置
    :return:
    """
    #scenario_file = scenario_path
    #path_openScenario = r'C:\Users\Administrator\Desktop\ramp\scenario\1cutin10\1cutin10_exam.xosc'
    opens = xml.dom.minidom.parse(path_openScenario).documentElement
    openScenario_info={}
    # 读取主车起点信息
    ego_node = opens.getElementsByTagName('Private')[0]
    ego_init = ego_node.childNodes[3].data
    ego_v, ego_x, ego_y, ego_head = [
        float(i.split('=')[1]) for i in ego_init.split(',')]
    for key, value in zip(["initial_x", "initial_y"], [ego_x, ego_y]):
        openScenario_info[key] = value
    #读取主车终点信息
    goal_init = ego_node.childNodes[5].data
    goal = [float(i) for i in re.findall('-*\d+\.\d+', goal_init)]
    for key, value in zip(["goal_x", "goal_y"], [goal[:2], goal[2:]]):
        openScenario_info[key] = value
    return openScenario_info

def parserzd(scenario_path):#判断匝道id和匝道起终点
    parser = ReplayParser()
    # 构造场景解析器
    
    # so = ScenarioOrganizer()
    # so.load(demo_input_dir, demo_output_dir)
    # scenario_to_test = so.next()

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
    desty_left=max(replay_info.road_info.discretelanes[idnum].left_vertices[:,1])
    destx_left=max(replay_info.road_info.discretelanes[idnum].left_vertices[:,0])
    desty_right=max(replay_info.road_info.discretelanes[idnum].right_vertices[:,1])
    destx_right=max(replay_info.road_info.discretelanes[idnum].right_vertices[:,0])
    #print(desty,destx)
    return replay_info,zd_id,destx_left,desty_left,destx_right,desty_right


def parserd_v2(scenario_path):
    #scenario_file = r'D:\PycharmProjects\pythonProject\ramp\scenariov2\2cutin97'
    path_openDrive = None
    try:
        for file in os.listdir(scenario_path):
            if '.xodr' in file:
                path_openDrive = os.path.join(scenario_path, file)
        assert path_openDrive is not None
    except FileNotFoundError:
        raise FileNotFoundError("未找到对应的openDrive地图文件，请检查路径是否正确")
    fh = open(path_openDrive, "r")
    root = etree.ElementTree(file=path_openDrive).getroot()
    open_drive_xml = parse_opendrive(etree.parse(fh).getroot())
    fh.close()
    loadedRoadNetwork = Network()
    loadedRoadNetwork.load_opendrive(open_drive_xml)
    open_drive_info = loadedRoadNetwork.export_discrete_network(
        filter_types=["driving", "onRamp", "offRamp", "exit", "entry"])
    #print(open_drive_info.discretelanes)
    i = 0
    a = []
    laneid = []
    for discrete_lane in open_drive_info.discretelanes:
        x0 = discrete_lane.center_vertices[0, 0]
        y0 = discrete_lane.center_vertices[0, 1]
        x1 = discrete_lane.center_vertices[-1, 0]
        y1 = discrete_lane.center_vertices[-1, 1]
        a.append(abs((y1 - y0) / (x1 - x0)))
        laneid.append(discrete_lane.lane_id)
    amax = max(a)
    idnum = a.index(amax)
    zdid = laneid[idnum]
    desty_left = max(open_drive_info.discretelanes[idnum].left_vertices[:, 1])
    destx_left = max(open_drive_info.discretelanes[idnum].left_vertices[:, 0])
    desty_right = max(open_drive_info.discretelanes[idnum].right_vertices[:, 1])
    destx_right = max(open_drive_info.discretelanes[idnum].right_vertices[:, 0])
    return  open_drive_info,zdid,destx_left,desty_left,destx_right,desty_right

def write_answersheet_ramp(outputs_path,scenario_path):
##生成主车信息
    replay_info,zd_id,destx_left,desty_left,destx_right,desty_right=parserd_v2(scenario_path)
    trajectory=pd.read_csv(outputs_path)
    answersheet=pd.DataFrame()
    x_ego=np.array(trajectory['x_ego'])
    y_ego=np.array(trajectory['y_ego'])
    laneid_ego=np.zeros(shape=(np.shape(x_ego)[0], 1)).astype(np.str_)
    for i in range(0,np.shape(x_ego)[0]):
        for discrete_lane in replay_info.discretelanes:
            vert_x, vert_y = RelationJudgement.sampling_from_vertices_inside_intersection(discrete_lane, 5)
            if RelationJudgement.pnpoly(len(vert_x), vert_x, vert_y, x_ego[i], y_ego[i]):
               laneid_ego[i]=discrete_lane.lane_id
    answersheet['time']=trajectory.iloc[:,0]
    answersheet['x_ego']=trajectory['x_ego']
    answersheet['y_ego']=trajectory['y_ego']
    answersheet['v_ego'] = trajectory['v_ego']
    answersheet['yaw_ego'] = trajectory['yaw_ego']
    vx_egodata=np.array(trajectory.iloc[:,3])*np.cos(trajectory.iloc[:,5])
    answersheet['vx_ego'] = pd.DataFrame(vx_egodata)
    vy_egodata=np.array(trajectory.iloc[:,3])*np.sin(trajectory.iloc[:,5])
    answersheet['vy_ego'] = pd.DataFrame(vy_egodata)
    # ax_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    # ay_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    # for i in range(0, np.shape(vx_egodata)[0] - 1):
    #     ax_egodata[i + 1] = (vx_egodata[i + 1] - vx_egodata[i]) / 0.1
    #     ay_egodata[i + 1] = (vy_egodata[i + 1] - vy_egodata[i]) / 0.1
    # answersheet['ax_ego'] = pd.DataFrame(ax_egodata)
    # answersheet['ay_ego'] = pd.DataFrame(ay_egodata)
    a_ego = trajectory['a_ego']
    ax_egodata = np.array(a_ego) * np.cos(trajectory.iloc[:, 5])
    answersheet['ax_ego'] = pd.DataFrame(ax_egodata)
    ay_egodata = np.array(a_ego) * np.sin(trajectory.iloc[:, 5])
    answersheet['ay_ego'] = pd.DataFrame(ay_egodata)

    aax_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    aay_egodata = np.zeros(shape=(np.shape(vx_egodata)[0], 1))
    for i in range(0, np.shape(vx_egodata)[0] - 1):
        aax_egodata[i + 1] = (ax_egodata[i + 1] - ax_egodata[i]) / 0.1
        aay_egodata[i + 1] = (ay_egodata[i + 1] - ay_egodata[i]) / 0.1
    answersheet['aax_ego'] = pd.DataFrame(aax_egodata)
    answersheet['aay_ego'] = pd.DataFrame(aay_egodata)
    answersheet['width_ego'] = trajectory['width_ego']
    answersheet['length_ego'] = trajectory['length_ego']
    y_ego = trajectory['y_ego'].values.tolist()
    height=answersheet['width_ego'].values.tolist()[0]
    answersheet['laneId'] = pd.DataFrame(laneid_ego)


    ##判断背景车车道
    nonego=trajectory.iloc[:,8:-1]
    nonego_arr=np.array(nonego)
    num_nonego=(np.shape(nonego_arr)[1])//7
    for i in range(1,num_nonego+1):
        x_nonego = nonego.iloc[:, 7 * i - 7]
        y_nonego = nonego.iloc[:,7*i-6]
        x_nonego = x_nonego.values.tolist()
        y_nonego = y_nonego.values.tolist()
        laneid_nonego = np.zeros(shape=(np.shape(x_ego)[0], 1)).astype(np.str_)
        for m in range(0, np.shape(x_ego)[0]):
            for discrete_lane in replay_info.discretelanes:
                # print(discrete_lane.lane_id)
                vert_x, vert_y = RelationJudgement.sampling_from_vertices_inside_intersection(discrete_lane, 5)
                if RelationJudgement.pnpoly(len(vert_x), vert_x, vert_y, x_nonego[m], y_nonego[m]):
                    laneid_nonego[m]=(discrete_lane.lane_id)
        laneid_nonego = pd.DataFrame(laneid_nonego)
        nonego = pd.concat([nonego, laneid_nonego], axis=1)
    #print(nonego)
    nonego.to_csv("nonego.csv")

    nonego = nonego.values.tolist()
    pre_x = []
    pre_y = []
    pre_v = []
    pre_yaw = []
    pre_width = []
    pre_length = []
    if np.shape(x_ego)[0] > 1:
        for t in range(0, np.shape(vx_egodata)[0]):
            distance = []
            for i in range(0, num_nonego ):
                distance.append(nonego[t][7 * i] - x_ego[t])
                if distance[i] < 0 or laneid_ego[t] != nonego[t][7 * num_nonego + i]:
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

    # 把前车信息写入answersheet
    pre_x = pd.DataFrame(pre_x)
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
    col_name.append('reward')
    answersheet = answersheet.reindex(columns=col_name)
    answersheet['x_pre'] = pre_x
    answersheet['y_pre'] = pre_y
    answersheet['v_pre'] = pre_v
    answersheet['yaw_pre'] = pre_yaw
    pre_x = np.array(pre_x)
    pre_y = np.array(pre_y)
    vx_predata = np.zeros(shape=(np.shape(pre_x)[0], 1))
    vy_predata = np.zeros(shape=(np.shape(pre_y)[0], 1))
    for i in range(0, np.shape(pre_x)[0] - 1):
        vx_predata[i + 1] = (pre_x[i + 1] - pre_x[i]) / 0.1
        vy_predata[i + 1] = (pre_y[i + 1] - pre_y[i]) / 0.1
    # vx_predata=np.array(pre_v.iloc[:,0])*np.cos(pre_yaw.iloc[:,0])
    answersheet['vx_pre'] = pd.DataFrame(vx_predata)
    # vy_predata=np.array(pre_v.iloc[:,0])*np.sin(pre_yaw.iloc[:,0])
    answersheet['vy_pre'] = pd.DataFrame(vy_predata)
    answersheet['width_pre'] = pre_width
    answersheet['length_pre'] = pre_length
    answersheet['reward'] = trajectory['end']


    return answersheet


def Evaluation_ramp(list_HAV,scenario,scenario_path,safety=50,efficiency=30,comfort=20,dt=0.1,output_type='default'):
    # 读取起终点
    replay_info, zd_id, destx_left,desty_left,destx_right,desty_right = parserd_v2(scenario_path)
    path_openScenario=os.path.join(scenario_path+"/"+scenario+"_exam.xosc")
    openScenario_info = parse_openScenario(path_openScenario)
    goal_x = openScenario_info['goal_x'][0]
    goal_y = openScenario_info['goal_y'][0]
    destinationid=""
    for discrete_lane in replay_info.discretelanes:
        vert_x, vert_y = RelationJudgement.sampling_from_vertices_inside_intersection(discrete_lane, 5)
        if RelationJudgement.pnpoly(len(vert_x), vert_x, vert_y,  goal_x, goal_y):
            destinationid = discrete_lane.lane_id



    destinationx = goal_x
    destinationy = goal_y
    list_HAV1=list_HAV[:,:13].astype(np.float64)
    list_HAV3=list_HAV[:,14:].astype(np.float64)
    list_HAV2=list_HAV[:,13]
    list_HAV=np.hstack((list_HAV1,list_HAV3))
    #print(np.shape(list_HAV))
    # 安全得分
    reward=np.array(list_HAV)[:, -1]
    mean_TTC = 0
    lane_ornot = 0
    TTC_HAV=[]
    if (2 in reward) or (3 in reward):  # 碰撞0分
        score_safe = 0
    else:
        List_HAV0 = list_HAV[list_HAV[:, 13] > -9999, :]
        list_HAV2_nopre=list_HAV2[list_HAV[:, 13] > -9999]
        if np.shape(List_HAV0)[0] == 0:
            score_safe = 50
        else:  # TTC<1扣分
            for i in range(0,np.shape(List_HAV0)[0]):
                if list_HAV2_nopre[i]!=zd_id:
                    TTC_HAVi = (List_HAV0[i, 13] - List_HAV0[i, 1]) / (
                                List_HAV0[i, 5] - List_HAV0[i, 17])
                else:
                    TTC_HAVi = ((List_HAV0[i, 14] - List_HAV0[i, 2])**2+(List_HAV0[i, 13] - List_HAV0[i, 1])**2)**0.5 / (
                                abs(List_HAV0[i, 3]) - abs(List_HAV0[i, 15]))
                TTC_HAV.append(TTC_HAVi)
            if len(TTC_HAV) != 0:
                mean_TTC = sum(TTC_HAV) / len(TTC_HAV)
            TTC_HAV=np.array(TTC_HAV)
            TTC_HAV = TTC_HAV[TTC_HAV > 0]
            TTC_HAV = TTC_HAV[TTC_HAV < 1]
            score_safe = safety - np.shape(TTC_HAV)[0] / np.shape(list_HAV)[0] * safety


        List_HAVlane = list_HAV2.tolist()  # 驶出行车道扣分
        lane999_num = List_HAVlane.count('0.0')
        if lane999_num > 0:
            lane_ornot = 1
            score_safe = score_safe - 50*lane999_num/np.shape(list_HAV)[0]
        score_safe = min(50, score_safe)
        score_safe = max(0, score_safe)
        out_lane_rate=lane999_num/np.shape(list_HAV)[0]
        oppo_lane_rate=0
        run_red=0



   ##效率得分
    HAV = list_HAV[:, 1]
    dest_HAVx = list_HAV[-1, 1]
    dest_HAVy=list_HAV[-1, 2]
    dest_HAVid=list_HAV2[-1]
    distance_HAV=0
    for i in range(0,np.shape(list_HAV)[0]-1):
        dis=((list_HAV[i+1, 1]-list_HAV[i, 1])**2+(list_HAV[i+1, 2]-list_HAV[i, 2])**2)**0.5
        distance_HAV=distance_HAV+dis
    time_cost = distance_HAV /33.33

    if dest_HAVx >= destinationx  and dest_HAVid==destinationid:
        score_efficiency1 = 15
        done_ornot = 0
        distance_todest = 0
    else:
        score_efficiency1 = 0
        done_ornot = 1
        distance_todest = ((destinationx - dest_HAVx) ** 2 + (destinationy - dest_HAVy) ** 2) ** 0.5
    #print(dest_HAVx,dest_HAVy,destinationx,destinationy)
    time_cost_HAV = np.shape(HAV)[0] * dt
    score_efficiency2 = min(15, time_cost / time_cost_HAV * 15)
    score_efficiency = min(efficiency, score_efficiency1 + score_efficiency2)
    mean_vy = abs(sum(list_HAV[:, 3]) / len(list_HAV[:, 3]))

    # comfortable
    UncomfortAccnum=0
    UncomfortDecnum=0
    UncomfortAcc_lateralnum=0
    UncomfortDec_lateralnum=0
    UncomfortAAccnum=0
    UncomfortDDecnum=0
    UncomfortAAcc_lateralnum=0
    UncomfortDDec_lateralnum=0
    for i in range(0,np.shape(HAV)[0]):
        if list_HAV[i, 7] > 3:
            UncomfortAccnum+=1
        if list_HAV[i, 7] < -3:
            UncomfortDecnum+=1
        if list_HAV[i,8] > 0.5:
            UncomfortAcc_lateralnum+=1
        if list_HAV[i,8]<-0.5:
            UncomfortDec_lateralnum+=1
        if list_HAV[i, 9] > 6:
            UncomfortAAccnum+=1
        if list_HAV[i, 9] <-6:
            UncomfortDDecnum+=1
        if list_HAV[i, 10] > 1:
            UncomfortAAcc_lateralnum+=1
        if list_HAV[i, 10] < -1:
            UncomfortDDec_lateralnum+=1


    Uncomfort_num = UncomfortAccnum +UncomfortDecnum
    Uncomfort_numlateral = UncomfortAcc_lateralnum+UncomfortDec_lateralnum
    Uncomfort_numAAcc =UncomfortAAccnum+UncomfortDDecnum
    Uncomfort_numlateralAAcc = UncomfortAAcc_lateralnum+UncomfortDDec_lateralnum
    all_num = np.shape(list_HAV)[0]
    score_comfort = comfort - Uncomfort_num / all_num * 5 - Uncomfort_numlateral / all_num * 5 - Uncomfort_numAAcc / all_num * 5 - Uncomfort_numlateralAAcc / all_num * 5
    score_comfort = max(0, score_comfort)
    score_comfort = min(comfort, score_comfort)

    ##增加规控器失效判断
    v_yaw = np.zeros(shape=(np.shape(list_HAV)[0], 1))
    for i in range(0,np.shape(list_HAV)[0]-1):
        v_yaw[i + 1] =abs((list_HAV[i + 1,4] - list_HAV[i,4]) /dt)
    v_yaw=v_yaw[v_yaw>500]
    v_err = list_HAV[list_HAV[:, 5] <-1, 5]
    if np.shape(v_yaw)[0]!=0 or (np.shape(list_HAV)[0]==1) or (len(list_HAV[abs(list_HAV[:, 7]) >200, 7])!=0)or(len(list_HAV[abs(list_HAV[:, 8]) >200, 8])!=0)or(np.shape(v_err)[0]!=0):
        score_safe=0
        score_efficiency=0
        score_comfort=0

   ##计算可能存在问题，未考虑横纵向的区别，若需输出则再更改
    if len(list_HAV[list_HAV[:, 7] > 0, 7]) != 0:
        mean_ACCx = sum(list_HAV[list_HAV[:, 7] > 0, 7]) / len(list_HAV[list_HAV[:, 7] > 0, 7])
    else:
        mean_ACCx = 0
    if len(list_HAV[list_HAV[:, 7] < 0, 7]) != 0:
        mean_DECx = sum(list_HAV[list_HAV[:, 7] < 0, 7]) / len(list_HAV[list_HAV[:, 7] < 0, 7])
    else:
        mean_DECx = 0
    if len(list_HAV[list_HAV[:, 8] > 0, 8]) != 0:
        mean_ACCy = sum(list_HAV[list_HAV[:, 8] > 0, 8]) / len(list_HAV[list_HAV[:, 8] > 0, 8])
    else:
        mean_ACCy = 0
    if len(list_HAV[list_HAV[:, 8] < 0, 8]) != 0:
        mean_DECy = sum(list_HAV[list_HAV[:, 8] < 0, 8]) / len(list_HAV[list_HAV[:, 8] < 0, 8])
    else:
        mean_DECy = 0

    if len(list_HAV[list_HAV[:, 9] > 0, 9]) != 0:
        mean_AACCx = sum(list_HAV[list_HAV[:, 9] > 0, 9]) / len(list_HAV[list_HAV[:, 9] > 0, 9])
    else:
        mean_AACCx = 0
    if len(list_HAV[list_HAV[:, 9] < 0, 9]) != 0:
        mean_DDECx = sum(list_HAV[list_HAV[:, 9] < 0, 9]) / len(list_HAV[list_HAV[:, 9] < 0, 9])
    else:
        mean_DDECx = 0
    if len(list_HAV[list_HAV[:, 10] > 0, 10]) != 0:
        mean_AACCy = sum(list_HAV[list_HAV[:, 10] > 0, 10]) / len(list_HAV[list_HAV[:, 10] > 0, 10])
    else:
        mean_AACCy = 0
    if len(list_HAV[list_HAV[:, 10] < 0, 10]) != 0:
        mean_DDECy = sum(list_HAV[list_HAV[:, 10] < 0, 10]) / len(list_HAV[list_HAV[:, 10] < 0, 10])
    else:
        mean_DDECy = 0
    turn_a=0

    #分数输出
    if output_type == 'default':
        score = score_safe + score_efficiency + score_comfort
        return ([score,score_safe,score_efficiency,score_comfort])
    elif output_type == 'details':
        return ( [score_safe + score_efficiency + score_comfort, score_safe, score_efficiency, score_comfort,mean_TTC,oppo_lane_rate,out_lane_rate,run_red,\
                  done_ornot,mean_vy,distance_todest,\
                mean_ACCy,mean_DECy,mean_ACCx,mean_DECx,mean_AACCy,mean_DDECy,mean_AACCx,mean_DDECx,turn_a])
    else:
        raise AttributeError("output_type do not accept!")

class Evaluatorzd:
    def __init__(self,outputs_path,scenario_path):
        self.outputs_path = outputs_path
        self.scenario_path =scenario_path

    def evaluate(self, output_type='details'):
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
            scenario_pathdetail=os.path.join(self.scenario_path+"/"+str(scenario))
            #answersheet_path = os.path.join("answersheet/"+str(scenario)+"_answer.csv" )
            answersheet=write_answersheet_ramp(file_path,scenario_pathdetail)
            #answersheet.to_csv(answersheet_path,index=False)
            #dataframe = pd.read_csv(answersheet_path, header=None)
            list_HAV=answersheet.values
            #list_HAV = np.array(list_HAV[3:,:])#实车需改动！！！
            list_HAV = np.array(list_HAV)
            score = Evaluation_ramp(list_HAV,scenario,scenario_pathdetail,safety=50,efficiency=30,comfort=20,dt=0.1,output_type=output_type)
            # print('score', score)
            all_score.append(score)
            all_scenarios.append(scenario)

        if output_type == 'default':
            return all_scenarios,np.array(all_score)
        elif output_type == 'details':
            return all_scenarios, np.array(all_score)

if __name__ == '__main__':
    #eva = Evaluatorzd("ramp/实车轨迹/汇出实车_处理","ramp/ramp_out","ramp/scenario_type.csv")

    eva=Evaluatorzd(r"C:\Users\Administrator\Desktop\demo\idm2onsite_demo\outputs_v5",r"C:\Users\Administrator\Desktop\场景及实车轨迹\封硕场景\ramp_scenariov5\final")
    names,score = eva.evaluate()
    print(score)
    #pd.DataFrame(score).to_csv("ramp_results.csv")
    df_score = pd.DataFrame(score,
                            columns=['total_score', 'score_safe', 'score_efficiency', 'score_comfort', 'lane_ornot',
                                     'done_ornot', 'distance_todest', 'mean_TTC', 'mean_vy', 'mean_ACCx', 'mean_DECx',
                                     'mean_ACCy', 'mean_DECy', 'mean_AACCx', 'mean_DDECx', 'mean_AACCy', 'mean_DDECy'],
                             index=names)
    df_score.to_csv('ramp_results.csv', header=True, index=True)

    # scenario_path = r'D:\PycharmProjects\pythonProject\ramp\scenariov2\2cutin97'
    # parserd_v2(scenario_path)

