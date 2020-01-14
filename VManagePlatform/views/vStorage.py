#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.models import VmServer
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from VManagePlatform.const.Const import StorageTypeXMLConfig



@login_required
def addStorage(request,id):
    try:
        vServer = VmServer.objects.get(id=id)
    except Exception,e:
        return JsonResponse({"code":500,"msg":"找不到主机资源","data":e})
    if request.method == "POST" and request.user.has_perm('VManagePlatform.add_vmserverinstance'):
        pool_xml = StorageTypeXMLConfig(pool_type=request.POST.get('pool_type'),pool_name=request.POST.get('pool_name'),
                                        pool_spath=request.POST.get('pool_spath'),pool_tpath=request.POST.get('pool_tpath'),
                                        pool_host=request.POST.get('pool_host'))
        if pool_xml:           
            try:
                VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
                STORAGE = VMS.genre(model='storage')
                pool = STORAGE.getStoragePool(pool_name=request.POST.get('pool_name'))
                if pool is False:
                    storage = STORAGE.createStoragePool(pool_xml)
                    VMS.close()
                    if isinstance(storage,int):return JsonResponse({"code":200,"msg":"存储池添加成功","data":None})  
                    else:return  JsonResponse({"code":500,"msg":"创建存储池失败。","data":None}) 
                else:
                    VMS.close()
                    return  JsonResponse({"code":400,"msg":"存储池已经存在。","data":None})
            except Exception,e:
                return JsonResponse({"code":500,"msg":"找到主机资源","data":e})
        else:
            return JsonResponse({"code":500,"msg":"不支持的存储类型或者您没有权限操作此项","data":None})
    if request.method == "GET":
        return render_to_response('vmStorage/add_storage.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"存储池管理","url":"/listStorage/%d/" % vServer.id},
                                                                    ],
                                    "vmServer":vServer}, context_instance=RequestContext(request))
        
@login_required
def listStorage(request,id):        
    if request.method == "GET":
        try:
            vServer = VmServer.objects.get(id=id)
        except Exception,e:
            return render_to_response('404.html',context_instance=RequestContext(request))
        try:
            VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
            SERVER = VMS.genre(model='server')
            if SERVER:
                storageList = SERVER.getVmStorageInfo()
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            return render_to_response('404.html',context_instance=RequestContext(request))        
        return render_to_response('vmStorage/list_storage.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"存储池管理","url":"/listStorage/%d/" % vServer.id}],
                                    "vmServer":vServer,"storageList":storageList}, context_instance=RequestContext(request))

@login_required
def viewStorage(request,id,name): 
    if request.method == "GET":
        try:
            vServer = VmServer.objects.get(id=id)
        except:
            return render_to_response('404.html',context_instance=RequestContext(request))        
        try:
            VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
            STORAGE = VMS.genre(model='storage')
            if STORAGE:
                storage = STORAGE.getStorageInfo(name)
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            return render_to_response('404.html',context_instance=RequestContext(request))    
        return render_to_response('vmStorage/view_storage.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"存储池管理","url":"/listStorage/%d/" % vServer.id},
                                                                    {"name":"存储池详情","url":"/viewStorage/%d/%s/" % (vServer.id,name)}],
                                    "vmServer":vServer,"storage":storage}, context_instance=RequestContext(request))
        
@login_required
def handleStorage(request,id):
    if request.method == "POST":
        try:
            vServer = VmServer.objects.get(id=id)
        except Exception,e:
            return JsonResponse({"code":500,"msg":"找不到主机资源","data":e})      
        op = request.POST.get('op') 
        pool_name = request.POST.get('pool_name') 
        if op in ['delete','disable','refresh'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
            STORAGE = VMS.genre(model='storage')
            pool = STORAGE.getStoragePool(pool_name=pool_name)  
            if pool:
                if op == 'delete':                                   
                    result = STORAGE.deleteStoragePool(pool=pool)
                elif op == 'refresh': 
                    result = STORAGE.refreshStoragePool(pool=pool)
                VMS.close()
                if isinstance(result,int):return  JsonResponse({"code":200,"msg":"操作成功。","data":None})
                else:return  JsonResponse({"code":500,"msg":result})                    
            else:return JsonResponse({"code":500,"msg":"存储池不存在。","data":None})
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持操作或者您没有权限操作此项"})                        
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})
