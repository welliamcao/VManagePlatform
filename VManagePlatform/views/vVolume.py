#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from VManagePlatform.models import VmServer
from django.contrib.auth.decorators import login_required
from VManagePlatform.utils.vMConUtils import LibvirtManage
from VManagePlatform.utils import vMUtil


@login_required
def handleVolume(request):
    if request.method == "POST":
        op = request.POST.get('op') 
        server_id = request.POST.get('server_id') 
        pool_name = request.POST.get('pool_name') 
        if op in ['delete','add', 'clone'] and request.user.has_perm('VManagePlatform.change_vmserverinstance'):
            try:
                vServer = VmServer.objects.get(id=server_id)
            except:
                return JsonResponse({"code":500,"data":None,"msg":"主机不存在。"})

            VMS = LibvirtManage(vServer.server_ip,vServer.username, vServer.passwd, vServer.vm_type)
            STORAGE = VMS.genre(model='storage')

            if STORAGE:
                pool = STORAGE.getStoragePool(pool_name=pool_name)
                if pool:
                    volume = STORAGE.getStorageVolume(pool=pool, volume_name=request.POST.get('vol_name'))
                    if op == 'add':
                        if volume:
                            return JsonResponse({"code":500,"data":None,"msg":"卷已经存在"})
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
                        else:
                            return  JsonResponse({"code":500,"data":None,"msg":"卷删除失败，卷不存在。"})
                    elif op == 'clone':
                        if not volume:
                            return JsonResponse({"code":500,"data":None,"msg":"卷不存在"})

                        target_volume_name = "clone_" + request.POST.get('vol_name')
                        new_vol_name = request.POST.get('new_vol_name')
                        if new_vol_name:
                            target_volume_name = new_vol_name

                        new_volume = STORAGE.getStorageVolume(pool=pool, volume_name=new_vol_name)
                        if new_volume:
                            return JsonResponse({"code":500,"data":None,"msg":"卷已经存在"})

                        vol_format = vMUtil.get_xml_path(volume.XMLDesc(0), "/volume/target/format/@type") #卷格式

                        vol_clone_xml = """
                                        <volume>
                                            <name>%s</name>
                                            <capacity>0</capacity>
                                            <allocation>0</allocation>
                                            <target>
                                                <format type='%s'/>
                                            </target>
                                        </volume>""" % (target_volume_name, vol_format)
                        pool.createXMLFrom(vol_clone_xml, volume, False)   #从vol卷复制卷，阻塞
                        return JsonResponse({"code": 200, "data": None, "msg": "卷克隆成功。"})
                else:
                    return  JsonResponse({"code":500,"data":None,"msg":"存储池不存在。"})
            else:
                return  JsonResponse({"code":500,"data":None,"msg":"主机连接失败。"})
        else:
            return  JsonResponse({"code":500,"data":None,"msg":"不支持操作。"})                                 
    else:
        return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作。"})              