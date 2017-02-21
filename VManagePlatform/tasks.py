#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
import os,json
from celery import task
from VManagePlatform.data.vMserver import VMServer 
from VManagePlatform.data.vMdhcp import VMDhcp
from VManagePlatform.utils.vDHCPConfigUtils import DHCPConfig
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.models import VmLogs,VmServerInstance


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
    serverList = VMServer.listVmServer()    
    for server in  serverList: 
        VMS = LibvirtManage(server.uri)
        SERVER = VMS.genre(model='server')    
        server_id = server.id
        if SERVER:
            if server.status == 0:
                data = SERVER.getVmServerInfo()
                VMServer.updateVmServer(server_id=server_id,instance=data.get('ins'),
                                              mem=data.get('mem'),cpu_total=data.get('cpu_total'),
                                              mem_per=data.get('mem_per'))
            elif server.status == 1:
                result = VMServer.updateVmServerStatus(server_id=server_id, status=0)
                if isinstance(result, str):return result                       
            VMS.close()
        else:
            result = VMServer.updateVmServerStatus(server_id=server_id, status=1)
            if isinstance(result, str):return result 
 


@task
def updateVMinstance(host=None):
    if host is None:
        serverList = VMServer.listVmServer()    
        for server in  serverList:
            if server.status == 0: 
                VMS = LibvirtManage(server.uri)
                SERVER = VMS.genre(model='server')    
                if SERVER:
                    dataList = SERVER.getVmInstanceBaseInfo(server_ip=server.server_ip,server_id=server.id)
                    for ds in dataList:
                        result = VmServerInstance.objects.filter(server=server,name=ds.get('name'))
                        if result:VmServerInstance.objects.filter(server=server,name=ds.get('name')).update(server=server,cpu=ds.get('cpu'),
                                                                                                            mem=ds.get('mem'),status=ds.get('status'),
                                                                                                            name=ds.get('name'),token=ds.get('token'),
                                                                                                            vnc=ds.get('vnc'),
                                                                                                            )
                        else:VmServerInstance.objects.create(server=server,cpu=ds.get('cpu'),
                                                             mem=ds.get('mem'),vnc=ds.get('vnc'),
                                                             status=ds.get('status'),name=ds.get('name'),
                                                             token=ds.get('token'))
                    VMS.close()
                    
    else:
        server =  VMServer.selectOneHostBy(host)
        if server and server.status == 0:
            VMS = LibvirtManage(server.uri)
            SERVER = VMS.genre(model='server')    
            if SERVER:
                dataList = SERVER.getVmInstanceBaseInfo(server_ip=server.server_ip,server_id=server.id)
                for ds in dataList:                            
                    result = VmServerInstance.objects.filter(server=server,name=ds.get('name'))
                    if result:VmServerInstance.objects.filter(server=server,name=ds.get('name')).update(server=server,cpu=ds.get('cpu'),
                                                                                                        mem=ds.get('mem'),vnc=ds.get('vnc'),
                                                                                                        status=ds.get('status'),name=ds.get('name'),
                                                                                                        token=ds.get('token'))
                    else:VmServerInstance.objects.create(server=server,cpu=ds.get('cpu'),
                                                         mem=ds.get('mem'),status=ds.get('status'),
                                                         name=ds.get('name'),token=ds.get('token'),
                                                         vnc=ds.get('vnc'))
                VMS.close()   



@task()
def startDhcpServer():
    DHCP = DHCPConfig()
    for dh in VMDhcp.listVmDhcp():
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
def migrateInstace(data):
    try:
        vMserver = VMServer.selectOneHost(id=data.get('server_id'))
    except Exception,e:
        return e 
    try:
        VMS = LibvirtManage(uri=vMserver.uri)
        #获取要迁移的虚拟机硬盘情况
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        source_instance = INSTANCE.getVmInstanceInfo(server_ip=vMserver.server_ip, vm_name=data.get('vm_name'))            
    except Exception,e:
        return e           
    try:
        #连接远程宿主机，获取存储池，然后在存储池里面创建跟迁移的虚拟机相同的硬盘
        vMTargetserver = VMServer.selectOneHost(id=data.get('server_tid'))
    except Exception,e:
        return e     
    targetUri = str(vMTargetserver.uri).replace('qemu+','').replace('/system','')
    TargetVMS = LibvirtManage(uri=vMTargetserver.uri)
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
                    print  volume_name,traget_volume             
    result = INSTANCE.migrate(instance,TargetVMS.conn,data.get('vm_tname'),targetUri)
    TargetVMS.close() 
    VMS.close()
    if result:result = 0
    else:result = 1
    desc = u'迁移虚拟机{vm_name}至{server_ip}宿主机'.format(vm_name=data.get('vm_name'),server_ip=targetUri)
    try:
        result = VmLogs.objects.create(desc=desc,user=data.user,status=result,action='migrate',object=data.get('vm_name'))
        if result:return True
        else:return False
    except Exception,e:
        return e
        
@task
def cloneInstace(data,user=None):
    server_id = data.get('server_id')
    insName = data.get('vm_name')
    try:
        vMserver = VMServer.selectOneHost(id=server_id)
    except:
        return False 
    try:
        VMS = LibvirtManage(uri=vMserver.uri)
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
    desc = u'克隆虚拟机{vm_name}'.format(vm_name=data.get('vm_name')) 
    if result == 0:result = 0
    else:result = 1
    VMS.close()
    try:
        result = VmLogs.objects.create(desc=desc,user=user,status=result,action='clone',object=data.get('vm_name'))
        if result:return True
        else:return False
    except Exception,e:
        return e
        
         
          
@task
def snapInstace(data,user):
    try:
        vMserver = VMServer.selectOneHost(id=data.get('server_id')) 
        VMS = LibvirtManage(uri=vMserver.uri) 
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        status = INSTANCE.snapShotCteate(instance, data.get('snap_name'))  
        if status:status = 0
        else:status = 1
        desc = u'创建快照{snap_name}'.format(snap_name=data.get('snap_name'))
        result = VmLogs.objects.create(desc=desc,user=user,status=status,action='add_snap',object=data.get('vm_name')) 
        if result:return True
        else:return False 
        VMS.close()
    except Exception,e:
        return e 
        
@task
def revertSnapShot(data,user):
    try:
        vMserver = VMServer.selectOneHost(id=data.get('server_id')) 
        VMS = LibvirtManage(uri=vMserver.uri) 
        INSTANCE = VMS.genre(model='instance')
        instance = INSTANCE.queryInstance(name=str(data.get('vm_name')))
        status = INSTANCE.revertSnapShot(instance, data.get('snap_name'))
        VMS.close()
        desc = u'快照恢复{snap_name}'.format(snap_name=data.get('snap_name'))
        if status==0:status = status
        else:status = 1
        result = VmLogs.objects.create(desc=desc,user=user,status=status,action='revert_snap',object=data.get('vm_name')) 
        if result:return True
        else:return False  
    except Exception,e:
        return e       
        
@task 
def recordLogs(user,action,status,vm_name=None,result=None,server_id=None):
    if status != 0:status = 1
    desc = {
               'suspend':"暂停虚拟机",
               'resume':"恢复虚拟机",
               'delete':"删除虚拟机",
               'halt':"强制关闭虚拟机",
               "start":"启动虚拟机",
               "reboot":"重启虚拟机",
               "shutdown":"关闭虚拟机",
               "umount":"卸载光驱",
               "mount":"挂载光驱",
               "clone":"克隆虚拟机",
               "migrate":"迁移虚拟机",
               "custom":"创建自定义虚拟机",
               "xml":"通过XML创建虚拟机",
               "template":"通过模板创建虚拟机",
               "attach_disk":"添加硬盘",
               "detach_disk":"删除硬盘",
               "detach_netk":"删除网卡",
               "attach_netk":"添加网卡",
               "attach_mem":"调整内存",
               "attach_cpu":"调整CPU",
               "delete_snap":"删除快照",
               }
    try:
        result = VmLogs.objects.create(desc=desc.get(action),user=user,status=status,action=action,object=vm_name,result=result) 
        if result:return True
        else:return False
    except Exception,e:
        return e