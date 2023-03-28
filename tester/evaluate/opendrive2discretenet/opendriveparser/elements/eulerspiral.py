# -*- coding: utf-8 -*-

import numpy as np
from scipy import special


class EulerSpiral:
    """ """

    def __init__(self, gamma):
        self._gamma = gamma

    @staticmethod
    def createFromLengthAndCurvature(length, curvStart, curvEnd):
        """
        从给定的螺旋线中，算出参考线曲线中曲率变化的一段的斜率
        具体参见 https://blog.csdn.net/weixin_38533133/article/details/108423271的图25
        :param length: 螺旋线的长度
        :param curvStart: 初始的曲率
        :param curvEnd: 最终的曲率
        :return: 参考线螺旋线阶段的曲率
        """
        # if length is zero, assume zero curvature
        if length == 0:
            return EulerSpiral(0)
        return EulerSpiral(1 * (curvEnd - curvStart) / length)

    def calc(self, s, x0=0, y0=0, kappa0=0, theta0=0):
        """

        Args:
          s: 
          x0:  (Default value = 0)
          y0:  (Default value = 0)
          kappa0:  (Default value = 0)
          theta0:  (Default value = 0)

        Returns:

        """

        # Start
        C0 = x0 + 1j * y0

        if self._gamma == 0 and kappa0 == 0:
            # Straight line
            Cs = C0 + np.exp(1j * theta0 * s)

        elif self._gamma == 0 and kappa0 != 0:
            # Arc
            Cs = C0 + np.exp(1j * theta0) / kappa0 * (
                np.sin(kappa0 * s) + 1j * (1 - np.cos(kappa0 * s))
            )

        else:
            # Fresnel integrals
            Sa, Ca = special.fresnel(
                (kappa0 + self._gamma * s) / np.sqrt(np.pi * np.abs(self._gamma))
            )
            Sb, Cb = special.fresnel(kappa0 / np.sqrt(np.pi * np.abs(self._gamma)))

            # Euler Spiral
            Cs1 = np.sqrt(np.pi / np.abs(self._gamma)) * np.exp(
                1j * (theta0 - kappa0 ** 2 / 2 / self._gamma)
            )
            Cs2 = np.sign(self._gamma) * (Ca - Cb) + 1j * Sa - 1j * Sb

            Cs = C0 + Cs1 * Cs2

        # Tangent at each point
        theta = self._gamma * s ** 2 / 2 + kappa0 * s + theta0

        return Cs.real, Cs.imag, theta
