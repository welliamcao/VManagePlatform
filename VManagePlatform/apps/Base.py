# -*- coding=utf-8 -*-
import logging
from logging.handlers import RotatingFileHandler
import os,sys



gProDir = os.path.dirname(os.path.abspath(sys.argv[ 0])) + '/'
gProDir = gProDir.replace('\\','/')
gLoggerName = 'VManagePlatform'
gLoggerFilePath = gProDir + '/logs/'
gLoggerFileName = 'VManagePlatform.log'
if not os.path.isdir(gLoggerFilePath):
    os.makedirs(gLoggerFilePath)
gLogger = logging.getLogger(gLoggerName)
gLoggerFormatter = logging.Formatter("[%(asctime)s]: %(message)s","%Y-%m-%d %H:%M:%S")
fileHandler = RotatingFileHandler(gLoggerFilePath + gLoggerFileName, mode='a' , maxBytes=10 *1024 *1024 , backupCount=4)
fileHandler.setFormatter(gLoggerFormatter)
fileHandler.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(gLoggerFormatter)
streamHandler.setLevel(logging.DEBUG)   
gLogger.addHandler(fileHandler)
gLogger.addHandler(streamHandler)
gLogger.setLevel(logging.DEBUG)

class  BaseLogging(object):   
    @staticmethod 
    def Logger(msg,level=None):
        if level == 'error':return gLogger.error(msg)
        elif level == 'warn':return gLogger.warn(msg)
        elif level == 'info':return gLogger.info(msg)  
        elif level == 'debug':return gLogger.debug(msg) 