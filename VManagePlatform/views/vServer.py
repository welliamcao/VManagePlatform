#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from django.http import JsonResponse
from django.shortcuts import render_to_response
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.data.vMserver import VMServer
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required

@login_required
def listVmServer(request):
    hostList = VMServer.listVmServer()
    return render_to_response('vmServer/list_server.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"主机列表","url":"/listServer"}],
                                   "dataList":hostList,"model":"server"},
                                  context_instance=RequestContext(request))  
    

@login_required
@permission_required('VManagePlatform.read_vmserver',login_url='/noperm/')
def viewVmServer(request):
    if request.GET.get('op') =="view":
        sid = request.GET.get('id')
        vServer = VMServer.selectOneHost(sid)
        VMS = LibvirtManage(vServer.uri)
        SERVER = VMS.genre(model='server') 
        if SERVER:vmServer =  SERVER.getVmServerInfo()
        else:return render_to_response('404.html',context_instance=RequestContext(request))
        if vmServer:
            vmServer['id'] = vServer.id      
            vmServer['server_ip'] = vServer.server_ip
            vmServer['name'] = vServer.hostname
        vmStorage = SERVER.getVmStorageInfo()
        vmInstance = SERVER.getVmInstanceInfo(server_ip=vServer.server_ip)
        vmIns = vmInstance.get('active').get('number') + vmInstance.get('inactice').get('number')
        vmInsList = []
        for vm in vmIns:
            vm['netk'] = ','.join(vm.get('netk'))
            vm['disk'] = vm.get('disks')
            vm.pop('disks')
            vmInsList.append(vm)
        VMS.close()
        return render_to_response('vmServer/index_server.html',
                                      {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"主机列表","url":"/listServer"},
                                                                        {"name":vmServer.get('name'),"url":"/viewServer?op=view&id="+str(vServer.id)}],
                                       "vmServer":vmServer,"model":"instance","vmStorage":vmStorage,"vmInstance":vmInsList},
                                      context_instance=RequestContext(request))             
            
@login_required
@permission_required('VManagePlatform.add_vmserver',login_url='/noperm/')
def addVmServer(request):
    if request.method == "GET":
        return render_to_response('vmServer/add_server.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"添加主机","url":"/addServer"}]},
                                  context_instance=RequestContext(request))
    
    elif  request.method == "POST":
        VMS = LibvirtManage(request.POST.get('vm_uri'))
        SERVER = VMS.genre(model='server')       
        if SERVER:
            VMS.close()
            server = VMServer.insertVmServer(
                                             server_ip=request.POST.get('vm_host'),
                                             uri=request.POST.get('vm_uri'),
                                             vm_type=request.POST.get('vm_type'),
                                             hostname = request.POST.get('vm_hostname'),
                                             status=0, 
                                             )
            if server:                         
                return JsonResponse({"code":200,"msg":"服务器添加成功","data":None})
            else:
                return   JsonResponse({"code":500,"msg":"服务器添加失败，写入数据库失败","data":None})
                   
        else:
            return  JsonResponse({"code":500,"msg":"服务器添加失败，注意URI连通性。","data":None})
            