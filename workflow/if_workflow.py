#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 15:19:00 2019

@author: ang434
"""

import time
import os
from model.itemCF import ItemCF

def run(user_id, topItems):
    assert os.path.exists('data/ratings.csv'), \
        'File not exists in path, run preprocess.py before this.'
    print('Start..')
    start = time.time()
    """movies = ItemCF().calculate(target_user_id=user_id, top_n=topItems)"""
    movies = ItemCF().recommend(target_user_id=user_id, top_n=topItems)
    for movie in movies:
        print(movie)
    return movies
    print('Cost time: %f' % (time.time() - start))