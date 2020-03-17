# -*- coding: utf-8 -*-
import time
import os
from model.cf import UserCf


def run(user_id, topItems):
    assert os.path.exists('data/ratings.csv'), \
        'File not exists in path, run preprocess.py before this.'
    print('Start..')
    start = time.time()
    movies = UserCf().calculate(target_user_id=user_id, top_n=topItems)
    for movie in movies:
        print(movie)
    return movies
    print('Cost time: %f' % (time.time() - start))
