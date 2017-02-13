#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from VManagePlatform.data.vMdhcp import VMDhcp
from VManagePlatform.utils.vDHCPConfigUtils import DHCPConfig



@login_required
def configDhcp(request):
    if request.method == "GET":
        dataList = VMDhcp.listVmDhcp()
        return render_to_response('vmDhcp/dhcp_network.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"网络管理","url":'/addNetwork'}],
                                   "dataList":dataList},context_instance=RequestContext(request))
    elif  request.method == "POST":
        dhcp = VMDhcp.selectOneMode(mode=request.POST.get('mode'))
        if dhcp:return JsonResponse({"code":500,"msg":"DHCP已经存在","data":None})
        else:
            data = dict()
            if request.POST.has_key('ext-iprange'):
                data['ip_range'] = request.POST.get('ext-iprange') 
            elif request.POST.has_key('int-iprange'):
                data['ip_range'] = request.POST.get('int-iprange')
            data['dhcp_port'] = 'tap-'+request.POST.get('mode')
            data['mode'] = request.POST.get('mode')
            data['server_ip'] = request.POST.get('server_ip')+'/'+request.POST.get('mask')
            data['drive'] = request.POST.get('drive')
            data['gateway'] = request.POST.get('gateway')
            data['brName'] = request.POST.get('brName')
            data['dns'] = request.POST.get('dns')
            dhcp = VMDhcp.insertVmDhcp(data)  
            if dhcp:return JsonResponse({"code":200,"msg":"DHCP添加成功","data":None}) 
            else:return  JsonResponse({"code":500,"msg":"DHCP添加失败","data":None})

@login_required
def handleDhcp(request):
    if request.method == "POST":    
        op = request.POST.get('op')
        dhcp_id = request.POST.get('id')
        if op in ['delete','enable','disable','start','stop']:
            try:
                vMdhcp = VMDhcp.selectOneId(id=dhcp_id)
            except:
                return JsonResponse({"code":500,"data":None,"msg":"DHCP配置不存在。"})
            DHCP = DHCPConfig()  
            if op == 'enable':
                if vMdhcp.isAlive == 1:
                    status = DHCP.enableNets(netnsName=vMdhcp.mode, brName=vMdhcp.brName, 
                                             port=vMdhcp.dhcp_port, ip=vMdhcp.server_ip, 
                                             drive=vMdhcp.drive)
                    if status[0] == 0:
                        VMDhcp.updateisAlive(id=dhcp_id, isAlive=0)
                        return JsonResponse({"code":200,"msg":"激活成功。","data":None})
                    else:
                        return JsonResponse({"code":500,"msg":"激活失败。","data":status[1]})
                else:return JsonResponse({"code":500,"msg":"配置已是激活状态。","data":None})
            elif op == 'disable':
                if vMdhcp.isAlive == 0:
                    status = DHCP.disableNets(netnsName=vMdhcp.mode, brName=vMdhcp.brName, 
                                             port=vMdhcp.dhcp_port,drive=vMdhcp.drive)
                    if status[0] == 0:
                        VMDhcp.updateisAlive(id=dhcp_id, isAlive=1)
                        return JsonResponse({"code":200,"msg":"禁用成功。","data":None})
                    else:
                        return JsonResponse({"code":500,"msg":"禁用失败。","data":status[1]})
                else:return JsonResponse({"code":500,"msg":"配置已是非激活状态。","data":None})                
            elif op == 'start':
                if vMdhcp.isAlive == 0 and vMdhcp.status == 1:
                    if vMdhcp.mode == 'dhcp-ext':
                        status = DHCP.start(netnsName=vMdhcp.mode, iprange=vMdhcp.ip_range, 
                                            port=vMdhcp.dhcp_port, mode='ext', 
                                            gateway=vMdhcp.gateway, dns=vMdhcp.dns)
                    elif vMdhcp.mode == 'dhcp-int':
                        status = DHCP.start(netnsName=vMdhcp.mode, iprange=vMdhcp.ip_range, 
                                            port=vMdhcp.dhcp_port, mode='int', 
                                            gateway=vMdhcp.gateway, dns=vMdhcp.dns)
                    if status[0] == 0:
                        VMDhcp.updateStatus(id=dhcp_id, status=0)
                        return JsonResponse({"code":200,"msg":"DHCP服务启动成功。","data":None})
                    else:
                        return JsonResponse({"code":500,"msg":"DHCP服务启动失败。","data":status[1]}) 
                else:
                    return JsonResponse({"code":500,"msg":"请先激活DHCP配置或者DHCP服务已是启动状态。","data":None})
            elif op == 'stop':
                if vMdhcp.isAlive == 0 and vMdhcp.status == 0:
                    if vMdhcp.mode == 'dhcp-ext':
                        status = DHCP.stop(mode='ext')
                    elif vMdhcp.mode == 'dhcp-int':
                        status = DHCP.stop(mode='int')
                    if status[0] == 0:
                        VMDhcp.updateStatus(id=dhcp_id, status=1)
                        return JsonResponse({"code":200,"msg":"DHCP服务启动成功。","data":None})
                    else:
                        return JsonResponse({"code":500,"msg":"DHCP服务启动失败。","data":status[1]}) 
                else:
                    return JsonResponse({"code":500,"msg":"请先激活DHCP配置或者DHCP服务已是关闭状态。","data":None})  
                
            elif  op == 'delete':  
                if vMdhcp.isAlive == 0 and vMdhcp.status == 0:
                    if vMdhcp.mode == 'dhcp-ext':
                        status = DHCP.stop(mode='ext')
                    elif vMdhcp.mode == 'dhcp-int':
                        status = DHCP.stop(mode='int')
                    if status[0] == 0:
                        status = DHCP.disableNets(netnsName=vMdhcp.mode, brName=vMdhcp.brName, 
                                                  port=vMdhcp.dhcp_port, drive=vMdhcp.drive)
                    if status[0] == 0:
                        result =  VMDhcp.deleteStatus(id=vMdhcp.id)
                elif vMdhcp.isAlive == 0 and vMdhcp.status == 1:
                    status = DHCP.disableNets(netnsName=vMdhcp.mode, brName=vMdhcp.brName, 
                                                  port=vMdhcp.dhcp_port, drive=vMdhcp.drive) 
#                     if status[0] == 0:
                    result = VMDhcp.deleteStatus(id=vMdhcp.id)
                else:
                    result = VMDhcp.deleteStatus(id=vMdhcp.id)
                if result: return JsonResponse({"code":500,"msg":"DHCP服务删除失败。","data":None})
                else: return JsonResponse({"code":200,"msg":"DHCP服务删除成功。","data":None})            
                        
                    
        else:
            return JsonResponse({"code":500,"msg":"不支持的操作。","data":None})      
                