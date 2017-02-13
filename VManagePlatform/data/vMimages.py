#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from VManagePlatform.models import VmServerImages
from VManagePlatform.apps.Base import BaseLogging

class VMImages(object):
    @staticmethod
    def insertVmImages(name,image_file,nfs_path,os_type):
        try:
            images = VmServerImages(name=name,image_file=image_file,
                                    nfs_path=nfs_path,os_type=os_type)
            images.save()
            return images
        except Exception,e:
            BaseLogging.Logger("[添加镜像] 状态：[失败] 失败原因："+str(e), level='error')
            return False
        
    @staticmethod
    def listVmServer(c=None,p=None):           
        if p and c is not None:
            return VmServerImages.objects.all().order_by("-id")[c:p] 
        else:
            return VmServerImages.objects.all().order_by("-id")   
        
    @staticmethod
    def selectOneHost(id):
        '''获取单个镜像'''
        try:
            return  VmServerImages.objects.select_related().get(id=id)
        except Exception,e:
            BaseLogging.Logger("[获取镜像] 状态：[失败] 失败原因："+str(e), level='error')
            return e                  