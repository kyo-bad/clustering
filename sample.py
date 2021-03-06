#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sklearn import datasets
from clustering import HAC


if __name__ == "__main__":

    print('iris data')
    iris = datasets.load_iris()

    print("Hierarchical Agglomerative clustering")
    hac = HAC(iris.data, iris.target)
    hac.draw_dendrogram(p=3,truncate_mode='lastp')
    hac.clustering(3)  # 今回は3種類のラベルなので試しに3でクラスタリング
