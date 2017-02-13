#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
import os

def getNfsImageDir():
    '''获取NFS目录列表'''
    imageDir = []
    try:
        with open('/etc/exports') as f:
            for line in f.readlines():
                imageDir.append(line.replace('\n','').split(' ')[0])
    except:
        return False
    return imageDir

def getImageList(dir_path):
    '''获取路径下面的镜像列表'''
    fileList = []
    try:
        for file in os.listdir(dir_path):
            if(os.path.isfile(dir_path + '/' + file)):fileList.append(file)  
    except:
        return fileList
    return fileList