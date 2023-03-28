# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/26 20:25
import numpy as np
from numpy.polynomial import polynomial as P
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt


def find_entrance_road(roads):
    entrance_roads_id = []
    for road in roads:
        if road.attrib['junction'] != '-1':
            predecessor = road.find('link').find('predecessor')
            if predecessor.attrib['elementType'] == 'road':
                entrance_roads_id.append(predecessor.attrib['elementId'])
                entrance_roads_id = list(set(entrance_roads_id))  # 列表去重
    # print(entrance_roads_id)

    return entrance_roads_id


def calc_width(width, road_mark, ds):
    s_offset = float(width.attrib['sOffset'])
    ds = ds - s_offset
    width_coefficient = [float(width.attrib['a']), float(width.attrib['b']),
                         float(width.attrib['c']), float(width.attrib['d'])]
    lane_width = P.polyval(ds, width_coefficient)
    # lane_width = float(width.attrib['a']) + float(width.attrib['b']) * ds + float(
    #     width.attrib['c']) * ds ** 2 + float(width.attrib['d']) * ds ** 3
    if road_mark == "" or road_mark.attrib["type"] == "none":
        pass
    else:
        lane_width += float(road_mark.attrib['width'])
    return lane_width


def alpha_shape(points, alpha, only_outer=True):
    """
    Compute the alpha shape (concave hull) of a set of points.
    :param points: np.array of shape (n,2) points.
    :param alpha: alpha value.
    :param only_outer: boolean value to specify if we keep only the outer border
    or also inner edges.
    :return: set of (i,j) pairs representing edges of the alpha-shape. (i,j) are
    the indices in the points array.
    """
    assert points.shape[0] > 3, "Need at least four points"

    def add_edge(edges, i, j):
        """
        Add an edge between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            assert (j, i) in edges, "Can't go twice over same directed edge right?"
            if only_outer:
                # if both neighboring triangles are in shape, it's not a boundary edge
                edges.remove((j, i))
            return
        edges.add((i, j))

    tri = Delaunay(points)

    edges = set()
    # Loop over triangles:
    # ia, ib, ic = indices of corner points of the triangle

    for ia, ib, ic in tri.vertices:
        pa = points[ia]
        pb = points[ib]
        pc = points[ic]
        # Computing radius of triangle circumcircle
        # www.mathalino.com/reviewer/derivation-of-formulas/derivation-of-formula-for-radius-of-circumcircle
        a = np.sqrt((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2)
        b = np.sqrt((pb[0] - pc[0]) ** 2 + (pb[1] - pc[1]) ** 2)
        c = np.sqrt((pc[0] - pa[0]) ** 2 + (pc[1] - pa[1]) ** 2)
        s = (a + b + c) / 2.0
        area = np.sqrt(s * (s - a) * (s - b) * (s - c))
        circum_r = a * b * c / (4.0 * area)
        # print('circum_r', circum_r)

        if circum_r < alpha:
            add_edge(edges, ia, ib)
            add_edge(edges, ib, ic)
            add_edge(edges, ic, ia)
    return edges


if __name__ == "__main__":
    pts = [(319, 320), (125, 198), (250, 366), (129, 182), (262, 375), (235, 344), (248, 369), (367, 261), (196, 307),
           (163, 286)]

    pts = np.array(pts).astype(np.int32)
    points = pts
    # Computing the alpha shape
    # 通过这里的alpha阈值，可以得到不同的外接多边形。阈值选的不好，可能得不到外接多边形。比如选的太小。
    edges = alpha_shape(points, alpha=200, only_outer=True)
    print('edges', edges)
    edges_ = np.array(list(edges)).ravel()
    print(edges_)
    a = [list(points[idx]) for idx in edges_]
    print(a)

    # Plotting the output
    fig, ax = plt.subplots(figsize=(6,4))
    ax.axis('equal')
    plt.plot(points[:, 0], points[:, 1], '.',color='b')
    for i, j in edges:
        # print(points[[i, j], 0], points[[i, j], 1])
        ax.plot(points[[i, j], 0], points[[i, j], 1], color='red')
        pass
    ax.invert_yaxis()
    plt.show()
