#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from django.http import JsonResponse
from django.shortcuts import render_to_response
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.models import VmServer
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required

@login_required
def listVmServer(request):
    hostList = VmServer.objects.all().order_by("-id")
    return render_to_response('vmServer/list_server.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"主机列表","url":"/listServer"}],
                                   "dataList":hostList,"model":"server"},
                                  context_instance=RequestContext(request))  
    

@login_required
@permission_required('VManagePlatform.read_vmserver',login_url='/noperm/')
def viewVmServer(request,id):
    try:
        vServer = VmServer.objects.get(id=id)
    except:
        return render_to_response('404.html',context_instance=RequestContext(request))

    VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
    SERVER = VMS.genre(model='server') 
    if SERVER:
        vmServer =  SERVER.getVmServerInfo()
    else:
        return render_to_response('404.html',context_instance=RequestContext(request))

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
                                                                    {"name":vmServer.get('name'),"url":"/viewServer/%d/" % vServer.id}],
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
        try:     
            VmServer.objects.create(hostname=request.POST.get('hostname'),
                                    username=request.POST.get('username',None),
                                    vm_type=request.POST.get('vm_type'),
                                    server_ip=request.POST.get('server_ip'),
                                    passwd=request.POST.get('passwd',None),
                                    status=0,)
            return render_to_response('vmServer/add_server.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"添加主机","url":"/addServer"}]},
                                  context_instance=RequestContext(request))
        except Exception,e:
            return render_to_response('vmServer/add_server.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机管理器","url":'#'},{"name":"添加主机","url":"/addServer"}],
                                   "errorInfo":e},
                                  context_instance=RequestContext(request))
            