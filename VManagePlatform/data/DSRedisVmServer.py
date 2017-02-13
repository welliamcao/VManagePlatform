# -*- coding=utf-8 -*-
'''
@author: Welliam<welliam.cao@ijinzhuan.com> 
@version:1.0 2016年12月06日
'''
import json
from VManagePlatform.apps.APBase import APBase

class DsRedisVManage():
    class rshVmInstance(object):
        @staticmethod
        def hget(vmserver):
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hget('rsh_instance_info', vmserver)    
            if data:return json.loads(data)
            else:return {}
            
        @staticmethod
        def hgetall():
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hgetall('rsh_instance_info')  
            if data:return data
            else:return {}

        @staticmethod
        def hset(vmserver,data):
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            redisConn.hset('rsh_instance_info', vmserver, data)
            
    class rshVmServer(object):
        @staticmethod
        def hget(vmserver):
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hget('rsh_server_snap', vmserver)
            if data:return json.loads(data)
            else:return {}   
                 
        @staticmethod
        def hgetall():
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hgetall('rsh_server_snap')
            if data:return json.loads(data)
            else:return {}
            
    class rshVmStorage(object):
        @staticmethod
        def hget(vmserver):
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hget('rsh_storage_snap', vmserver)
            if data:return json.loads(data)
            else:return {}    
            
        @staticmethod
        def hgetall():
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hgetall('rsh_storage_snap')    
            if data:return json.loads(data)
            else:return {} 

        @staticmethod
        def hdel(vmserver):
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            redisConn.hdel('rsh_storage_snap',vmserver)               
               
    class rshVmPerform(object):                  
        @staticmethod
        def hgetall(vmserver):  
            redisConn = APBase.getRedisConnection(APBase.DS_REDIS_SNAP_VMANAGE)
            data = redisConn.hgetall('rsh_perform_' + vmserver)    
            if data:return data
            else:return {}                   