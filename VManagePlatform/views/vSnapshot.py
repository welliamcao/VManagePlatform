#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.data.vMserver import VMServer
from VManagePlatform.tasks import revertSnapShot
from VManagePlatform.tasks import snapInstace      
from VManagePlatform.tasks import recordLogs
        
@login_required
def handleSnapshot(request):
    if request.method == "POST":
        op = request.POST.get('op')
        server_id = request.POST.get('server_id')
        insName = request.POST.get('vm_name')
        snapName = request.POST.get('snap_name')
        if op in ['view','resume','delete','add']:
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
                if op == 'view':
                    snap = INSTANCE.snapShotView(instance, snapName)
                    VMS.close()
                    if snap:return JsonResponse({"code":200,"data":snap.replace('<','&lt;').replace('>','&gt;'),"msg":"查询成功."})
                    else:return JsonResponse({"code":500,"data":"查无结果","msg":"查无结果"})
                elif op == 'resume':
                    revertSnapShot.delay(request.POST,request.user)
                    VMS.close()
                    return JsonResponse({"code":200,"data":None,"msg":"快照恢复任务提交成功。"})
                elif op == 'add':
                    snapInstace.delay(request.POST,request.user)
                    VMS.close() 
                    return  JsonResponse({"code":200,"data":None,"msg":"快照任务提交成功."})
                elif op == 'delete':
                    snap = INSTANCE.snapShotDelete(instance, snapName)  
                    VMS.close() 
                    recordLogs.delay(user=request.user,action=op+'_snap',status=snap,vm_name=insName)
                    if snap == 0:return JsonResponse({"code":200,"data":None,"msg":"快照删除成功"})  
                    else:return JsonResponse({"code":500,"data":None,"msg":"快照删除失败"})                                  
            except Exception,e:
                return JsonResponse({"code":500,"msg":"虚拟机快照操作失败。。","data":e}) 
        else:
            return JsonResponse({"code":500,"msg":"不受支持的操作。","data":e})