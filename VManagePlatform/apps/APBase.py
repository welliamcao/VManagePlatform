# -*- coding=utf-8 -*-
'''
应用基类（每次应用启动时，都必须调用基类的初始化方法）
@author: Welliam<welliam.cao@ijinzhuan.com> 
@version:1.0 2016年12月06日
'''
import redis,libvirt
import MySQLdb
from DBUtils.PooledDB import PooledDB
from django.conf import settings

class APBase(object):

    DS_MYSQL_VMANAGE_READ    = 20001
    DS_REDIS_SNAP_VMANAGE    = 30001
    DS_LIBVIRT_VMANAGE = 40001
    
    @staticmethod
    def getRedisConnection(db):
        '''根据数据源标识获取Redis连接池'''
        if db==APBase.DS_REDIS_SNAP_VMANAGE:
            args = settings.REDIS_KWARGS_VMANAGE
            if settings.REDIS_POOLS_VMANAGE==None:
                settings.REDIS_POOLS_VMANAGE = redis.ConnectionPool(host=args.get('host'), port=args.get('port'), db=args.get('db'))
            pools = settings.REDIS_POOLS_VMANAGE         
        connection = redis.Redis(connection_pool=pools)
        return connection
    

    

            
            
            