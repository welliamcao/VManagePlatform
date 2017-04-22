#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.data.vMserver import VMServer
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from VManagePlatform.const.Const import StorageTypeXMLConfig



@login_required
def addStorage(request):
    if request.method == "POST" and request.user.has_perm('VManagePlatform.add_vmserverinstance'):
        pool_xml = StorageTypeXMLConfig(pool_type=request.POST.get('pool_type'),pool_name=request.POST.get('pool_name'),
                                        pool_spath=request.POST.get('pool_spath'),pool_tpath=request.POST.get('pool_tpath'),
                                        pool_host=request.POST.get('pool_host'))
        if pool_xml:
            try:
                vMserver = VMServer.selectOneHost(id=request.POST.get('pool_server'))
                try:
                    VMS = LibvirtManage(uri=vMserver.uri) 
                except:
                    return  JsonResponse({"code":500,"msg":"连接虚拟服务器失败。","data":None})
                STORAGE = VMS.genre(model='storage')
                pool = STORAGE.getStoragePool(pool_name=request.POST.get('pool_name'))
                if pool is False:
                    storage = STORAGE.createStoragePool(pool_xml)
                    VMS.close()
                    if storage:return JsonResponse({"code":200,"msg":"存储池添加成功","data":None})  
                    else:return  JsonResponse({"code":500,"msg":"创建存储池失败。","data":None}) 
                else:
                    VMS.close()
                    return  JsonResponse({"code":400,"msg":"存储池已经存在。","data":None})
            except Exception,e:
                return JsonResponse({"code":500,"msg":"找到主机资源","data":e})
        else:
            return JsonResponse({"code":500,"msg":"不支持的存储类型或者您没有权限操作此项","data":None})
        
@login_required
def listStorage(request):        
    if request.method == "GET":
        vMserverId = request.GET.get('id')
        vmServer = VMServer.selectOneHost(id=vMserverId)
        try:
            VMS = LibvirtManage(uri=vmServer.uri) 
            SERVER = VMS.genre(model='server')
            if SERVER:
                storageList = SERVER.getVmStorageInfo()
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            return render_to_response('404.html',context_instance=RequestContext(request))        
        return render_to_response('vmStorage/list_storage.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"存储池管理","url":"/listStorage/?id=%d" % vmServer.id}],
                                    "vmServer":vmServer,"storageList":storageList}, context_instance=RequestContext(request))

@login_required
def viewStorage(request): 
    if request.method == "GET":
        vMserverId = request.GET.get('id')
        pool_name = request.GET.get('pool')
        vmServer = VMServer.selectOneHost(id=vMserverId)
        try:
            VMS = LibvirtManage(uri=vmServer.uri) 
            STORAGE = VMS.genre(model='storage')
            if STORAGE:
                storage = STORAGE.getStorageInfo(pool_name)
                VMS.close()
            else:return render_to_response('404.html',context_instance=RequestContext(request))
        except Exception,e:
            return render_to_response('404.html',context_instance=RequestContext(request))    
        return render_to_response('vmStorage/view_storage.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"虚拟机实例","url":'#'},
                                                                    {"name":"存储池管理","url":"/listStorage/?id=%d" % vmServer.id},
                                                                    {"name":"存储池详情","url":"/viewStorage/?id=%d&pool={{ ds.pool_name }}" % vmServer.id}],
                                    "vmServer":vmServer,"storage":storage}, context_instance=RequestContext(request))
        
@login_required
def handleStorage(request):
    if request.method == "POST":
        op = request.POST.get('op') 
        server_id = request.POST.get('server_id') 
        pool_name = request.POST.get('pool_name') 
        if op in ['delete','disable','refresh'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            try:
                vMserver = VMServer.selectOneHost(id=server_id)
                VMS = LibvirtManage(uri=vMserver.uri) 
            except Exception,e:
                return  JsonResponse({"code":500,"msg":"服务器连接失败。。","data":e})
            STORAGE = VMS.genre(model='storage')
            pool = STORAGE.getStoragePool(pool_name=pool_name)  
            if pool:
                if op == 'delete':                                   
                    result = STORAGE.deleteStoragePool(pool=pool)
                elif op == 'refresh': 
                    result = STORAGE.refreshStoragePool(pool=pool)
                VMS.close()
                if result:return  JsonResponse({"code":200,"msg":"操作成功。","data":None})
                else:return  JsonResponse({"code":500,"msg":"操作失败。","data":None})                    
            else:return JsonResponse({"code":500,"msg":"存储池不存在。","data":e}) 
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持操作或者您没有权限操作此项"})                        
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})                