# -*- coding: utf-8 -*-
import time
import os
from model.prank import Graph, PersonalRank


def run(userId, topItems):
    assert os.path.exists('data/ratings.csv'), \
        'File not exists in path, run preprocess.py before this.'
    print('Start..')
    start = time.time()
    if not os.path.exists('data/prank.graph'):
        Graph.gen_graph()
    if not os.path.exists('data/prank_{}.model'.format(userId)):
        PersonalRank().train(user_id=userId)
    movies = PersonalRank().predict(user_id=userId, top_n=topItems)
    for movie in movies:
        print(movie)
    return movies
    print('Cost time: %f' % (time.time() - start))
