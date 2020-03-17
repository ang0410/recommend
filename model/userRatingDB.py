#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 10:39:46 2019

@author: ang434
"""

import sqlite3
import csv
import time
import json

class userRatingData:
    
    ratingDBPath = 'turiData/rating.db'
    ratingCSVPath = 'turiData/ratings.csv'
    
    def connnetDB(self):
        return sqlite3.connect(self.ratingDBPath, check_same_thread = False, timeout=30)
        print "Opened database successfully";
        
    def creatTable(self):
        conn = self.connnetDB();

        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS Rating
               (
               ID INTEGER PRIMARY KEY   AUTOINCREMENT,
               userId            INT    NOT NULL,
               itemId            INT    NOT NULL,
               rating            INT    NOT NULL,
               timestamp         INT    NOT NULL);''')
        print "Table created successfully";
        conn.commit()
        conn.close()
        
    def updateData(self, userData):

        conn = self.connnetDB();
        c = conn.cursor()
        
        #判斷Table是否存在
        try:
            c.execute('''CREATE TABLE IF NOT EXISTS Rating
               (
               ID INTEGER PRIMARY KEY   AUTOINCREMENT,
               userId            INT    NOT NULL,
               itemId            INT    NOT NULL,
               rating            INT    NOT NULL,
               timestamp         INT    NOT NULL);''')
        except:
            print('CREATE False')

        cursor = c.execute("SELECT userId, itemId, rating, timestamp from Rating where userId=%s AND itemId=%s" 
                           % (userData['userId'],userData['itemId']))
        
        #判斷資料是否已經存在
        if len(cursor.fetchall()) <= 0:
            
            #新增使用者資料
            c.execute('INSERT INTO Rating (userId,itemId,rating,timestamp) \
                      VALUES (%s, %s, %s, %s)' 
                      % (userData['userId'],userData['itemId'],userData['rating'],self.currentTimestamp())
                      );
        else:
            #更新使用者資料
            c.execute("UPDATE Rating set rating=%s,timestamp=%s where userId=%s AND itemId=%s" 
                  % (userData['rating'], self.currentTimestamp(), userData['userId'], userData['itemId']))
        
        conn.commit()
        conn.close()
    
    def deleteData(self, userData):
        conn = self.connnetDB();
        c = conn.cursor()

        c.execute("DELETE from Rating where userId=%d AND itemId=%d;"
                  % (userData['userId'],userData['itemId']))
        conn.commit()
        conn.close()
        
    def getUserRatingInfo(self, userId):
        conn = self.connnetDB();
        c = conn.cursor()
        c.execute("SELECT itemId, rating from Rating where userId=%s;" % (userId))
        infoList = c.fetchall()
        
        infoJson = []
        for info in infoList:
            jsonStr = {'itemId': info[0], 'rating': info[1]}
            infoJson.append(jsonStr)
  
        conn.commit()
        conn.close()
        
        print json.dumps(infoJson)
        return json.dumps(infoJson)
        
    def transformDBToCSV(self):
        
        conn = self.connnetDB();
        cursor = conn.cursor()
        cursor.execute("select userId, itemId, rating, timestamp from Rating;")
        #with open("out.csv", "w", newline='') as csv_file:  # Python 3 version    
        with open(self.ratingCSVPath, "wb") as csv_file:              # Python 2 version
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description]) # write headers
            csv_writer.writerows(cursor)
            
    def currentTimestamp(self):
        #timestamp
        return int(time.time())

 
if __name__ == '__main__':
   userDB = userRatingData()
   #userDB.creatTable()
   #userData={'userId': 3, 'itemId': 54, 'rating': 5, 'timestamp': 4324}
   #userDB.selectData(userData = userData)
   #userDB.insertData(userData = userData)
   #userDB.updateData(userData = userData)
   #userDB.deleteData(userData = userData)
   #userDB.coverDBToCSV()
   #userDB.currentTimestamp()
   userDB.getUserRatingInfo(userId=367)
   
