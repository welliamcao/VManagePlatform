#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from VManagePlatform.models import VmServer
from VManagePlatform.apps.Base import BaseLogging

class VMServer(object):
    @staticmethod
    def insertVmServer(server_ip,uri,vm_type,status,hostname):
        try:
            server = VmServer(server_ip=server_ip,uri=uri,hostname=hostname,
                              vm_type=vm_type,status=status)
            server.save()
            return server
        except Exception,e:
            BaseLogging.Logger("[添加主机] 状态：[失败] 失败原因："+str(e), level='error')
            return False
        
    @staticmethod
    def updateVmServer(server_id,instance,mem,cpu_total,mem_per):
        try:
            return  VmServer.objects.filter(id=server_id).update(instance=instance,mem=mem,cpu_total=cpu_total,mem_per=mem_per)
        except Exception,e:
            BaseLogging.Logger("[更新主机] 状态：[失败] 失败原因："+str(e), level='error')
            return str(e)                
    
    @staticmethod
    def updateVmServerStatus(server_id,status,):
        try:
            server = VmServer.objects.get(id=server_id)
            server.status = status
            return server.save()
        except Exception,e:
            BaseLogging.Logger("[更新主机] 状态：[失败] 失败原因："+str(e), level='error')
            return str(e)    
    
    @staticmethod
    def selectOneHost(id):
        '''获取单个主机资料'''
        try:
            return  VmServer.objects.get(id=id)
        except Exception,e:
            BaseLogging.Logger("[获取主机] 状态：[失败] 失败原因："+str(e), level='error')
            return False  
    
    @staticmethod
    def selectOneHostBy(host):
        '''获取单个主机资料'''
        try:
            return  VmServer.objects.get(server_ip=host)
        except Exception,e:
            BaseLogging.Logger("[获取主机] 状态：[失败] 失败原因："+str(e), level='error')
            return False

        
    @staticmethod
    def listVmServer(c=None,p=None):           
        if p and c is not None:
            return VmServer.objects.all().order_by("-id")[c:p] 
        else:
            return VmServer.objects.all().order_by("-id")
        
    @staticmethod
    def countServer(status=None):
        if isinstance(status,int):return VmServer.objects.filter(status=status)
        else:return VmServer.objects.all().order_by("-id")            
        