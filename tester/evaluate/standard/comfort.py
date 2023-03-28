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
        # print(type(self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego']))
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
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
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 0.5, 'ax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -0.5, 'ax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') > 0.5, 'ay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') < -0.5, 'ay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        return None

    def penalty_for_horizontal_a(self) -> None:
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
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
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') > 3, 'ay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'ay_ego'].astype('float') < -3, 'ay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') > 3, 'ax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'ax_ego'].astype('float') < -3, 'ax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        return None

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
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
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
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 1, 'aax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -1, 'aax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') > 1, 'aay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') < -1, 'aay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        return None

    def penalty_for_horizontal_aa(self) -> None:
        if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') or ('W', 'E'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S') or ('S', 'N'):
            uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
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
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
                uncomfortable_d = self.info_table.ego_front_vehicle_info.loc[
                    self.info_table.ego_front_vehicle_info.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
            if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' or 'E':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
            elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' or 'S':
                uncomfortable_a = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
                uncomfortable_d = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
                self.deducted_score = (uncomfortable_a.shape[0] + uncomfortable_d.shape[0]) / \
                                      self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') or ('E', 'S') or ('W', 'N') or ('W', 'S'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') or ('N', 'E') or ('S', 'W') or ('S', 'E'):
            uncomfortable_a_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') > 6, 'aay_ego']
            uncomfortable_d_front = self.front_segment.loc[self.front_segment.loc[:, 'aay_ego'].astype('float') < -6, 'aay_ego']
            uncomfortable_a_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') > 6, 'aax_ego']
            uncomfortable_d_latter = self.latter_segment.loc[self.latter_segment.loc[:, 'aax_ego'].astype('float') < -6, 'aax_ego']
            self.deducted_score = (uncomfortable_a_front.shape[0] + uncomfortable_d_front.shape[0] +
                                   uncomfortable_a_latter.shape[0] + uncomfortable_d_latter.shape[0]) / \
                                  self.info_table.ego_front_vehicle_info.shape[0] * 4
        return None

    def penalty_for_turning(self) -> None:
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
            except ZeroDivisionError:
                self.deducted_score += 0
        return None

    def comfort_evaluation(self) -> float:

        # if self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'W') :
        #     error_v = self.info_table.ego_front_vehicle_info.loc[
        #         self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #     error_vshape=error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] ==  ('W', 'E'):
        #     error_v = self.info_table.ego_front_vehicle_info.loc[
        #         self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #     error_vshape = error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'S'):
        #     error_v = self.info_table.ego_front_vehicle_info.loc[
        #         self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #     error_vshape = error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] ==  ('S', 'N'):
        #     error_v = self.info_table.ego_front_vehicle_info.loc[
        #         self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #     error_vshape = error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'].count(
        #         self.info_table.relation_judgement.info.replay_info['travel_direction'][0]) == len(
        #     self.info_table.relation_judgement.info.replay_info['travel_direction']):
        #     if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' :
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'E' :
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' :
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'S':
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #         error_vshape = error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'][1] == 'IN':
        #     if self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'W' :
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'E':
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'N' :
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #         error_vshape = error_v.shape[0]
        #     elif self.info_table.relation_judgement.info.replay_info['travel_direction'][0] == 'S':
        #         error_v = self.info_table.ego_front_vehicle_info.loc[
        #             self.info_table.ego_front_vehicle_info.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #         error_vshape = error_v.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'N') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #     error_vshape = error_v_front.shape[0]+error_v_latter.shape[0]
        # elif  self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('E', 'S') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif  self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('W', 'N') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('W', 'S'):
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'W') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('N', 'E') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') > 0, 'vy_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('S', 'W') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') > 0, 'vx_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]
        # elif self.info_table.relation_judgement.info.replay_info['travel_direction'] == ('S', 'E') :
        #     error_v_front = self.front_segment.loc[self.front_segment.loc[:, 'vy_ego'].astype('float') < 0, 'vy_ego']
        #     error_v_latter = self.front_segment.loc[self.front_segment.loc[:, 'vx_ego'].astype('float') < 0, 'vx_ego']
        #     error_vshape = error_v_front.shape[0] + error_v_latter.shape[0]


        if self.info_table.ego_front_vehicle_info is None:
            self.deducted_score = 20
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ax_ego'].astype('float') )> 200, 'ax_ego'].shape[0]!=0:
            self.deducted_score =20
        elif self.info_table.ego_front_vehicle_info.loc[
                abs(self.info_table.ego_front_vehicle_info.loc[:, 'ay_ego'].astype('float') )> 200, 'ay_ego'].shape[0]!=0:
            self.deducted_score = 20
        else:
            self.penalty_for_vertical_a()
            self.penalty_for_horizontal_a()
            self.calculate_aax_and_aay()
            self.penalty_for_vertical_aa()
            self.penalty_for_horizontal_aa()
            self.penalty_for_turning()
            self.deducted_score = np.clip(self.deducted_score, 0, 20)
        return self.deducted_score


if __name__ == "__main__":
    Trajectory_path = r''
    Scenario_path = r''
    Interval = 5
    ego_front_vehicle_info = EgoForwardVehicleInfo(Trajectory_path, Scenario_path, Interval)
    ego_front_vehicle_info.ndarray_to_dataframe()
    comfort_deduct = ComfortCriteria(ego_front_vehicle_info)
    comfort_deduct_score = comfort_deduct.comfort_evaluation()
    print(comfort_deduct_score)
