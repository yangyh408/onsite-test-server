# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/2/20 19:25
import matplotlib.pyplot as plt
from pathlib import Path

import pandas as pd

from parsing.parser import Parser
import shapely.geometry
from descartes import PolygonPatch
import os
from pathlib import Path


if __name__ == "__main__":
    Scenario_path = r"E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\scenario"
    Trajectory_path = r"E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\trajectory"
    trajectory_files = os.listdir(Trajectory_path)
    for trajectory in trajectory_files:
        parser = Parser()
        parser.parse(Trajectory_path + '\\' + trajectory, Scenario_path)
        # print(parser.info.zone)
        try:
            fig, ax = plt.subplots()
            for index, item in enumerate(['WI', 'EI', 'NI', 'SI', 'WO', 'EO', 'NO', 'SO', 'IN']):
                if item != 'IN':
                    ax.add_patch(PolygonPatch(parser.info.zone[item], alpha=0.3))
                else:
                    for lane in parser.info.zone[item]:
                        ax.add_patch(PolygonPatch(lane, alpha=0.3))
            plt.scatter(parser.info.openScenario_info['goal_x'][-1], parser.info.openScenario_info['goal_y'][-1], c='r')
            ax.set(xlim=(-50, 450),
                   ylim=(-50, 75)
                   )
            # plt.show()
            plt.savefig('E:\研究生\同济大学\TOPs\onsite网站\intersection_evaluation\onsite_intersection_evaluation_version_2\demo\map_fig\{0}.png'.format(trajectory.split('.')[0]), dpi=600)
        except ValueError:
            print(trajectory)
