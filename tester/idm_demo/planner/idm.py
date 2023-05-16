#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import lib
import numpy as np
import pandas as pd

class IDM():
    def __init__(self, a_bound=5.0, exv=40, t=1.2, a=2.22, b=2.4, gama=4, s0=1.0, s1=2.0):
        """跟idm模型有关的模型参数，一定要记得调整

        :param a_bound: 本车加速度绝对值的上下界
        :param exv: 期望速度
        :param t: 反应时间
        :param a: 起步加速度
        :param b: 舒适减速度
        :param gama: 加速度指数
        :param s0: 静止安全距离
        :param s1: 与速度有关的安全距离选择参数
        """
        self.a_bound = a_bound
        self.exv = exv
        self.t = t
        self.a = a
        self.b = b
        self.gama = gama
        self.s0 = s0
        self.s1 = s1
        self.s_ = 0

    def act(self, observation, traj=None):
        frame = pd.DataFrame()
        for key, value in observation['vehicle_info'].items():
                sub_frame = pd.DataFrame(value,columns=['x', 'y', 'v', 'yaw', 'length', 'width'],index=[key])
                if traj:
                    if key != 'ego':    # 对于背景车
                        t = round(float(observation['test_setting']['t']),2)   # 当前时间
                        dt = round(float(observation['test_setting']['dt']),2) # 时间步长
                        t_n = round(t + dt , 2) # 下步时间
                        try:
                            x = traj[key][str(t)]['x']  # 当前x位置
                            x_n = traj[key][str(t_n)]['x']  # 下步x位置
                            sub_frame['v'] = abs((x_n-x)/dt) # 计算背景车速度
                        except KeyError:    # 缺失背景车数据
                            sub_frame['v'] = 0

                frame = pd.concat([frame, sub_frame])
        state = frame.to_numpy()

        return self.deside_acc(state),0

    def deside_acc(self, state):
        v, fv, dis_gap,direction = self.getInformFront(state)
        # print(v, fv, dis_gap,direction)
        # print(state)
        if dis_gap < 0:
            a_idm = self.a * (1 - (v / self.exv) ** self.gama)
        else:
            # 求解本车与前车的期望距离
            # print(self.s0,self.s1,self.exv,v,self.t)
            self.s_ = self.s0 + self.s1 * (v / self.exv) ** 0.5 + self.t * v + v * (
                v - fv) / 2 / (self.a * self.b) ** 0.5
            # 求解本车加速度
            a_idm = self.a * (1 - (v / self.exv) ** self.gama - ((self.s_ / (dis_gap+1e-6)) ** 2))
        # 对加速度进行约束
        a_idm = np.clip(a_idm, -self.a_bound, 1e7)
        # print(v,fv,dis_gap,a_idm,self.s_)
        # print(state,v,fv,dis_gap,a_idm)
        return a_idm

    def getInformFront(self,state):
        # direction = np.sign(state[0,2])
        if state[0, 3] < np.pi / 2 or state[0, 3] > np.pi * 3 / 2:
            direction = 1.0
        else:
            direction = -1.0
        state[:,0] = state[:,0]*direction
        # state[:,2] = state[:,2]*direction
        ego = state[0,:]
        v, fv, dis_gap = ego[2], -1, -1
        
        # 在本车前侧
        x_ind = ego[0] < state[:,0]
        y_ind = (np.abs(ego[1] - state[:,1])) < ((ego[5] + state[:,5])/2)
        ind = x_ind & y_ind
        if ind.sum() > 0:
            state_ind = state[ind,:]
            front = state_ind[(state_ind[:,0]-ego[0]).argmin(),:]
            # print(front)
            fv = front[2]
            dis_gap = front[0] - ego[0] - (ego[4] + front[4])/2
        if dis_gap > 100:
            dis_gap = -1
            fv = -1
        return v, fv, dis_gap, direction
