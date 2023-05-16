# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/30 22:35
import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm
from interface import Interface
from standard.safety import SafetyCriteria
from standard.comfort import ComfortCriteria
from standard.efficiency import EfficiencyCriteria
from evaluation_prepare.ego_and_forward_vehicle_relation import EgoForwardVehicleInfo
from server_v3.evaluate import Evaluation
from server_v3.evaluate import write_answerSheet
from ramp.ramp_eval import write_answersheet_ramp
from ramp.ramp_eval import Evaluation_ramp
# import PySimpleGUI as sgimport
from statistics import mean

def evaluating_multiple_scenarios(trajectory_path: str, scenario_path: str, interval: int = 5) -> tuple:
    all_scenario = []
    safety_score = []
    efficiency_score = []
    comfort_score = []
    all_score = []
    Mean_ttc=[]
    Oppo_lane_rate=[]
    Out_lane_rate=[]
    Run_red=[]
    Done_ornot=[]
    Mean_v=[]
    Distance_todest=[]
    a_x=[]
    d_x=[]
    a_y=[]
    d_y=[]
    aa_x=[]
    dd_x=[]
    aa_y=[]
    dd_y=[]
    turn_a=[]
    trajectory_list = list(os.listdir(trajectory_path))
    for item in trajectory_list:
        # sgimport.theme('lightgrey')
        # sgimport.set_global_icon(filename='onsite.png')
        # sgimport.one_line_progress_meter("评价进度", i , len(trajectory_list), orientation='h',button_color=('black','lightgrey'))
        if item[0] != '.' and  '_result.csv' in item:
            all_scenario.append(item[:-11])
    with tqdm(total=len(all_scenario)) as _tqdm:
        for scenario in all_scenario:
            _tqdm.set_description(f"--> scene<{scenario}>")    
            file_path = os.path.join(trajectory_path, f"{scenario}_result.csv")
            output = pd.read_csv(file_path)
            if len(output) == 1 or output['end'].iloc[-1] == -1:
                safety_score.append(0)
                efficiency_score.append(0)
                comfort_score.append(0)
                all_score.append(0)
                Mean_ttc.append(0)
                Oppo_lane_rate.append(0)
                Out_lane_rate.append(0)
                Run_red.append(0)
                Done_ornot.append(0)
                Mean_v.append(0)
                Distance_todest.append(0)
                a_x.append(0)
                d_x.append(0)
                a_y.append(0)
                d_y.append(0)
                aa_x.append(0)
                dd_x.append(0)
                aa_y.append(0)
                dd_y.append(0)
                turn_a.append(0)
            else:
                ego_front_vehicle_info = EgoForwardVehicleInfo(file_path, scenario_path)
                if ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_one':  # 高速公路评价体系
                    database = os.path.abspath(os.path.join(os.path.dirname(__file__), './server_v3/database'))
                    recording_path = database + '/recording.csv'
                    start_destpath = database + '/start_dest.csv'
                    answersheet = write_answerSheet(file_path, recording_path, start_destpath, scenario)
                    list_HAV = answersheet.values
                    list_HAV = np.array(list_HAV[1:])
                    list_HAV = list_HAV.astype(np.float64)
                    score = Evaluation(list_HAV, start_destpath, scenario, area=0, safety=50, efficiency=30, comfort=20,
                                    dt=0.04, output_type='details')
                    safetyscore = float(format(score[1], '.2f'))
                    efficiencyscore = float(format(score[2], '0.2f'))
                    comfortscore = round(score[3], 2)
                    allscore = round(safetyscore + efficiencyscore + comfortscore, 2)
                    safety_score.append(safetyscore)
                    efficiency_score.append(efficiencyscore)
                    comfort_score.append(comfortscore)
                    all_score.append(allscore)
                    Mean_ttc.append(score[4])
                    Oppo_lane_rate.append(score[5])
                    Out_lane_rate.append(score[6])
                    Run_red.append(score[7])
                    Done_ornot.append(score[8])
                    Mean_v.append(score[9])
                    Distance_todest.append(score[10])
                    a_x.append(score[11])
                    d_x.append(score[12])
                    a_y.append(score[13])
                    d_y.append(score[14])
                    aa_x.append(score[15])
                    dd_x.append(score[16])
                    aa_y.append(score[17])
                    dd_y.append(score[18])
                    turn_a.append(score[19])

                    # print('该场景安全得分为：', safetyscore, '\n该场景效率得分为：', efficiencyscore, '\n该场景舒适得分为：', comfortscore, '\n该场景总得分为：', allscore)
                elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_two':  # 交叉口评价体系
                    ego_front_vehicle_info.init(interval)
                    ego_front_vehicle_info.ndarray_to_dataframe()
                    # 安全得分(0-50)
                    safety_deduct = SafetyCriteria(ego_front_vehicle_info)
                    safety_deduct_score,mean_ttc,oppo_lane_rate,out_area_rate,run_red = safety_deduct.safety_evaluation()
                    safetyscore=round(50 - safety_deduct_score,2)
                    safety_score.append(safetyscore)
                    Mean_ttc.append(mean_ttc)
                    Oppo_lane_rate.append(oppo_lane_rate)
                    Out_lane_rate.append(out_area_rate)
                    Run_red.append(run_red)
                    #print('该场景安全得分为：', safetyscore)

                    # 效率得分(0-30)
                    efficiency_deduct = EfficiencyCriteria(ego_front_vehicle_info)
                    efficiency_deduct_score,done_ornot,mean_vy,distance_todest = efficiency_deduct.efficiency_evaluation()
                    efficiencyscore=round(30-efficiency_deduct_score,2)
                    efficiency_score.append(efficiencyscore)
                    Done_ornot.append(done_ornot)
                    Mean_v.append(mean_vy)
                    Distance_todest.append(distance_todest)
                    #print('该场景效率得分为：', efficiencyscore)

                    # 舒适得分(0-20)
                    comfort_deduct = ComfortCriteria(ego_front_vehicle_info)
                    comfort_deduct_score,mean_vertical_a,mean_vertical_d,mean_horizontal_a,mean_horizontal_d,mean_vertical_aa,mean_vertical_dd,mean_horizontal_aa, mean_horizontal_dd,mean_turn_a= comfort_deduct.comfort_evaluation()
                    comfortscore=round(20-comfort_deduct_score,2)
                    comfort_score.append(comfortscore)
                    a_x.append(mean_vertical_a)
                    d_x.append(mean_vertical_d)
                    a_y.append(mean_horizontal_a)
                    d_y.append(mean_horizontal_d)
                    aa_x.append(mean_vertical_aa)
                    dd_x.append(mean_vertical_dd)
                    aa_y.append(mean_horizontal_aa)
                    dd_y.append(mean_horizontal_dd)
                    turn_a.append(mean_turn_a)
                    #print('该场景舒适得分为：', comfortscore)

                    total_score = round(100 - safety_deduct_score - efficiency_deduct_score - comfort_deduct_score,2)
                    all_score.append(total_score)
                    #print('该场景总得分为：', total_score)
                elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_three': #汇入汇出
                    scenario_path_detail = os.path.join(scenario_path + "/" + scenario)
                    #scenariotype_path = os.path.join(os.path.dirname(__file__), './ramp/scenario_type.csv')
                    answersheet = write_answersheet_ramp(file_path, scenario_path_detail)
                    list_HAV = answersheet.values
                    # list_HAV = np.array(list_HAV[3:,:])#实车轨迹存在误差，需用这个改动
                    list_HAV = np.array(list_HAV)
                    score = Evaluation_ramp(list_HAV, scenario, scenario_path_detail, safety=50, \
                                            efficiency=30, comfort=20, dt=0.1, output_type="details")
                    safetyscore = float(format(score[1], '.2f'))
                    efficiencyscore = float(format(score[2], '0.2f'))
                    comfortscore = round(score[3], 2)
                    allscore = round(safetyscore + efficiencyscore + comfortscore, 2)
                    safety_score.append(safetyscore)
                    efficiency_score.append(efficiencyscore)
                    comfort_score.append(comfortscore)
                    all_score.append(allscore)
                    Mean_ttc.append(score[4])
                    Oppo_lane_rate.append(score[5])
                    Out_lane_rate.append(score[6])
                    Run_red.append(score[7])
                    Done_ornot.append(score[8])
                    Mean_v.append(score[9])
                    Distance_todest.append(score[10])
                    a_x.append(score[11])
                    d_x.append(score[12])
                    a_y.append(score[13])
                    d_y.append(score[14])
                    aa_x.append(score[15])
                    dd_x.append(score[16])
                    aa_y.append(score[17])
                    dd_y.append(score[18])
                    turn_a.append(score[19])
                elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_four':  # 其他评价体系
                        #print('使用其他评价体系')
                        safety_score.append(100)
                        efficiency_score.append(100)
                        comfort_score.append(100)
                        all_score.append(300)
            _tqdm.update(1)
    return ([all_scenario, safety_score, efficiency_score, comfort_score, all_score,Mean_ttc,Oppo_lane_rate,Out_lane_rate,Run_red,Done_ornot,Mean_v,Distance_todest,\
a_x,d_x,a_y,d_y,aa_x,dd_x,aa_y,dd_y,turn_a])





def _check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def recording(result: tuple, output: str) -> None:
    _check_dir(output)
    # (scenario, safety, efficiency, comfort, total) = result
    # result_array = np.array([np.array(scenario),
    #                         np.array(safety),
    #                         np.array(efficiency),
    #                         np.array(comfort),
    #                         np.array(total)])
    result_array = np.array(result[:5])
    note = pd.Series(
        ['1.本工具从安全性(满分50分)、效率性(满分30分) 以及舒适性(满分20分)三个维度对规控器进行性能评价，总分满分100分。',
        '2.用户可依据评价结果选取需要的场景，借助onsite官网提供的可视化工具对该场景下的驾驶场景进行复现。'])
    result_dataframe = pd.DataFrame(result_array.T, columns=['Scenario', 'Safety', 'Efficiency', 'Comfort', 'Total'])
    result_dataframe0 = pd.DataFrame(np.insert(result_dataframe.values, len(result_dataframe.index),
                                               values=["Mean", round(mean(result_array[1,:].astype(float)), 2), round(mean(result_array[2,:].astype(float)), 2),
                                                       round(mean(result_array[3,:].astype(float)), 2), round(mean(result_array[4,:].astype(float)), 2)], axis=0))
    result_dataframe0.columns = result_dataframe.columns
    result_dataframe1 = pd.concat([result_dataframe0, note], axis=1)
    result_dataframe1.columns = ['Scenario', 'Safety', 'Efficiency', 'Comfort', 'Total','Note']
    result_dataframe1.to_csv(os.path.join(output, 'score.csv'), index=False, encoding="utf_8_sig")
    return None


if __name__ == "__main__":
    mode = 0
    if mode == 1:
        info = Interface()
        infoscenario,infotrajectory,infoeval = info.interface_making()
        #print(infoscenario,infotrajectory,infoeval)
        # while '' in infoscenario:
        #     infoscenario.remove('')
        Scenario_path = infoscenario
        #print(Scenario_path)
        # while '' in infotrajectory:
        #     infotrajectory.remove('')
        Trajectory_path = infotrajectory
        # Interval = param_list[2]
        # while '' in infoeval:
        #     infoeval.remove('')
        Output = infoeval
        # record = param_list[4]
        score_result = evaluating_multiple_scenarios(Trajectory_path, Scenario_path)
        recording(score_result, Output)

    else:
        Scenario_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "./inputs")
        Trajectory_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "./outputs")
        # Scenario_path =r"C:\Users\Administrator\Desktop\评分inter\inputs"
        # Trajectory_path =r"C:\Users\Administrator\Desktop\评分inter\outputs"
        Interval = 1
        Output = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "./outputs")
        record = True
        score_result = evaluating_multiple_scenarios(Trajectory_path, Scenario_path, Interval)
        if record:
            recording(score_result, Output)
        print(f"评分完成，结果保存在:{os.path.join(Output, 'score.csv')}")
