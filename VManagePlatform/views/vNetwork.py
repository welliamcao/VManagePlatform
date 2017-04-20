#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from VManagePlatform.utils.vMConUtils import LibvirtManage
from django.template import RequestContext
from VManagePlatform.data.vMserver import VMServer
from VManagePlatform.const.Const import CreateNetwork
from VManagePlatform.utils.vBrConfigUtils import BRManage

@login_required
def configNetwork(request):
    if request.method == "GET":
        vmServerId = request.GET.get('id')
        vmServer = VMServer.selectOneHost(id=vmServerId)
        try:
            VMS = LibvirtManage(uri=vmServer.uri)
            NETWORK = VMS.genre(model='network')
            if NETWORK:
                netList = NETWORK.listNetwork()
                insList = NETWORK.listInterface()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            netList = None
        return render_to_response('vmNetwork/add_network.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"网络管理","url":'/addNetwork'}],
                                   "vmServer":vmServer,"netList":netList,"insList":insList},context_instance=RequestContext(request))    
    elif request.method == "POST" and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
        try:
            vmServer = VMServer.selectOneHost(id=request.POST.get('server_id'))
        except:
            return JsonResponse({"code":500,"data":None,"msg":"主机不存在。"})  
        try:
            VMS = LibvirtManage(uri=vmServer.uri)
            NETWORK = VMS.genre(model='network')
            SSH = BRManage(hostname=vmServer.server_ip,port=22)
            OVS = SSH.genre(model='ovs')
            BRCTL = SSH.genre(model='brctl')
            if NETWORK and OVS:
                status = NETWORK.getNetwork(netk_name=request.POST.get('name'))
                if status:
                    VMS.close() 
                    return  JsonResponse({"code":500,"msg":"网络已经存在。","data":None}) 
                else:
                    if request.POST.get('mode') == 'openvswitch':
                        status =  OVS.ovsAddBr(brName=request.POST.get('name'))#利用ovs创建网桥
                        if status.get('status') == 'success':
                            status = OVS.ovsAddInterface(brName=request.POST.get('name'), interface=request.POST.get('interface'))#利用ovs创建网桥，并且绑定端口
                        if status.get('status') == 'success':
                            if request.POST.get('stp') == 'on':status = OVS.ovsConfStp(brName=request.POST.get('name'))#是否开启stp
                    elif request.POST.get('mode') == 'bridge':
                        if request.POST.get('stp') == 'on':status = BRCTL.brctlAddBr(iface=request.POST.get('interface'),brName=request.POST.get('name'),stp='on')
                        else:status = BRCTL.brctlAddBr(iface=request.POST.get('interface'),brName=request.POST.get('name'),stp=None)
                    SSH.close()
                    if  status.get('status') == 'success':                          
                        XML = CreateNetwork(name=request.POST.get('name'),
                                            bridgeName=request.POST.get('name'),
                                            mode=request.POST.get('mode'))
                        result = NETWORK.createNetwork(XML)
                        VMS.close()
                    else:
                        VMS.close()
                        return  JsonResponse({"code":500,"msg":"网络创建失败。","data":status.get('stderr')}) 
                    if isinstance(result,int): return  JsonResponse({"code":200,"msg":"网络创建成功。","data":None})   
                    else:return  JsonResponse({"code":500,"msg":"网络创建失败。","data":None})   
            else:return  JsonResponse({"code":500,"msg":"网络创建失败。","data":None})                                                 
        except Exception,e:
            return  JsonResponse({"code":500,"msg":"服务器连接失败。。","data":e})  
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作或者您没有权限操作此项"}) 
    
            
@login_required
def handleNetwork(request):
    if request.method == "POST":
        op = request.POST.get('op')
        server_id = request.POST.get('server_id')
        netkName = request.POST.get('netkName')
        if op in ['delete'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            try:
                vmServer = VMServer.selectOneHost(id=server_id)
            except:
                return JsonResponse({"code":500,"data":None,"msg":"主机不存在。"})  
            try:
                VMS = LibvirtManage(uri=vmServer.uri)
                SSH = BRManage(hostname=vmServer.server_ip,port=22)
                OVS = SSH.genre(model='ovs')
                BRCTL = SSH.genre(model='brctl')                
            except Exception,e:
                return  JsonResponse({"code":500,"msg":"服务器连接失败。。","data":e})             
            try:
                NETWORK = VMS.genre(model='network')
                netk = NETWORK.getNetwork(netk_name=netkName)
                if op == 'delete':
                    try:
                        if netkName.startswith('ovs'):OVS.ovsDelBr(brName=netkName)
                        elif netkName.startswith('br'):
                            BRCTL.brctlDownBr(brName=netkName)
#                             BRCTL.brctlDelBr(brName=netkName)
                        SSH.close()
                    except:
                        pass
                    status = NETWORK.deleteNetwork(netk)
                    VMS.close() 
                    if status == 0:return JsonResponse({"code":200,"data":None,"msg":"网络删除成功"})  
                    else:return JsonResponse({"code":500,"data":None,"msg":"网络删除失败"})     
            except Exception,e:
                return JsonResponse({"code":500,"msg":"获取网络失败。","data":e}) 
        else:
            return JsonResponse({"code":500,"msg":"不支持的操作。","data":e})                                 