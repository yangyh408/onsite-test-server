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
    trajectory_list = list(os.listdir(trajectory_path))
    for item in trajectory_list:
        # sgimport.theme('lightgrey')
        # sgimport.set_global_icon(filename='onsite.png')
        # sgimport.one_line_progress_meter("评价进度", i , len(trajectory_list), orientation='h',button_color=('black','lightgrey'))
        if item[0] != '.' and  '_result.csv' in item:
            all_scenario.append(item.split('_')[0])
    # with tqdm(total=len(all_scenario)) as _tqdm:
    for scenario in all_scenario:
        # _tqdm.set_description(f"--> scene<{scenario}>")    
        file_path = os.path.join(trajectory_path, f"{scenario}_result.csv")
        ego_front_vehicle_info = EgoForwardVehicleInfo(file_path, scenario_path)
        if ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_one':  # 高速公路评价体系
            database = os.path.abspath(os.path.join(os.path.dirname(__file__), './server_v3/database'))
            recording_path = database + '/recording.csv'
            start_destpath = database + '/start_dest.csv'
            answersheet = write_answerSheet(file_path, recording_path, start_destpath, scenario)
            list_HAV = answersheet.values
            list_HAV = np.array(list_HAV[1:])
            list_HAV = list_HAV.astype(np.float64)
            score = Evaluation(list_HAV, start_destpath, scenario, area=5, safety=50, efficiency=30, comfort=20,
                            dt=0.04, output_type='default')
            safetyscore = float(format(score[1], '.2f'))
            efficiencyscore = float(format(score[2], '0.2f'))
            comfortscore = round(score[3], 2)
            allscore = round(safetyscore + efficiencyscore + comfortscore, 2)
            safety_score.append(safetyscore)
            efficiency_score.append(efficiencyscore)
            comfort_score.append(comfortscore)
            all_score.append(allscore)
            # print('该场景安全得分为：', safetyscore, '\n该场景效率得分为：', efficiencyscore, '\n该场景舒适得分为：', comfortscore, '\n该场景总得分为：', allscore)
        elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_two':  # 交叉口评价体系
            ego_front_vehicle_info.init(interval)
            ego_front_vehicle_info.ndarray_to_dataframe()
            # 安全得分(0-50)
            safety_deduct = SafetyCriteria(ego_front_vehicle_info)
            safety_deduct_score = safety_deduct.safety_evaluation()
            safetyscore=round(50 - safety_deduct_score,2)
            safety_score.append(safetyscore)
            #print('该场景安全得分为：', safetyscore)

            # 效率得分(0-30)
            efficiency_deduct = EfficiencyCriteria(ego_front_vehicle_info)
            efficiency_deduct_score = efficiency_deduct.efficiency_evaluation()
            efficiencyscore=round(30-efficiency_deduct_score,2)
            efficiency_score.append(efficiencyscore)
            #print('该场景效率得分为：', efficiencyscore)

            # 舒适得分(0-20)
            comfort_deduct = ComfortCriteria(ego_front_vehicle_info)
            comfort_deduct_score = comfort_deduct.comfort_evaluation()
            comfortscore=round(20-comfort_deduct_score,2)
            comfort_score.append(comfortscore)
            #print('该场景舒适得分为：', comfortscore)

            total_score = round(100 - safety_deduct_score - efficiency_deduct_score - comfort_deduct_score,2)
            all_score.append(total_score)
            #print('该场景总得分为：', total_score)
        elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_three': #汇入汇出
            scenario_path_detail = os.path.join(scenario_path + "/" + scenario)
            scenariotype_path = os.path.join(os.path.dirname(__file__), './ramp/scenario_type.csv')
            answersheet = write_answersheet_ramp(file_path, scenario_path_detail)
            list_HAV = answersheet.values
            # list_HAV = np.array(list_HAV[3:,:])#实车轨迹存在误差，需用这个改动
            list_HAV = np.array(list_HAV)
            score = Evaluation_ramp(list_HAV, scenariotype_path, scenario, scenario_path_detail, safety=50, \
                                    efficiency=30, comfort=20, dt=0.1, output_type="default")
            safetyscore = float(format(score[1], '.2f'))
            efficiencyscore = float(format(score[2], '0.2f'))
            comfortscore = round(score[3], 2)
            allscore = round(safetyscore + efficiencyscore + comfortscore, 2)
            safety_score.append(safetyscore)
            efficiency_score.append(efficiencyscore)
            comfort_score.append(comfortscore)
            all_score.append(allscore)
        elif ego_front_vehicle_info.relation_judgement.info.replay_info['evaluation_type'] == 'scheme_four':  # 其他评价体系
                #print('使用其他评价体系')
                safety_score.append(100)
                efficiency_score.append(100)
                comfort_score.append(100)
                all_score.append(300)
        # _tqdm.update(1)
    return all_scenario, safety_score, efficiency_score, comfort_score, all_score



def _check_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def recording(result: tuple, output: str) -> None:
    _check_dir(output)
    (scenario, safety, efficiency, comfort, total) = result
    result_array = np.array([np.array(scenario),
                            np.array(safety),
                            np.array(efficiency),
                            np.array(comfort),
                            np.array(total)])
    note = pd.Series(
        ['1.本工具从安全性(满分50分)、效率性(满分30分) 以及舒适性(满分20分)三个维度对规控器进行性能评价，总分满分100分。',
        '2.用户可依据评价结果选取需要的场景，借助onsite官网提供的可视化工具对该场景下的驾驶场景进行复现。'])
    result_dataframe = pd.DataFrame(result_array.T, columns=['Scenario', 'Safety', 'Efficiency', 'Comfort', 'Total'])
    result_dataframe0 = pd.DataFrame(np.insert(result_dataframe.values, len(result_dataframe.index),
                                               values=["Mean", round(mean(safety), 2), round(mean(efficiency), 2),
                                                       round(mean(comfort), 2), round(mean(total), 2)], axis=0))
    result_dataframe0.columns = result_dataframe.columns
    result_dataframe1 = pd.concat([result_dataframe0, note], axis=1)
    result_dataframe1.columns = ['Scenario', 'Safety', 'Efficiency', 'Comfort', 'Total', 'Note']
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
        Interval = 1
        Output = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "./outputs")
        record = True
        score_result = evaluating_multiple_scenarios(Trajectory_path, Scenario_path, Interval)
        if record:
            recording(score_result, Output)
        print(f"评分完成，结果保存在:{os.path.join(Output, 'score.csv')}")
