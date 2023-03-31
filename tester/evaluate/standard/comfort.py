# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/30 11:43
import numpy as np
import pandas as pd
from evaluation_prepare.ego_and_forward_vehicle_relation import EgoForwardVehicleInfo


class ComfortCriteria:
    """
    这里定义了与舒适相关的指标，包括横向舒适度、纵向舒适度和转弯舒适度
    """

    def __init__(self, EgoForwardVehicleInfo):
        self.deducted_score = None
        self.info_table = EgoForwardVehicleInfo
        try:
            self.front_segment = self.info_table.ego_front_vehicle_info.iloc[0:self.info_table.first_segment_length, :]
            self.middle_segment = self.info_table.ego_front_vehicle_info.iloc[
                                  self.info_table.first_segment_length:self.info_table.first_segment_length + self.info_table.second_segment_length,
                                  :]
            self.latter_segment = self.info_table.ego_front_vehicle_info.iloc[
                                  self.info_table.first_segment_length + self.info_table.second_segment_length:, :]
        except AttributeError:
            pass
        self.info_table.relation_judgement.info.replay_info['travel_direction'] = tuple(
            self.info_table.relation_judgement.info.replay_info['travel_direction'])

    def penalty_for_vertical_a(self) -> None:
        sum_a=0
        sum_d=0
        sum(self.info_table.ego_front_vehicle_info['ay_ego'].astype('float'))
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a=sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 0, 'ay_ego'].astype('float'))
            sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                            self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                'float'))

        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                            self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                'float') > 0, 'ax_ego'].astype('float'))
            sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
                self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(
            self.info_table.relation_judgement.info.replay_info['travel_direction']):
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype(
                                    'float') > 0, 'ay_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                    'float') > 0, 'ax_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype(
                                    'float') > 0, 'ay_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                    'float') > 0, 'ax_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ay_ego'].astype('float') > 0, 'ay_ego'].astype('float'))+sum(self.latter_segment.loc[
                            self.latter_segment.loc[:, 'ax_ego'].astype('float') > 0, 'ax_ego'].astype('float'))
            sum_d =sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype('float'))+sum(self.latter_segment.loc[
                            self.latter_segment.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype('float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ax_ego'].astype('float') > 0, 'ax_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ay_ego'].astype('float') > 0, 'ay_ego'].astype('float'))
            sum_d = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype('float'))
        mean_vertical_a=sum_a/self.info_table.ego_front_vehicle_info.shape[0]
        mean_vertical_d=sum_d/self.info_table.ego_front_vehicle_info.shape[0]
        return mean_vertical_a,mean_vertical_d

    def penalty_for_horizontal_a(self) -> None:
        sum_a=0
        sum_d=0
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a=sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                    'float') > 0, 'ax_ego'].astype('float'))
            sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                            self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype(
                                'float') > 0, 'ay_ego'].astype('float'))
            sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
                self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(
            self.info_table.relation_judgement.info.replay_info['travel_direction']):
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                    'float') > 0, 'ax_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype(
                                    'float') > 0, 'ay_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype(
                                    'float') > 0, 'ax_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_a = sum(self.info_table.ego_front_vehicle_info.loc[
                                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype(
                                    'float') > 0, 'ay_ego'].astype('float'))
                sum_d = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ax_ego'].astype('float') > 0, 'ax_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ay_ego'].astype('float') > 0, 'ay_ego'].astype('float'))
            sum_d = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype('float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_a = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ay_ego'].astype('float') > 0, 'ay_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ax_ego'].astype('float') > 0, 'ax_ego'].astype('float'))
            sum_d = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'ay_ego'].astype('float') < 0, 'ay_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'ax_ego'].astype('float') < 0, 'ax_ego'].astype('float'))
        mean_horizontal_a=sum_a/self.info_table.ego_front_vehicle_info.shape[0]
        mean_horizontal_d=sum_d/self.info_table.ego_front_vehicle_info.shape[0]
        return mean_horizontal_a,mean_horizontal_d


    def calculate_aax_and_aay(self) -> None:
        # aay
        ay = list(self.info_table.ego_front_vehicle_info['ay_ego'])
        aay = []
        for i in range(len(ay) - 1):
            diff_y = float(ay[i + 1]) - float(ay[i])
            aay.append(diff_y / self.info_table.relation_judgement.info.replay_info['dt'])
        aay.append(aay[-1])
        self.info_table.ego_front_vehicle_info['aay_ego'] = aay
        # aax
        ax = list(self.info_table.ego_front_vehicle_info['ax_ego'])
        aax = []
        for i in range(len(ax) - 1):
            diff_x = float(ax[i + 1]) - float(ax[i])
            aax.append(diff_x / self.info_table.relation_judgement.info.replay_info['dt'])
        aax.append(aax[-1])
        self.info_table.ego_front_vehicle_info['aax_ego'] = aax
        return None

    def penalty_for_vertical_aa(self) -> None:
        sum_aa=0
        sum_dd=0
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                            self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                'float') > 0, 'aay_ego'].astype('float'))
            sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                            self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                'float') > 0, 'aax_ego'].astype('float'))
            sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
                self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(
            self.info_table.relation_judgement.info.replay_info['travel_direction']):
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                     'float') > 0, 'aay_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                     'float') > 0, 'aax_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                     'float') > 0, 'aay_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                     'float') > 0, 'aax_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'aay_ego'].astype('float') > 0, 'aay_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aax_ego'].astype('float') > 0, 'aax_ego'].astype('float'))
            sum_dd = sum(self.front_segment.loc[
                            self.front_segment.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype('float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype('float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.front_segment.loc[
                             self.front_segment.loc[:, 'aax_ego'].astype('float') > 0, 'aax_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aay_ego'].astype('float') > 0, 'aay_ego'].astype('float'))
            sum_dd = sum(self.front_segment.loc[
                             self.front_segment.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype('float'))
        mean_vertical_aa = sum_aa / self.info_table.ego_front_vehicle_info.shape[0]
        mean_vertical_dd = sum_dd / self.info_table.ego_front_vehicle_info.shape[0]
        return mean_vertical_aa, mean_vertical_dd

    def penalty_for_horizontal_aa(self) -> None:
        sum_aa=0
        sum_dd=0
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                             self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                 'float') > 0, 'aax_ego'].astype('float'))
            sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                             self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                 'float') > 0, 'aay_ego'].astype('float'))
            sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
                self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(
            self.info_table.relation_judgement.info.replay_info['travel_direction']):
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                     'float') > 0, 'aax_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                     'float') > 0, 'aay_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype(
                                     'float') > 0, 'aax_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                    'float'))
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
                sum_aa = sum(self.info_table.ego_front_vehicle_info.loc[
                                 self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype(
                                     'float') > 0, 'aay_ego'].astype('float'))
                sum_dd = sum(self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                    'float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.front_segment.loc[
                self.front_segment.loc[:, 'aax_ego'].astype('float') > 0, 'aax_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aay_ego'].astype('float') > 0, 'aay_ego'].astype('float'))
            sum_dd = sum(self.front_segment.loc[
                self.front_segment.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype('float'))
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
            sum_aa = sum(self.front_segment.loc[
                             self.front_segment.loc[:, 'aay_ego'].astype('float') > 0, 'aay_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aax_ego'].astype('float') > 0, 'aax_ego'].astype('float'))
            sum_dd = sum(self.front_segment.loc[
                             self.front_segment.loc[:, 'aay_ego'].astype('float') < 0, 'aay_ego'].astype(
                'float')) + sum(
                self.latter_segment.loc[
                    self.latter_segment.loc[:, 'aax_ego'].astype('float') < 0, 'aax_ego'].astype('float'))
        mean_horizontal_aa = sum_aa / self.info_table.ego_front_vehicle_info.shape[0]
        mean_horizontal_dd = sum_dd / self.info_table.ego_front_vehicle_info.shape[0]
        return mean_horizontal_aa, mean_horizontal_dd


    def penalty_for_turning(self) -> None:
        mean_turn_a=0
        if not self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N') or (
                'E', 'W') or ('W', 'E'):
            a_turning = self.info_table.ego_front_vehicle_info['ay_ego'].astype('float') * np.cos(
                self.info_table.ego_front_vehicle_info['yaw_ego'].astype('float')) - \
                        self.info_table.ego_front_vehicle_info['ax_ego'].astype('float') * np.sin(
                self.info_table.ego_front_vehicle_info['yaw_ego'].astype('float'))

            uncomfortable_a_turning_pos = a_turning[a_turning > 1]
            uncomfortable_a_turning_neg = a_turning[a_turning < -1]
            try:
                self.deducted_score += (uncomfortable_a_turning_pos.shape[0] + uncomfortable_a_turning_neg.shape[0]) / \
                                        self.middle_segment.shape[0]
                mean_turn_a = sum(a_turning) / self.middle_segment.shape[0]
            except ZeroDivisionError:
                self.deducted_score += 0
        return mean_turn_a

    def comfort_evaluation(self) -> float:
        mean_turn_a=0
        mean_vertical_a=0
        mean_vertical_d=0
        mean_horizontal_a=0
        mean_horizontal_d=0
        mean_vertical_aa = 0
        mean_vertical_dd = 0
        mean_horizontal_aa=0
        mean_horizontal_dd=0
        if self.info_table.ego_front_vehicle_info is None:
            self.deducted_score = 20
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') )> 200, 'ax_ego'].shape[0]!=0:
            self.deducted_score =20
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') )> 200, 'ay_ego'].shape[0]!=0:
            self.deducted_score = 20
        else:
            mean_vertical_a,mean_vertical_d=self.penalty_for_vertical_a()
            mean_horizontal_a,mean_horizontal_d=self.penalty_for_horizontal_a()
            self.calculate_aax_and_aay()
            mean_vertical_aa,mean_vertical_dd=self.penalty_for_vertical_aa()
            mean_horizontal_aa,mean_horizontal_dd=self.penalty_for_horizontal_aa()
            mean_turn_a=self.penalty_for_turning()
            self.deducted_score = np.clip(self.deducted_score, 0, 20)
        return self.deducted_score,mean_vertical_a,mean_vertical_d,mean_horizontal_a,mean_horizontal_d,mean_vertical_aa,mean_vertical_dd,mean_horizontal_aa,mean_horizontal_dd,mean_turn_a


if __name__ == "__main__":
    Trajectory_path = r''
    Scenario_path = r''
    Interval = 5
    ego_front_vehicle_info = EgoForwardVehicleInfo(Trajectory_path, Scenario_path, Interval)
    ego_front_vehicle_info.ndarray_to_dataframe()
    comfort_deduct = ComfortCriteria(ego_front_vehicle_info)
    comfort_deduct_score = comfort_deduct.comfort_evaluation()
    print(comfort_deduct_score)
