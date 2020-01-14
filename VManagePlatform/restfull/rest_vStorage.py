#!/usr/bin/env python  
# _#_ coding:utf-8 _*_

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from VManagePlatform.models import VmServer
from VManagePlatform.utils.vMConUtils import LibvirtManage
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie    
@api_view(['GET', 'PUT', 'DELETE'])
def vmStorage_detail(request, serverId, poolName, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        vmServer = VmServer.objects.get(id=serverId)
    except VmServer.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        VMS = LibvirtManage(vmServer.server_ip, vmServer.username, vmServer.passwd, vmServer.vm_type)
        STORAGE = VMS.genre(model='storage')
        if STORAGE:
            storage = STORAGE.getStorageInfo(poolName)
            VMS.close()
            return Response(storage, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    except Exception, e:
        return Response(status=status.HTTP_404_NOT_FOUND)

