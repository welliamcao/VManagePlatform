#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  

from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response,render
from django.contrib import auth
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from VManagePlatform.models import VmServer,VmServerInstance
from VManagePlatform.utils.vConnUtils import TokenUntils
from VManagePlatform.models import VmLogs


@login_required(login_url='/login')
def index(request):
    vmRun = 0
    vmStop = 0
    serRun = 0
    serStop = 0
    try:
        logList = VmLogs.objects.all().order_by("-id")[0:20]
        vmList = VmServer.objects.all().order_by("-id")
        serList = VmServerInstance.objects.all().order_by("-id")
        for vm in vmList:
            if vm.status == 1:vmRun = vmRun + 1
            else:vmStop = vmStop + 1
        for ser in serList:
            if ser.status == 0:serRun = serRun + 1
            else:serStop = serStop + 1
    except:
        logList = None
        vmList = []
        serList = []
    totalInfo = {"vmRun":vmRun,"vmStop":vmStop,"serTotal":len(serList),
                 "serStop":serStop,"vmTotal":len(vmList),"serRun":serRun}
    return render_to_response('index.html',{"user":request.user,"localtion":[{"name":"首页","url":'/'}],
                                            "logList":logList,"totalInfo":totalInfo,"msgTotal":serStop+vmStop},
                              context_instance=RequestContext(request))

def login(request):
    if request.session.get('username') is not None:
        return HttpResponseRedirect('/profile',{"user":request.user})
    else:
        username = request.POST.get('username')
        password = request.POST.get('password') 
        user = auth.authenticate(username=username,password=password)
        if user and user.is_active:
            auth.login(request,user)
            request.session['username'] = username
            return HttpResponseRedirect('/profile',{"user":request.user})
        else:
            if request.method == "POST":
                return render_to_response('login.html',{"login_error_info":"用户名不错存在，或者密码错误！"},
                                                        context_instance=RequestContext(request))  
            else:
                return render_to_response('login.html',context_instance=RequestContext(request)) 


          
@login_required
def permission(request,args=None):
    return render_to_response('noperm.html',{"user":request.user},
                                  context_instance=RequestContext(request))    

        
@login_required
def run_vnc(request,id,vnc,uuid):
    '''
        Call the VNC proxy for remote control
    '''
    vServer = VmServer.objects.get(id=id)
    tokenStr = uuid + ': ' + vServer.server_ip + ':' + str(vnc)
    TokenUntils.writeVncToken(filename=uuid,token=tokenStr) 
    return render(request, 'vnc/vnc_auto.html',{"vnc_port":settings.VNC_PROXY_PORT,
                                                    "vnc_token":uuid,
                                                    })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')