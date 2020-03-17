#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 20 09:30:04 2019

@author: ang434
"""

import turicreate as tc
import os
import json
import random

from model.userRatingDB import userRatingData as ratingDB

class recommendTuriCreat:
    
    UserModelPath = 'model/UserModel.model'
    ItemModelPath = 'model/ItemModel.model'
    PopularModelPath = 'model/PopularModel.model'
    ratingDataPath = 'turiData/ratings.csv'
    ratingDataPathTest = 'turiData/ratingDB.csv'
    itemDataPath = 'turiData/movies.csv'
    userKey = 'userId'
    itemKey = 'itemId'
    ratingKey = 'rating'
    timestampKey = 'timestamp'

    def recommendByUser(self, userId, topN=10):
        
        if os.path.exists(self.UserModelPath):
            model = tc.load_model(self.UserModelPath)
        else:
            model = self.trainUserBasedCF()
            
        results = model.recommend(users=[userId], k=topN, diversity=random.uniform(1, 3))
        items = self.getRecommendJson(topN, results[self.itemKey])
        return items
        
    def trainUserBasedCF(self):
        actions = tc.SFrame.read_csv(self.ratingDataPath)
        actions = self.normalizedRatingData(actions)
        model = tc.recommender.create(actions, self.userKey, self.itemKey)
        model.save(self.UserModelPath)
        return model
    
    def recommendByItems(self, itemId, topN=10):

        if os.path.exists(self.ItemModelPath):
            model = tc.load_model(self.ItemModelPath)
        else:
            model = self.trainItemBasedCF()
            
        results = model.get_similar_items(items=[itemId], k=topN)
        items = self.getRecommendJson(topN, results['similar'])
        return items
        
    def trainItemBasedCF(self):
        actions = tc.SFrame.read_csv(self.ratingDataPath)
        actions = self.normalizedRatingData(actions)
        model = tc.item_similarity_recommender.create(actions, self.userKey, self.itemKey)
        model.save(self.ItemModelPath)
        return model
    
    def getRecommendJson(self, top_n, interestList):
        recommemdJson = [itemID for itemID in interestList]
        return json.dumps(recommemdJson)
    
    def getPopularForUser(self, userId, topN=10):
        
        if os.path.exists(self.PopularModelPath):
            model = tc.load_model(self.PopularModelPath)
        else:
            model = self.trainPopular()
            
        results = model.recommend(users=[userId], k=topN, diversity=random.uniform(1, 3))
        items = self.getRecommendJson(topN, results[self.itemKey])
        return items
        
    def trainPopular(self):
        actions = tc.SFrame.read_csv(self.ratingDataPath)
        actions = self.normalizedRatingData(actions)
        model = tc.popularity_recommender.create(actions, self.userKey, self.itemKey)
        model.save(self.PopularModelPath)
        return model
        
    def saveUserRatingData(self, userData):
        ratingDB().updateData(userData = userData)
        ratingDB().transformDBToCSV()
        
    def getUserRatingData(self, userId):
        return ratingDB().getUserRatingInfo(userId = userId)
    
    def normalizedRatingData(self, csvFile):
        for c in csvFile.column_names():
            if c == self.ratingKey:
                csvFile[c] = (csvFile[c] - csvFile[c].mean()) / csvFile[c].std()
        return csvFile

if __name__ == '__main__':
    turi = recommendTuriCreat()
    #turi.recommendByItems(20, 5)
    turi.trainUserBasedCF()
    #turi.saveUserRatingData(userData={'userId': 353, 'movieId': 463, 'rating': 2, 'timestamp': 239247823})
