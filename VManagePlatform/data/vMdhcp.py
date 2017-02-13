#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from VManagePlatform.models import VmDHCP
from VManagePlatform.apps.Base import BaseLogging

class VMDhcp(object):
    @staticmethod
    def insertVmDhcp(data):
        try:
            dhcp = VmDHCP.objects.create(**data)
            return dhcp
        except Exception,e:
            BaseLogging.Logger("[添加DHCP] 状态：[失败] 失败原因："+str(e), level='error')
            return False
        
    @staticmethod
    def listVmDhcp(c=None,p=None):           
        if p and c is not None:
            return VmDHCP.objects.all().order_by("-id")[c:p] 
        else:
            return VmDHCP.objects.all().order_by("-id")   

    @staticmethod
    def selectOneId(id):
        try:
            return  VmDHCP.objects.get(id=id)
        except Exception,e:
            return False
        
    @staticmethod
    def updateisAlive(id,isAlive):
        try:
            return  VmDHCP.objects.filter(id=id).update(isAlive=isAlive)
        except Exception,e:
            return False        

    @staticmethod
    def updateStatus(id,status):
        try:
            return  VmDHCP.objects.filter(id=id).update(status=status)
        except Exception,e:
            return False  
        
    @staticmethod
    def deleteStatus(id):
        try:
            return  VmDHCP.objects.filter(id=id).delete()
        except Exception,e:
            return e         
        
    @staticmethod
    def selectOneMode(mode):
        try:
            return  VmDHCP.objects.get(mode=mode)
        except Exception,e:
            return False  