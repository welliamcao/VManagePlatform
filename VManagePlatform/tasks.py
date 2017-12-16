#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
import os
from celery import task
from VManagePlatform.models import VmServer
from VManagePlatform.utils.vDHCPConfigUtils import DHCPConfig
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.models import VmLogs,VmServerInstance,VmDHCP


'''
Django 版本大于等于1.7的时候，需要加上下面两句
import django
django.setup()
否则会抛出错误 django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet.
'''
 
import django
if django.VERSION >= (1, 7):#自动判断版本
    django.setup()


'''
    异步通知功能模块：by welliam.cao@ijinzhuan.com 2016/06/28
    task   处理能带参数的task
    task() 处理不需要带参数的task，不能混用不然提示task没有注册^-^!
'''
                    
@task()
def updateVMserver():
    serverList = VmServer.objects.all()   
    for server in  serverList: 
        VMS = LibvirtManage(server.server_ip,server.username, server.passwd, server.vm_type,pool=False)
        SERVER = VMS.genre(model='server')    
        if SERVER:
            if server.status == 0:
                data = SERVER.getVmServerInfo()
                try:
                    VmServer.objects.filter(id=server.id).update(instance=data.get('ins'),mem=data.get('mem'),
                                                          cpu_total=data.get('cpu_total'))
                    VMS.close()
                except Exception,e:
                    return e
            elif server.status == 1:
                try:
                    VmServer.objects.filter(id=server.id).update(status=0)
                except Exception,e:
                    return e                     
            
 


@task
def updateVMinstance(host=None):
    if host is None:
        serverList = VmServer.objects.all()    
        for server in  serverList:
            if server.status == 0: 
                VMS = LibvirtManage(server.server_ip,server.username, server.passwd, server.vm_type,pool=False)
                SERVER = VMS.genre(model='server')    
                if SERVER:
                    dataList = SERVER.getVmInstanceBaseInfo(server_ip=server.server_ip,server_id=server.id)
                    for ds in dataList:
                        ipaddress = ''
                        for ip in ds.get('ip'):
                            for k,v in ip.items():
                                ips = k + ':' + v.get('addr') + '/' + str(v.get('prefix')) 
                                ipaddress = ips + '\n' + ipaddress  
                        result = VmServerInstance.objects.filter(server=server,name=ds.get('name'))
                        if result:VmServerInstance.objects.filter(server=server,name=ds.get('name')).update(server=server,cpu=ds.get('cpu'),
                                                                                                            mem=ds.get('mem'),status=ds.get('status'),
                                                                                                            name=ds.get('name'),token=ds.get('token'),
                                                                                                            vnc=ds.get('vnc'),ips=ipaddress)
                                                                                                            
                        else:VmServerInstance.objects.create(server=server,cpu=ds.get('cpu'),
                                                             mem=ds.get('mem'),vnc=ds.get('vnc'),
                                                             status=ds.get('status'),name=ds.get('name'),
                                                             token=ds.get('token'),ips=ipaddress)
                    VMS.close()
                    
    else:
        server =  VmServer.objects.get(server_ip=host)
        if server and server.status == 0:
            VMS = LibvirtManage(server.server_ip,server.username, server.passwd, server.vm_type,pool=False)
            SERVER = VMS.genre(model='server')    
            if SERVER:
                dataList = SERVER.getVmInstanceBaseInfo(server_ip=server.server_ip,server_id=server.id)
                for ds in dataList:     
                    ipaddress = ''
                    for ip in ds.get('ip'):
                        for k,v in ip.items():
                            ips = k + ':' + v.get('addr') + '/' + str(v.get('prefix')) 
                            ipaddress = ips + '\n' + ipaddress                           
                    result = VmServerInstance.objects.filter(server=server,name=ds.get('name'))
                    if result:VmServerInstance.objects.filter(server=server,name=ds.get('name')).update(server=server,cpu=ds.get('cpu'),
                                                                                                        mem=ds.get('mem'),vnc=ds.get('vnc'),
                                                                                                        status=ds.get('status'),name=ds.get('name'),
                                                                                                        token=ds.get('token'),ips=ipaddress)
                    else:VmServerInstance.objects.create(server=server,cpu=ds.get('cpu'),
                                                         mem=ds.get('mem'),status=ds.get('status'),
                                                         name=ds.get('name'),token=ds.get('token'),
                                                         vnc=ds.get('vnc'),ips=ipaddress)
                VMS.close()   


@task()
def checkVMinstance():
    '''检查所有宿主机上面的实例，如果不存在的实例则从数据库里面清除掉'''
    serverList = VmServer.objects.all()    
    for server in  serverList:
        if server.status == 0:     
            VMS = LibvirtManage(server.server_ip,server.username, server.passwd, server.vm_type,pool=False)
            SERVER = VMS.genre(model='server')   
            vList = SERVER.getAllInstance()
            try:
                vmList = [ str(vm.token) for vm in VmServerInstance.objects.filter(server=server).all()]
            except Exception ,ex:
                print ex
            delVmList = list(set(vmList).difference(set(vList)))
            for v in delVmList:
                try:
                    vm = VmServerInstance.objects.filter(server=server,token=v)
                    vm.delete()
                except Exception ,ex:
                    print ex
            if SERVER:VMS.close() 

@task()
def startDhcpServer():
    DHCP = DHCPConfig()
    for dh in VmDHCP.objects.all():
        if dh.isAlive == 0 and dh.status == 0:
            alive = DHCP.netnsIsAlive(dh.mode)
            if alive[0] > 0:DHCP.enableNets(netnsName=dh.mode, brName=dh.brName, port=dh.dhcp_port, ip=dh.server_ip, drive=dh.drive)
            if dh.mode == 'dhcp-int': 
                status = DHCP.status(mode='int')               
                if status[0] > 0:
                    DHCP.start(netnsName=dh.mode, iprange=dh.ip_range,
                               port=dh.dhcp_port,drive=dh.drive,
                               mode='int',brName=dh.brName,
                               gateway=dh.gateway, dns=dh.dns)                          
            elif dh.mode == 'dhcp-ext':
                status = DHCP.status(mode='ext')
                if status[0] > 0:
                    DHCP.start(netnsName=dh.mode, iprange=dh.ip_range,
                               port=dh.dhcp_port, drive=dh.drive,
                               mode='ext',brName=dh.brName,
                               gateway=dh.gateway, dns=dh.dns)               
            


                
@task
def migrateInstace(data,user=None):
    try:
        vMserver = VmServer.objects.get(id=data.get('server_id'))
    except Exception,e:
        return e 
    try:
        VMS = LibvirtManage(vMserver.server_ip,vMserver.username, vMserver.passwd, vMserver.vm_type,pool=False)
        #获取要迁移的虚拟机硬盘情况
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        source_instance = INSTANCE.getVmInstanceInfo(server_ip=vMserver.server_ip, vm_name=data.get('vm_name'))            
    except Exception,e:
        return e           
    try:
        #连接远程宿主机，获取存储池，然后在存储池里面创建跟迁移的虚拟机相同的硬盘
        vMTargetserver = VmServer.objects.get(id=data.get('server_tid'))
    except Exception,e:
        return e     
    targetUri = str(vMTargetserver.uri).replace('qemu+','').replace('/system','')
    TargetVMS = LibvirtManage(vMserver.server_ip,vMserver.username, vMserver.passwd, vMserver.vm_type,pool=False)
    TargetStorage = TargetVMS.genre(model='storage')
    #获取被迁移的虚拟机磁盘配置，并且到远程服务器上创建，相同的磁盘配置
    for volume in source_instance.get('disks'):
        if volume.get('disk_sn').startswith('vd'):
            pool_name = volume.get('disk_pool')
            if pool_name:
                #判断远程服务器上是否存在相同的存储池
                pool = TargetStorage.getStoragePool(pool_name=pool_name)
                if pool:
                    volume_name = volume.get('disk_path')
                    pathf = os.path.dirname(volume.get('disk_path'))
                    volume_name = volume_name[len(pathf)+1:]
                    #创建磁盘
                    traget_volume = TargetStorage.createVolumes(pool, volume_name=volume_name, volume_capacity=volume.get('disk_size'),flags=0)            
    result = INSTANCE.migrate(instance,TargetVMS.conn,data.get('vm_tname'),targetUri)
    TargetVMS.close() 
    VMS.close()
    if result:result = 0
    else:result = 1
    desc = u'迁移虚拟机{vm_name}至{server_ip}宿主机'.format(vm_name=data.get('vm_name'),server_ip=targetUri)
    try:
        result = VmLogs.objects.create(server_id=data.get('server_id'),vm_name=data.get('vm_name'),
                                       content=desc,
                                       user=user,status=result,isRead=0) 
        if result:return True
        else:return False
    except Exception,e:
        return e
        
@task
def cloneInstace(data,user=None):
    server_id = data.get('server_id')
    insName = data.get('vm_name')
    try:
        vMserver =  VmServer.objects.get(id=server_id)
    except:
        return False 
    try:
        VMS = LibvirtManage(vMserver.server_ip,vMserver.username, vMserver.passwd, vMserver.vm_type,pool=False)
    except Exception,e:
        return  False
    try:
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(insName))
    except Exception,e:
        return False   
    clone_data = {}
    clone_data['name'] = data.get('vm_cname')
    clone_data['disk'] = data.get('vol_name')
    result = INSTANCE.clone(instance, clone_data=clone_data)
    if result == 0:result = 0
    else:result = 1
    VMS.close()
    try:
        result = VmLogs.objects.create(server_id=data.get('server_id'),vm_name=insName,
                                       content="克隆虚拟机：{name}".format(name=insName),
                                       user=user,status=result,isRead=0) 
        if result:return True
        else:return False
    except Exception,e:
        return e
        
         
          
@task
def snapInstace(data,user):
    try:
        vMserver = VmServer.objects.get(id=data.get('server_id')) 
        VMS = LibvirtManage(vMserver.server_ip,vMserver.username, vMserver.passwd, vMserver.vm_type,pool=False)
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        status = INSTANCE.snapShotCteate(instance, data.get('snap_name'))  
        VMS.close()
        if isinstance(status, str) is False:
            VmLogs.objects.create(server_id=data.get('server_id'),vm_name=data.get('vm_name'),
                                       content="虚拟机{name}创建快照{snap}".format(name=data.get('vm_name'),snap=data.get('snap_name')),
                                       user=user,status=0,isRead=0) 
        else:
            VmLogs.objects.create(server_id=data.get('server_id'),vm_name=data.get('vm_name'),
                                       content="虚拟机{name}创建快照{snap}".format(name=data.get('vm_name'),snap=data.get('snap_name')),
                                       user=user,status=1,isRead=0,result=status)             
        
    except Exception,e:
        return e 
        
@task
def revertSnapShot(data,user):
    try:
        vMserver = VmServer.objects.get(id=data.get('server_id')) 
        VMS = LibvirtManage(vMserver.server_ip,vMserver.username, vMserver.passwd, vMserver.vm_type,pool=False) 
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        status = INSTANCE.revertSnapShot(instance, data.get('snap_name'))
        VMS.close()
        if isinstance(status, int):
            VmLogs.objects.create(server_id=data.get('server_id'),vm_name=data.get('vm_name'),
                                       content="虚拟机{name}恢复快照{snap}".format(name=data.get('vm_name'),snap=data.get('snap_name')),
                                       user=user,status=0,isRead=0) 
        else:
            VmLogs.objects.create(server_id=data.get('server_id'),vm_name=data.get('vm_name'),
                                       content="虚拟机{name}恢复快照{snap}".format(name=data.get('vm_name'),snap=data.get('snap_name')),
                                       user=user,status=1,isRead=0,result=status)            
    except Exception,e:
        return e       
        
@task 
def recordLogs(server_id,vm_name,content,user,status,result=None):
    try:
        VmLogs.objects.create(server_id=server_id,vm_name=vm_name,
                                       content=content,user=user,status=status,
                                       isRead=0,result=result) 
    except Exception,e:
        return e