#!/usr/bin/python
# coding:utf8
"""
Created on Mon Jan 28 15:12:38 2019

@author: ang434
"""

import sys
import math
import random
import pandas as pd
import cPickle as pickle
import os
import time
from operator import itemgetter

# 作用：使得随机数据可预测
random.seed(0)


class ItemBasedCF():
    ''' TopN recommendation - ItemBasedCF '''

    itemcf_dict_path = 'ItemCF_Data/itemCF_%s.dic'
    movies_csv_patch = 'data/movies.csv'
    
    def __init__(self):
        self.trainset = {}
        self.testset = {}

        # n_rec_movie: top 10个推荐结果
        self.n_rec_movie = 10

        # user_sim_mat: 电影之间的相似度， movie_popular: 电影的出现次数， movie_count: 总电影数量
        self.movie_sim_mat = {}
        self.movie_popular = {}
        self.movie_count = 0

        print >> sys.stderr, 'Recommended movie number = %d' % self.n_rec_movie

        self.file_path = 'data/ratings.csv'
        self._init_frame()

    def _init_frame(self):
        self.frame = pd.read_csv(self.file_path)

    def generate_dataset(self, pivot=0.7):
        """loadfile(加载文件，将数据集按照7:3 进行随机拆分)

        Args:
            pivot      拆分比例
        """
        trainset_len = 0
        testset_len = 0
        
        for row in self.frame.itertuples(index=True, name='Pandas'):
            user = getattr(row, "UserID")
            movie = getattr(row, "MovieID")
            rating = getattr(row, "Rating")
            if (random.random() < pivot):

                # dict.setdefault(key, default=None)
                # key -- 查找的键值
                # default -- 键不存在时，设置的默认键值
                self.trainset.setdefault(user, {})
                self.trainset[user][movie] = int(rating)
                trainset_len += 1
            else:
                self.testset.setdefault(user, {})
                self.testset[user][movie] = int(rating)
                testset_len += 1

        print >> sys.stderr, '分离训练集和测试集成功'
        print >> sys.stderr, 'train set = %s' % trainset_len
        print >> sys.stderr, 'test set = %s' % testset_len

    def calc_movie_sim(self):
        """calc_movie_sim(计算用户之间的相似度)"""

        print >> sys.stderr, 'counting movies number and popularity...'

        # 统计在所有的用户中，不同电影的总出现次数， user, movies
        self.calculate_all_user_diff_items()
        print >> sys.stderr, 'count movies number and popularity success'

        # save the total number of movies
        self.movie_count = len(self.movie_popular)
        print >> sys.stderr, 'total movie number = %d' % self.movie_count

        # 统计在相同用户时，不同电影同时出现的次数
        itemsim_mat = self.calculate_same_user_diff_items()

        # calculate similarity matrix
        print >> sys.stderr, 'calculating movie similarity matrix...'
        self.calculate_similarity_matrix(itemsim_mat = itemsim_mat)
     
    def calculate_all_user_diff_items(self):
        for _, movies in self.trainset.items():
            for movie in movies:
                # count item popularity
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1
                
    def calculate_same_user_diff_items(self):
        itemsim_mat = self.movie_sim_mat
        print >> sys.stderr, 'building co-rated users matrix...'
        # user, movies
        for _, movies in self.trainset.items():
            for m1 in movies:
                for m2 in movies:
                    if m1 != m2:
                        itemsim_mat.setdefault(m1, {})
                        itemsim_mat[m1].setdefault(m2, 0)
                        itemsim_mat[m1][m2] += 1
        print >> sys.stderr, 'build co-rated users matrix success'
        return itemsim_mat
    
    def calculate_similarity_matrix(self, itemsim_mat):
        simfactor_count = 0
        PRINT_STEP = 2000000
        
        for m1, related_movies in itemsim_mat.items():
            for m2, count in related_movies.iteritems():
                # 余弦相似度
                itemsim_mat[m1][m2] = count / math.sqrt(
                    self.movie_popular[m1] * self.movie_popular[m2])
                simfactor_count += 1
                # 打印进度条
                if simfactor_count % PRINT_STEP == 0:
                    print >> sys.stderr, 'calculating movie similarity factor(%d)' % simfactor_count
        
        self.save()
        print >> sys.stderr, 'calculate movie similarity matrix(similarity factor) success'
        print >> sys.stderr, 'Total similarity factor number = %d' % simfactor_count
        
    # @profile
    def recommend(self, target_user_id=1, top_n=10):
    
        # 将数据按照 7:3的比例，拆分成：训练集和测试集，存储在usercf的trainset和testset中
        self.currentUserId = target_user_id
        self.generate_dataset(pivot=0.7)
        # 计算用户之间的相似度
        
        if os.path.exists(self.itemcf_dict_path % str(self.currentUserId)):
            print >> sys.stderr, 'load 相似矩陣...'
            start = time.time()
            self.movie_sim_mat = self.load()
            print('Cost time: %f' % (time.time() - start))
            print >> sys.stderr, '完成相似矩陣...'
        else:
            print >> sys.stderr, '產生相似矩陣...'
            start = time.time()
            self.calc_movie_sim()
            print('Cost time: %f' % (time.time() - start))
            print >> sys.stderr, '完成相似矩陣...'

        """recommend(找出top K的电影，对电影进行相似度sum的排序，取出top N的电影数)

        Args:
            user       用户
        Returns:
            rec_movie  电影推荐列表，按照相似度从大到小的排序
        """
        ''' Find K similar movies and recommend N movies. '''
        K = top_n*2
        #N = self.n_rec_movie
        rank = {}
        watched_movies = self.trainset[target_user_id]

        # 计算top K 电影的相似度
        # rating=电影评分, w=不同电影出现的次数
        # 耗时分析：98.2%的时间在 line-154行
        for movie, rating in watched_movies.iteritems():
            for related_movie, w in sorted(
                    self.movie_sim_mat[movie].items(),
                    key=itemgetter(1),
                    reverse=True)[0:K]:
                if related_movie in watched_movies:
                    continue
                rank.setdefault(related_movie, 0)
                rank[related_movie] += w * rating
                
        # return the N best movies
        movieIDList = [movie for movie, _ in sorted(rank.items(), key=itemgetter(1), reverse=True)[0:top_n]]
        moviesData = pd.read_csv(self.movies_csv_patch)
        recommemdMovies = [moviesData[moviesData['MovieID'] == movieID]['Title'].values[0] for movieID in movieIDList]

        recommemdJson = []
        for index, _ in enumerate(movieIDList):
            jsonStr = '{movieID: %s, name: %s}' % (movieIDList[index], recommemdMovies[index])
            recommemdJson.append(jsonStr)
            
        return recommemdJson

    def evaluate(self):
        ''' return precision, recall, coverage and popularity '''
        print >> sys.stderr, 'Evaluation start...'

        # 返回top N的推荐结果
        N = self.n_rec_movie
        # varables for precision and recall
        # hit表示命中(测试集和推荐集相同+1)，rec_count 每个用户的推荐数， test_count 每个用户对应的测试数据集的电影数
        hit = 0
        rec_count = 0
        test_count = 0
        # varables for coverage
        all_rec_movies = set()
        # varables for popularity
        popular_sum = 0

        # enumerate将其组成一个索引序列，利用它可以同时获得索引和值
        # 参考地址：http://blog.csdn.net/churximi/article/details/51648388
        for i, user in enumerate(self.trainset):
            if i > 0 and i % 500 == 0:
                print >> sys.stderr, 'recommended for %d users' % i
            test_movies = self.testset.get(user, {})
            rec_movies = self.recommend(user)

            # 对比测试集和推荐集的差异 movie, w
            for movie, _ in rec_movies:
                if movie in test_movies:
                    hit += 1
                all_rec_movies.add(movie)
                # 计算用户对应的电影出现次数log值的sum加和
                popular_sum += math.log(1 + self.movie_popular[movie])
            rec_count += N
            test_count += len(test_movies)

        precision = hit / (1.0 * rec_count)
        recall = hit / (1.0 * test_count)
        coverage = len(all_rec_movies) / (1.0 * self.movie_count)
        popularity = popular_sum / (1.0 * rec_count)

        print >> sys.stderr, 'precision=%.4f \t recall=%.4f \t coverage=%.4f \t popularity=%.4f' % (
            precision, recall, coverage, popularity)


    def save(self):
        with open(self.itemcf_dict_path % str(self.currentUserId), 'wb') as f:
            pickle.dump(self.movie_sim_mat, f, protocol=pickle.HIGHEST_PROTOCOL)
  
    
    def load(self):
        with open(self.itemcf_dict_path % str(self.currentUserId), 'rb') as f:
            simMatrix = pickle.load(f)
            return simMatrix

       
"""if __name__ == '__main__':
    #ratingfile = '/Users/ang434/Desktop/RecommenderSystems-master/data/ml-1m/ratings'
    #ratingfile = 'db/16.RecommenderSystems/ml-100k/u.data'
    ratingfile = 'data/ratings.dat'

    # 创建ItemCF对象
    itemcf = ItemBasedCF()
    # 将数据按照 7:3的比例，拆分成：训练集和测试集，存储在usercf的trainset和testset中
    itemcf.generate_dataset(ratingfile, pivot=0.7)
    # 计算用户之间的相似度
    itemcf.calc_movie_sim()
    # 评估推荐效果
    # itemcf.evaluate()
    # 查看推荐结果用户
    user = "2"
    print("Recommend", itemcf.recommend(user))
    print("---", itemcf.testset.get(user, {}))"""
