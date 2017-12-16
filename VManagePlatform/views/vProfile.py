#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from VManagePlatform.models import VmLogs,VmServerInstance,VmServer
from django.contrib.auth.models import User

@login_required
def profile(request):
    if request.method == "GET":
        try:
            if request.user.is_superuser:
                vmList = VmServerInstance.objects.select_related().all().order_by("-id")
            else:
                vmList = VmServerInstance.objects.select_related().filter(owner=request.user).all().order_by("-id")[0:200]
            logList = VmLogs.objects.filter(user=request.user).all().order_by("-id")[0:10]
        except:
            logList = None
            vmList = None
        return render_to_response('profile.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"用户配置","url":'/profile'}],
                                   "logList":logList,"vmList":vmList
                                   },context_instance=RequestContext(request))
    elif request.method == "POST":
        op = request.POST.get('op')
        if op in ['assign','password','viewlog']:
            if op == 'assign':
                try:
                    server = VmServer.objects.get(id=int(request.POST.get('server')))
                    instance = VmServerInstance.objects.get(server_id=server,name=request.POST.get('name'))
                    instance.owner = request.POST.get('username')
                    instance.save()
                    return JsonResponse({"code":200,"data":None,"msg":"虚拟机分配成功。"})
                except Exception,e:
                    return JsonResponse({"code":500,"data":e,"msg":"虚拟机分配失败。"})
            elif op == 'password':
                if request.POST.get('n_pwd') == request.POST.get('c_pwd'):
                    try:
                        user = User.objects.get(username=request.POST.get('username'))
                        user.set_password(request.POST.get('c_pwd'))
                        user.save()
                        return JsonResponse({'msg':"密码修改成功。","code":200,'data':None})
                    except Exception,e:
                        return JsonResponse({'msg':'failed',"code":500,'data':"系统忙请稍后在尝试。"}) 
                else:
                    return JsonResponse({'msg':'新密码不一致，修改密码失败。',"code":500,'data':None})
            elif op == 'viewlog':
                try:
                    count = int(request.POST.get('count')) - 10
                    logList = VmLogs.objects.filter(user=request.user).all().order_by("-id")[count:int(request.POST.get('count'))]
                    dataList = []
                    for ds in logList:
                        data  = dict()
                        data['id'] = ds.id
                        data['content'] = ds.content
                        data['user'] = ds.user
                        data['vm_name'] = ds.vm_name
                        data['status'] = ds.status
                        data['create_time'] = ds.create_time
                        data['result'] = ds.result
                        dataList.append(data)
                    if len(dataList) > 0:return JsonResponse({'msg':"数据加载成功。","code":200,'data':dataList})
                    else:return JsonResponse({'msg':'没有更多的消息',"code":500,'data':None})
                except Exception,e:
                    return JsonResponse({'msg':str(e),"code":500,'data':None})             
        else:return JsonResponse({"code":500,"data":None,"msg":"不支持的操作。"})