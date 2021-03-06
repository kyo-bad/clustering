#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
クラスタリングでよく使われる処理を関数化
ラベルがわかっているもののクラスタリングを中心に
クラスタの分布とかデータの内訳を返す
"""

import sys
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster, cophenet, ward
from scipy.spatial.distance import pdist
import matplotlib.pyplot as plt
import seaborn as sns
from tools import sort_smart, view_breakdown


def fancy_dendrogram(*args, **kwargs):
    max_d = kwargs.pop('max_d', None)
    if max_d and 'color_threshold' not in kwargs:
        kwargs['color_threshold'] = max_d
    annotate_above = kwargs.pop('annotate_above', 0)

    ddata = dendrogram(*args, **kwargs)

    if not kwargs.get('no_plot', False):
        plt.title('Hierarchical Clustering Dendrogram (truncated)')
        plt.xlabel('sample index or (cluster size)')
        plt.ylabel('distance')
        for i, d, c in zip(ddata['icoord'], ddata['dcoord'], ddata['color_list']):
            x = 0.5 * sum(i[1:3])
            y = d[1]
            if y > annotate_above:
                plt.plot(x, y, 'o', c=c)
                plt.annotate("%.3g" % y, (x, y), xytext=(0, -5),
                             textcoords='offset points',
                             va='top', ha='center')
        if max_d:
            plt.axhline(y=max_d, c='k')
    return ddata


class HAC:
    """凝集型階層的クラスタリング"""

    def __init__(self, data: np.ndarray, label: np.ndarray, method="ward", metric="euclidean"):
        """
        :param data: 学習データ
        :param label: ラベル
        :param method: 連結の方法
        :param metric: ベクトル間の距離
        """
        self.data = data
        self.label = label
        self.method = method
        self.metric = metric
        if method == "ward":
            self.Z = ward(data)
        else:
            self.distance = pdist(self.data, metric = self.metric)
            self.Z = linkage(self.distance, method=self.method)
        c, coph_dists = cophenet(self.Z, pdist(self.data, metric=self.metric))
        print("Cophenetic Correlation Coefficient: ", c)

    def set_distance_array(self, dArray: list, method = "average"):
        self.distance = dArray
        self.method = method
        self.Z = linkage(self.distance, method=self.method)
        c, coph_dists = cophenet(self.Z, self.distance)
        print("Cophenetic Correlation Coefficient: ", c)

    def clustering(self, n: int = 6, name: str = False, kind: str ='bar', isplot: bool = True):
        """
        :param n: クラスタ数
        :param name: 結果ファイルの保存名
        :param kind: グラフの可視化方法
        :param isplot: 可視化するかしないか
        """
        self.pred = fcluster(self.Z, n, criterion="maxclust")
        self.report = view_breakdown(self.label, self.pred, kind=kind, isplot=isplot)

    def draw_dendrogram(self, name: str = False, **kwargs):
        """
        :param name: 保存ファイル名
        :param kwargs: 各種パラメータ
        max_d=cut-off line
        """
        try:
            labels = np.array([str(str(i) + "_" + str(j)) for i, j in zip(self.label, self.pred)])
        except:
            labels = self.label

        plt.figure()
        fancy_dendrogram(self.Z, labels=labels,
                         show_contracted=True, leaf_font_size=10, **kwargs)
        if name is not False:
            plt.savefig(name)
        plt.show()

    def set_tree_structure(self):
        """ツリー構造を表現"""
        self.c_index = {}  # 結合されていった順に,クラスタ内のインデックスが入る
        self.tree = {}
        for i in range(0, len(self.Z)):
            self.tree[i] = [int(self.Z[i, 0]), int(self.Z[i, 1])]  # Zのクラスタ連結部分のみ抽出

            index = np.array([], dtype=np.int)
            if self.Z[i, 0] < len(self.data):
                index = np.hstack([index, int(self.Z[i, 0])])
            else:
                index = np.hstack([index, self.c_index[int(self.Z[i, 0]) - len(self.data)]])
            if self.Z[i, 1] < len(self.data):
                index = np.hstack([index, int(self.Z[i, 1])])
            else:
                index = np.hstack([index, self.c_index[int(self.Z[i, 1]) - len(self.data)]])
            self.c_index[i] = sorted(index.tolist())

    def get_tree_structure(self, index):
        """
        :param index: クラスタインデックス(0が最初の結合)
        :return: 階層構造
        """
        if self.tree[index][0] < len(self.data):
            cls1 = self.tree[index][0]
        else:
            cls1 = self.c_index[self.tree[index][0] - len(self.data)]
        if self.tree[index][1] < len(self.data):
            cls2 = self.tree[index][1]
        else:
            cls2 = self.c_index[self.tree[index][1] - len(self.data)]
        return (cls1,cls2)

    def z_threshold(self, threshold: float):
        """
        :param threshold: 閾値
        :return: [閾値,クラスタ数]
        """
        pred = fcluster(self.Z, threshold, criterion='distance')
        key = sorted(list(set(pred)), key=int)
        return [threshold, len(key)]
