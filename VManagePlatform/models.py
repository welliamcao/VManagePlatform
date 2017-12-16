#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from django.db import models


class VmServer(models.Model):
    server_ip = models.GenericIPAddressField(unique=True,verbose_name='管理IP')
    username = models.CharField(max_length=100,verbose_name='用户名称')
    passwd = models.CharField(max_length=100,blank=True,null=True,verbose_name='密码')
    hostname = models.CharField(max_length=100,blank=True,null=True,verbose_name='主机名称')
    instance = models.SmallIntegerField(blank=True,null=True,verbose_name='实例个数') 
    vm_type =  models.IntegerField(verbose_name='虚拟化类型')
    mem = models.CharField(max_length=100,blank=True,null=True,verbose_name='内存容量')
    cpu_total = models.SmallIntegerField(blank=True,null=True,verbose_name='CPU个数') 
    status =  models.SmallIntegerField(blank=True,null=True,verbose_name='状态')
    createTime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modifyTime = models.DateTimeField(auto_now=True,blank=True,null=True)
    class Meta:
        permissions = (
            ("read_vmserver", "Can read 虚拟主机信息"),
        )
        verbose_name = '虚拟主机信息'  
        verbose_name_plural = '虚拟主机信息'


class VmDHCP(models.Model):
    mode = models.CharField(unique=True,max_length=100,verbose_name='dhcp类型')
    drive = models.CharField(max_length=10,verbose_name='驱动类型')
    brName = models.CharField(max_length=100,verbose_name='网桥名称')
    server_ip = models.GenericIPAddressField(verbose_name='DHCP服务地址')
    ip_range = models.CharField(max_length=100,verbose_name='地址池')
    gateway = models.GenericIPAddressField(blank=True,null=True,verbose_name='网关地址')
    dns = models.GenericIPAddressField(blank=True,null=True,verbose_name='DNS地址') 
    dhcp_port = models.CharField(max_length=100,verbose_name='dhcp端口名')
    isAlive = models.SmallIntegerField(default=1,null=True, blank=True,verbose_name='是否激活') 
    status = models.SmallIntegerField(default=1,null=True, blank=True,verbose_name='是否启动') 
    createTime = models.DateTimeField(auto_now_add=True,blank=True,null=True)
    modifyTime = models.DateTimeField(auto_now=True,blank=True,null=True)
    class Meta:
        permissions = (
            ("read_vmdhcp", "Can read 虚拟主机DHCP配置"),
        )
        verbose_name = '虚拟主机DHCP配置'  
        verbose_name_plural = '虚拟主机DHCP配置'
        unique_together = (("mode", "brName"))

class VmInstance_Template(models.Model):
    name =  models.CharField(unique=True,max_length=100,verbose_name='模板名称')
    cpu =  models.SmallIntegerField(verbose_name='cpu个数')
    mem =  models.SmallIntegerField(verbose_name='mem大小')
    disk =  models.SmallIntegerField(verbose_name='磁盘大小') 
    class Meta:
        permissions = (
            ("read_vminstance_template", "Can read 虚拟主机模板"),
        )
        verbose_name = '虚拟主机模板'  
        verbose_name_plural = '虚拟主机模板'
        
        
class VmServerInstance(models.Model):  
    server = models.ForeignKey('VmServer') 
    name =  models.CharField(max_length=100,verbose_name='实例名称')
    cpu = models.SmallIntegerField(verbose_name='Cpu个数') 
    mem = models.IntegerField(verbose_name='内存容量')
    status = models.SmallIntegerField(verbose_name='实例状态')
    owner =  models.CharField(max_length=50,blank=True,null=True,verbose_name='拥有者')
    rate_limit = models.SmallIntegerField(blank=True,null=True,verbose_name='网卡限速')
    token = models.CharField(max_length=100,blank=True,null=True,verbose_name='令牌')
    ips = models.TextField(max_length=200,blank=True,null=True,verbose_name='ip地址')
    vnc = models.SmallIntegerField(blank=True,null=True,verbose_name='VNC端口')
    class Meta:
        permissions = (
            ("read_vmserver_instance", "Can read 虚拟主机实例"),
        )
        verbose_name = '虚拟主机实例'  
        verbose_name_plural = '虚拟主机实例'  
    unique_together = (("server", "name"))    
        

        
class VmLogs(models.Model): 
    server_id = models.IntegerField(verbose_name='宿主机id',blank=True,null=True,default=None)
    vm_name = models.CharField(max_length=50,verbose_name='虚拟机名称',default=None)
    content = models.CharField(max_length=100,verbose_name='操作内容',default=None)
    user =  models.CharField(blank=True,null=True,max_length=20,verbose_name='用户')
    status = models.SmallIntegerField(verbose_name='执行结果',blank=True,null=True) 
    isRead = models.SmallIntegerField(verbose_name='是否已读取',blank=True,null=True) 
    result = models.TextField(verbose_name='失败原因',blank=True,null=True) 
    create_time = models.DateTimeField(auto_now_add=True,blank=True,null=True,verbose_name='执行时间')
    class Meta:
        permissions = (
            ("read_vmlogs", "Can read 虚拟主机操作日志"),
        )
        verbose_name = '虚拟主机操作日志'  
        verbose_name_plural = '虚拟主机操作日志' 