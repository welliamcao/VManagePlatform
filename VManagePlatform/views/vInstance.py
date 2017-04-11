#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.data.vMserver import VMServer
from VManagePlatform.data.vMinstance import TempInstance,VmInstance
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from VManagePlatform.const import Const 
from VManagePlatform.utils.vConnUtils import CommTools
from VManagePlatform.tasks import migrateInstace,cloneInstace,recordLogs
from VManagePlatform.utils.vBrConfigUtils import BRManage
from django.contrib.auth.models import User


@login_required
def addInstance(request):
    if request.method == "GET":
        try:
            vMserverId = request.GET.get('id')
            vmServer = VMServer.selectOneHost(id=vMserverId)
            userList = User.objects.all()
            tempList = TempInstance.listVmTemp()
            VMS = LibvirtManage(vmServer.uri)    
            SERVER = VMS.genre(model='server') 
            NETWORK = VMS.genre(model='network')       
            if SERVER:vStorage = SERVER.getVmStorageInfo()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except:
            vStorage = None
        vMImages =SERVER.getVmIsoList()
        netkList = NETWORK.listNetwork()
        VMS.close()
        return render_to_response('vmInstance/add_instance.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"添加虚拟机","url":"/addInstance"}],
                                    "vmServer":vmServer,"vStorage":vStorage,"vMImages":vMImages,"netkList":netkList,
                                    "tempList":tempList,"userList":userList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        op = request.POST.get('op')
        if op in ['custom','xml','template'] and request.user.has_perm('VManagePlatform.add_vmserverinstance'):
            try:
                vMserver = VMServer.selectOneHost(id=request.POST.get('server_id'))
                VMS = LibvirtManage(uri=vMserver.uri)
                INSTANCE = VMS.genre(model='instance')
                SERVER = VMS.genre(model='server')
                STORAGE = VMS.genre(model='storage')
                NETWORK = VMS.genre(model='network')
            except Exception,e:
                return  JsonResponse({"code":500,"msg":"虚拟服务器连接失败，请注意连通性。","data":e})  
            if  SERVER:     
                if op == 'custom':
                    netks = [ str(i) for i in request.POST.get('netk').split(',')]
                    if INSTANCE:
                        instance =  INSTANCE.queryInstance(name=str(request.POST.get('vm_name'))) 
                        if instance:
                            return  JsonResponse({"code":500,"msg":"虚拟机已经存在","data":None})
                        else:
                            networkXml = ''
                            radStr = CommTools.radString(4)
                            for nt in netks:
                                netkType = NETWORK.getNetworkType(nt)
                                netXml = Const.CreateNetcard(nkt_br=nt,ntk_name=nt+'-'+radStr,mode=netkType)                             
                                networkXml = netXml +  networkXml
                            pool = STORAGE.getStoragePool(pool_name=request.POST.get('storage')) 
                            volume_name = request.POST.get('vm_name')+'.img'
                            if pool:
                                volume = STORAGE.createVolumes(pool, volume_name=volume_name, volume_capacity=request.POST.get('disk'))
                                if volume:
                                    disk_path = volume.path()
                                    volume_name = volume.name()
                                    disk_xml = Const.CreateDisk(volume_path=disk_path)  
                                else:return JsonResponse({"code":500,"msg":"添加虚拟机失败，存储池里面以存在以主机名命名的磁盘","data":None})
                            else:
                                return  JsonResponse({"code":500,"msg":"添加虚拟机失败，存储池已经被删除掉","data":None}) 
                            dom_xml = Const.CreateIntanceConfig(dom_name=request.POST.get('vm_name'),maxMem=int(SERVER.getServerInfo().get('mem')),
                                                          mem=int(request.POST.get('mem')),cpu=request.POST.get('cpu'),disk=disk_xml,
                                                          iso_path=request.POST.get('system'),network=networkXml)
                            dom = SERVER.createInstance(dom_xml)
                            recordLogs.delay(user=str(request.user),action=op,status=dom,vm_name=request.POST.get('vm_name'))
                            if dom==0:    
                                VMS.close()
                                VmInstance.insertInstance(dict(server=vMserver,name=request.POST.get('vm_name'),
                                                               cpu=request.POST.get('cpu'),mem=request.POST.get('mem'),
                                                               owner=request.POST.get('owner'),status=1,
                                                               ))       
                                return JsonResponse({"code":200,"data":None,"msg":"虚拟主机添加成功。"}) 
                            else:
                                STORAGE.deleteVolume(pool, volume_name)
                                VMS.close() 
                                return JsonResponse({"code":500,"data":None,"msg":"虚拟主机添加失败。"}) 
                elif op == 'xml':
                    domXml = request.POST.get('xml')
                    dom = SERVER.defineXML(xml=domXml)
                    VMS.close() 
                    recordLogs.delay(user=str(request.user),action=op,status=dom,vm_name=request.POST.get('vm_name'))
                    if dom:return  JsonResponse({"code":200,"data":None,"msg":"虚拟主机添加成功。"})
                    else:return JsonResponse({"code":500,"data":None,"msg":"虚拟主机添加失败。"})
                elif op=='template':
                    try:
                        temp = TempInstance.selectVmTemp(id=request.POST.get('temp'))
                        if INSTANCE:instance =  INSTANCE.queryInstance(name=str(request.POST.get('vm_name'))) 
                        if instance:return  JsonResponse({"code":500,"msg":"虚拟机已经存在","data":None})
                        else:
                            pool = STORAGE.getStoragePool(pool_name=request.POST.get('storage')) 
                            volume_name = request.POST.get('vm_name')+'.img'
                            if pool:
                                volume = STORAGE.createVolumes(pool, volume_name=volume_name, volume_capacity=temp.disk)
                                if volume:
                                    disk_path = volume.path()
                                    volume_name = volume.name()
                                    disk_xml = Const.CreateDisk(volume_path=disk_path)  
                                else:return JsonResponse({"code":500,"msg":"添加虚拟机失败，存储池里面以存在以主机名命名的磁盘","data":None})
                            else:
                                return  JsonResponse({"code":500,"msg":"添加虚拟机失败，存储池已经被删除掉","data":None}) 
                            dom_xml = Const.CreateIntanceConfig(dom_name=request.POST.get('vm_name'),maxMem=int(SERVER.getServerInfo().get('mem')),
                                                          mem=temp.mem,cpu=temp.cpu,disk=disk_xml,
                                                          iso_path=request.POST.get('system'),network=None)
                            dom = SERVER.createInstance(dom_xml)
                            recordLogs.delay(user=str(request.user),action=op,status=dom,vm_name=request.POST.get('vm_name'))
                            if dom==0:    
                                VMS.close()        
                                return JsonResponse({"code":200,"data":None,"msg":"虚拟主机添加成功。"}) 
                            else:
                                STORAGE.deleteVolume(pool, volume_name)
                                VMS.close() 
                                return JsonResponse({"code":500,"data":None,"msg":"虚拟主机添加失败。"}) 
                    except:
                        return JsonResponse({"code":500,"data":None,"msg":"虚拟主机添加失败。"})
                    
            else:return JsonResponse({"code":500,"data":None,"msg":"虚拟服务器连接失败，请注意连通性。"}) 
        else:return JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限添加虚拟机"})

@login_required
def modfInstance(request):                
    if request.method == "POST":
        if CommTools.argsCkeck(args=['op','server_id','vm_name'], data=request.POST) and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            vMserver = VMServer.selectOneHost(id=request.POST.get('server_id'))
            LIBMG = LibvirtManage(uri=vMserver.uri)
            SERVER = LIBMG.genre(model='server')
            STROAGE = LIBMG.genre(model='storage')
            INSTANCE = LIBMG.genre(model='instance')
            if SERVER:
                instance = INSTANCE.queryInstance(name=str(request.POST.get('vm_name')))  
                if instance is False:
                    LIBMG.close()
                    return  JsonResponse({"code":404,"data":None,"msg":"虚拟机不存在，或者已经被删除。"})     
            else:return  JsonResponse({"code":500,"data":None,"msg":"虚拟主机链接失败。"}) 
            #调整磁盘            
            if request.POST.get('device') == 'disk':   
                if request.POST.get('op') == 'attach':                     
                    if instance.state()[0] == 5:return  JsonResponse({"code":500,"data":None,"msg":"请先启动虚拟机。"})
                    storage = STROAGE.getStoragePool(pool_name=request.POST.get('pool_name'))                     
                    if storage:
                        volume = STROAGE.createVolumes(pool=storage, volume_name=request.POST.get('vol_name'),
                                                       drive=request.POST.get('vol_drive'), volume_capacity=request.POST.get('vol_size'))
                        if volume:
                            volPath = volume.path()
                            volume_name = volume.name()
                        else:
                            LIBMG.close()
                            return  JsonResponse({"code":500,"data":None,"msg":"卷已经存在。"})
                        status = INSTANCE.addInstanceDisk(instance, volPath)
                        LIBMG.close()
                        if status:
                            recordLogs.delay(user=str(request.user),action='attach_disk',status=0,vm_name=request.POST.get('vm_name'))
                            return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"})
                        else:
                            STROAGE.deleteVolume(storage, volume_name)
                            recordLogs.delay(user=str(request.user),action='attach_disk',status=1,vm_name=request.POST.get('vm_name'))
                            return  JsonResponse({"code":500,"data":None,"msg":"操作失败。"})
                    else: 
                        LIBMG.close()                       
                        return  JsonResponse({"code":404,"data":None,"msg":"存储池不存在，或者已经被删除。"})                             
                elif  request.POST.get('op') == 'detach':
                    status = INSTANCE.delInstanceDisk(instance, volPath=request.POST.get('disk'))    
                    LIBMG.close()
                    recordLogs.delay(user=str(request.user),action='detach_disk',status=status,vm_name=request.POST.get('vm_name'))
                    if status==0:return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"})
                    else:
                        LIBMG.close()
                        return  JsonResponse({"code":500,"data":status,"msg":"操作失败。"})                     
            #调整网卡
            elif  request.POST.get('device') == 'netk':
                if request.POST.get('op') == 'attach': 
                    result = INSTANCE.addInstanceInterface(instance, brName=request.POST.get('netk_name'))
                    recordLogs.delay(user=str(request.user),action='attach_netk',status=result,vm_name=request.POST.get('vm_name'))
                    if isinstance(result,int):return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"})
                    else:return  JsonResponse({"code":500,"data":status,"msg":"添加失败。"})
                elif  request.POST.get('op') == 'detach':
                    result = INSTANCE.delInstanceInterface(instance, interName=request.POST.get('netk'))
                    recordLogs.delay(user=str(request.user),action='detach_netk',status=result,vm_name=request.POST.get('vm_name'))
                    if isinstance(result,int):return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"})
                    else:return  JsonResponse({"code":500,"data":status,"msg":"添加失败。"})
            #调整内存大小
            elif  request.POST.get('device') == 'mem':
                if request.POST.get('op') == 'attach': 
                    result = INSTANCE.setMem(instance, mem=int(request.POST.get('mem')))  
                    recordLogs.delay(user=str(request.user),action='attach_mem',status=result,vm_name=request.POST.get('vm_name')) 
                    if isinstance(result,int):return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"}) 
                    else:return  JsonResponse({"code":500,"data":None,"msg":"不能设置虚拟机内存超过宿主机机器的物理内存"})
            #调整cpu个数   
            elif  request.POST.get('device') == 'cpu':
                if request.POST.get('op') == 'attach': 
                    result = INSTANCE.setVcpu(instance, cpu=int(request.POST.get('cpu')))
                    LIBMG.close()
                    recordLogs.delay(user=str(request.user),action='attach_cpu',status=result,vm_name=request.POST.get('vm_name'))
                    if isinstance(result,int):return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"}) 
                    else:return  JsonResponse({"code":500,"data":None,"msg":"不能设置虚拟机CPU超过宿主机机器的物理CPU个数"})     
            #调整带宽
            elif  request.POST.get('device') == 'bandwidth':
                SSH = BRManage(hostname=vMserver.server_ip,port=22)
                OVS = SSH.genre(model='ovs')
                mode = INSTANCE.getInterFace(instance,request.POST.get('netk_name'))
                if request.POST.get('op') == 'attach': 
                    if mode.get('type') == 'openvswitch':
                        if int(request.POST.get('bandwidth')) == 0:result = OVS.ovsCleanBandwidth(port=request.POST.get('netk_name'))
                        else:result = OVS.ovsConfBandwidth(port=request.POST.get('netk_name'), bandwidth=request.POST.get('bandwidth'))
                    else:
                        if int(request.POST.get('bandwidth')) == 0:result = INSTANCE.cleanInterfaceBandwidth(instance, request.POST.get('netk_name'))
                        result = INSTANCE.setInterfaceBandwidth(instance, port=request.POST.get('netk_name'), bandwidth=request.POST.get('bandwidth'))
                    SSH.close()
                    LIBMG.close()
                    if result.get('status') == 'success':return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"}) 
                    else:return  JsonResponse({"code":500,"data":None,"msg":"未设置带宽，不需要清除"})    
                            
                       
            LIBMG.close()                                 
        else:
            return  JsonResponse({"code":500,"data":None,"msg":"暂时不支持的操作或者您没有权限操作操作此项。"})
@login_required
def handleInstance(request):
    if request.method == "POST":
        op = request.POST.get('op')
        server_id = request.POST.get('server_id')
        insName = request.POST.get('vm_name')
        if op in ['start','reboot','shutdown','halt','suspend',
                  'resume','xml','migrate','delete','mount',
                  'umount','clone'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            try:
                vMserver = VMServer.selectOneHost(id=server_id)
            except:
                return JsonResponse({"code":500,"data":None,"msg":"主机不存在。"})  
            try:
                VMS = LibvirtManage(uri=vMserver.uri)
            except Exception,e:
                return  JsonResponse({"code":500,"msg":"服务器连接失败。。","data":e})
            try:
                INSTANCE = VMS.genre(model='instance')
                instance = INSTANCE.queryInstance(name=str(insName))
            except Exception,e:
                return JsonResponse({"code":500,"msg":"虚拟机强制关闭失败。。","data":e})  
            if op == 'halt':
                result = INSTANCE.destroy(instance)
            elif op == 'start':
                result = INSTANCE.start(instance)
            elif op == 'reboot':
                result = INSTANCE.reboot(instance)
            elif op == 'shutdown':
                result = INSTANCE.shutdown(instance)
            elif op == 'suspend':
                result = INSTANCE.suspend(instance)   
            elif op == 'resume':
                result = INSTANCE.resume(instance)  
            elif op == 'delete':
                INSTANCE.delDisk(instance)  
                VmInstance.deleteInstance(server=vMserver, name=insName)         
                result = INSTANCE.delete(instance) 
            elif op == 'migrate':
                migrateInstace.delay(request.POST)
                VMS.close() 
                return  JsonResponse({"code":200,"data":None,"msg":"迁移任务提交成功."})
            elif op == 'umount':
                result = INSTANCE.umountIso(instance, dev=request.POST.get('dev'), image=request.POST.get('iso'))  
            elif op == 'mount':
                result = INSTANCE.mountIso(instance, dev=request.POST.get('dev'), image=request.POST.get('iso'))  
            elif op == 'clone':
                cloneInstace.delay(data=request.POST,user=str(request.user))
                VMS.close()
                return  JsonResponse({"code":200,"data":None,"msg":"克隆任务提交成功."}) 
            elif op == 'xml':
                try:
                    result = INSTANCE.defineXML(xml=request.POST.get('xml')) 
                except Exception,e:
                    result = e           
            VMS.close()  
            recordLogs.delay(user=str(request.user),action=op,status=result,vm_name=insName)   
            if isinstance(result,int):return  JsonResponse({"code":200,"data":None,"msg":"操作成功。"}) 
            else:return  JsonResponse({"code":500,"data":result,"msg":"操作失败。"})           
        else:
            return  JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})            

    else:
        return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"}) 
    
    
@login_required
def listInstance(request): 
    if request.method == "GET":       
        vMserverId = request.GET.get('id')
        vmServer = VMServer.selectOneHost(id=vMserverId)
        try:
            VMS = LibvirtManage(vmServer.uri)    
            SERVER = VMS.genre(model='server')
            userList = User.objects.all()    
            if SERVER:
                inStanceList = SERVER.getVmInstanceBaseInfo(server_ip=vmServer.server_ip,server_id=vmServer.id)
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except:
            inStanceList = None
        return render_to_response('vmInstance/list_instance.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"虚拟机实例列表","url":"/listInstance?id=%s" % vMserverId}],
                                   "inStanceList":inStanceList,"vmServer":vmServer,"userList":userList},
                                  context_instance=RequestContext(request))    
        
        
@login_required
def viewInstance(request): 
    if request.method == "GET":       
        vMserverId = request.GET.get('id')
        vmServer = VMServer.selectOneHost(id=vMserverId)
        serverList = VMServer.listVmServer()
        try:
            VMS = LibvirtManage(vmServer.uri)    
            INSTANCE = VMS.genre(model='instance')  
            SERVER = VMS.genre(model='server')
            NETWORK = VMS.genre(model='network')    
            if INSTANCE:
                instance = INSTANCE.queryInstance(name=str(request.GET.get('vm_name')))
                '''获取存储池'''
                poolInfo = SERVER.getVmStorageInfo()
                '''获取网络设备'''
                netkInfo = NETWORK.listNetwork()
                '''获取cdrom设备'''
                imgList =  INSTANCE.getMediaDevice(instance)
                '''获取iso存储池的iso列表'''
                isoList = SERVER.getVmIsoList()
                '''获取实例的xml文件'''
                insXml = INSTANCE.getInsXMLDesc(instance, flag=0)
                '''获取实例信息'''
                insInfo = INSTANCE.getVmInstanceInfo(instance,server_ip=vmServer.server_ip,vMname=request.GET.get('vm_name'))
                insInfo['cpu_per'] = INSTANCE.getCpuUsage(instance)
                snapList = INSTANCE.snapShotList(instance)
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            snapList = None
            insInfo = None
        return render_to_response('vmInstance/view_instance.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"虚拟机实例列表","url":"/listInstance"}],
                                   "inStance":insInfo,"vmServer":vmServer,"snapList":snapList,"poolInfo":poolInfo,
                                   "netkInfo":netkInfo,"imgList":imgList,"isoList":isoList,"serverList":serverList,
                                   "insXml":insXml},
                                  context_instance=RequestContext(request))                 

@login_required
def tempInstance(request): 
    if request.method == "GET":  
        tempList = TempInstance.listVmTemp()
        return render_to_response('vmInstance/temp_instance.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"实例模板","url":'/tempInstance'}],
                                   "tempList":tempList},
                                  context_instance=RequestContext(request)) 
    elif request.method == "POST":
        op = request.POST.get('op')
        if op in ['add','modf','del'] and request.user.has_perm('VManagePlatform.add_vminstance_template'):
            if op == 'add':
                result = TempInstance.insertVmTemp(name=request.POST.get('name'),cpu=request.POST.get('cpu'),
                                                       mem=request.POST.get('mem'),disk=request.POST.get('disk')) 
                if isinstance(result, str):return JsonResponse({"code":500,"data":result,"msg":"添加失败。"})                   
                else:return JsonResponse({"code":200,"data":None,"msg":"添加成功。"})
        else:return JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})