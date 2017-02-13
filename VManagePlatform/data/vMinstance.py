#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from VManagePlatform.models import VmInstance_Template
from VManagePlatform.models import VmServerInstance

class TempInstance(object):
    @staticmethod
    def insertVmTemp(name,cpu,mem,disk):
        try:
            temp = VmInstance_Template(name=name,cpu=cpu,
                                       mem=mem,disk=disk)
            temp.save()
            return temp
        except Exception,e:
            return str(e)
        
    @staticmethod   
    def listVmTemp(c=None,p=None):           
        if p and c is not None:
            return VmInstance_Template.objects.all().order_by("-id")[c:p] 
        else:
            return VmInstance_Template.objects.all().order_by("-id")
        
    @staticmethod
    def delVmTemp(name):
        try:
            return  VmInstance_Template.objects.filter(name=name).delete()
        except Exception,e:
            return str(e)    
    
    @staticmethod
    def selectVmTemp(id):
        try:
            return  VmInstance_Template.objects.get(id=id)
        except Exception,e:
            return str(e)   
        

class VmInstance(object):
    @staticmethod
    def insertInstance(data):
        if isinstance(data,dict):
            try:
                result = VmServerInstance.objects.create(**data)
                return result
            except Exception,e:
                return str(e)
        else:return False  
    
    @staticmethod
    def deleteInstance(server,name):
        try:
            return VmServerInstance.objects.get(server=server,name=name).delete()
        except Exception,e:
            return str(e)
        
    @staticmethod
    def updateInstance(id,data):
        try:
            result = VmServerInstance.objects.filter(id=id).update(**data)
            return result
        except Exception,e:
            return str(e)
    
    @staticmethod
    def countInstnace(status=None):
        if isinstance(status,int):return VmServerInstance.objects.filter(status=status)
        else:return VmServerInstance.objects.all().order_by("-id")
        
