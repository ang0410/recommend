# -*- coding: utf-8 -*-
from preprocess import Channel
from workflow.cf_workflow import run as user_cf
from workflow.if_workflow import run as user_if
from workflow.rsif_workflow import run as user_rsif
from workflow.lfm_workflow import run as lfm
from workflow.prank_workflow import run as prank
from flask import Flask, jsonify, abort, make_response, request

from workflow.turi_workflow import runByUser as tcUser
from workflow.turi_workflow import runByItems as tcItems
from workflow.turi_workflow import runPopular as tcPopular
from workflow.turi_workflow import runSaveUserData as tcSaveUserData
from workflow.turi_workflow import runGetUserData as tcGetUserData

app = Flask(__name__)

@app.route('/recommend/<method_name>', methods=['GET', 'POST'])
def methods(method_name):
     
    if method_name == 'preprocess':
        Channel().process()
        
    elif method_name == 'cf':
        return cfMed()
    
    elif method_name == 'rsif':
        return rsifMed()
    
    elif method_name == 'if':
        return ifMed()
    
    elif method_name == 'lfm':
        return lfmMed()
        
    elif method_name == 'prank':
        return prankMed()
    
    elif method_name == 'tcUser':
        return tcUserMed()
    
    elif method_name == 'tcItems':
        return tcItemsMed()
    
    elif method_name == 'tcPopular':
        return tcPopularMed()
    
    elif method_name == 'setData':
        return tcSetData()
    
    elif method_name == 'getData':
        return tcGetData()
    
    else:
        abort(404)
        
        
def cfMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
            
    return jsonify(user_cf(user_id=userId, topItems=topN))

def ifMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
            
    return jsonify(user_if(user_id=userId, topItems=topN))

def rsifMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
            
    return jsonify(user_rsif(user_id=userId, topItems=topN))

def lfmMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
        
    return jsonify(lfm(userId=userId, topItems=topN))

def prankMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
        
    return jsonify(prank(userId=userId, topItems=topN))

def tcUserMed():
    userId = request.args.get('userId', default=None, type=int)
    if userId is None:
        abort(404)

    topN = request.args.get('topN', default=10, type=int)
        
    return tcUser(userId=userId, topItems=topN)

def tcItemsMed():
    itemId = request.args.get('itemId', default=None, type=int)
    if itemId is None:
        abort(404)
            
    topN = request.args.get('topN', default=10, type=int)
        
    return tcItems(itemId=itemId, topItems=topN)

def tcPopularMed():
    userId = request.args.get('userId', default=None, type=int)
            
    topN = request.args.get('topN', default=10, type=int)
    return tcPopular(userId=userId, topItems=topN)

def tcSetData():
    contentType = request.headers['Content-Type']
    
    if contentType == 'application/json':
        jsonStr = request.json
        infoArray = jsonStr['info']
        for info in infoArray:
            #key = userId, itemId, rating
            tcSaveUserData(info)
        
        return jsonify(infoArray)
    
    else:
        abort(415)

def tcGetData():
    userId = request.args.get('userId', default=None, type=int)
    return tcGetUserData(userId)
        
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(415)
def errorType_415(error):
    return make_response(jsonify({'error': 'Unsupported Content Type'}), 415)
    
if __name__ == '__main__':
    #app.run(host='192.168.1.241', debug=True)
    app.run(host='127.0.0.1', debug=True)
