#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from VManagePlatform.data.vMserver import VMServer
from django.contrib.auth.decorators import login_required
from VManagePlatform.utils.vMConUtils import LibvirtManage


@login_required
def handleVolume(request):
    if request.method == "POST":
        op = request.POST.get('op') 
        server_id = request.POST.get('server_id') 
        pool_name = request.POST.get('pool_name') 
        if op in ['delete','add'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            try:
                vmServer = VMServer.selectOneHost(id=server_id)
            except:
                return JsonResponse({"code":500,"data":None,"msg":"主机不存在。"})                 
            VMS = LibvirtManage(uri=vmServer.uri) 
            STORAGE = VMS.genre(model='storage')
            if STORAGE:
                pool = STORAGE.getStoragePool(pool_name=pool_name)
                if pool:
                    volume = STORAGE.getStorageVolume(pool=pool, volume_name=request.POST.get('vol_name'))
                    if op == 'add':
                        if volume:return JsonResponse({"code":500,"data":None,"msg":"卷已经存在"})
                        else:
                            status = STORAGE.createVolumes(pool=pool, volume_name=request.POST.get('vol_name'),
                                                volume_capacity=int(request.POST.get('vol_size')),drive=request.POST.get('vol_drive'))
                            VMS.close()
                            if isinstance(status,str) :return  JsonResponse({"code":500,"data":None,"msg":status})
                            else:return  JsonResponse({"code":200,"data":None,"msg":"卷创建成功。"})
                    elif op == 'delete':
                        if volume:
                            status = STORAGE.deleteVolume(pool=pool, volume_name=request.POST.get('vol_name'))
                            VMS.close()
                            if isinstance(status, str):return  JsonResponse({"code":500,"data":status,"msg":"卷删除失败。"})
                            else:return  JsonResponse({"code":200,"data":None,"msg":"卷删除成功。"})
                        else:return  JsonResponse({"code":500,"data":None,"msg":"卷删除失败，卷不存在。"})
                else:return  JsonResponse({"code":500,"data":None,"msg":"存储池不存在。"})
            else:
                return  JsonResponse({"code":500,"data":None,"msg":"主机连接失败。"})
        else:
            return  JsonResponse({"code":500,"data":None,"msg":"不支持操作。"})                                 
    else:
        return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作。"})              