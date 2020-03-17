#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 17:16:21 2019

@author: edward
"""

from model.turiRecommend import recommendTuriCreat as turi

def runByItems(itemId, topItems):
    movies = turi().recommendByItems(itemId=itemId, topN=topItems)
    return movies
    
def runByUser(userId, topItems):
    movies = turi().recommendByUser(userId=userId, topN=topItems)
    return movies
    
def runPopular(userId, topItems):
    movies = turi().getPopularForUser(userId=userId, topN=topItems)
    return movies

def runSaveUserData(userData):
    turi().saveUserRatingData(userData=userData)
    return 'finish'

def runGetUserData(userId):
    return turi().getUserRatingData(userId=userId)