#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from rest_framework import serializers
from VManagePlatform.models import VmServer,VmLogs

class VmServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmServer
        fields = ('id', 'server_ip', 'hostname', 'username','instance',
                  'passwd','mem','status','cpu_total','vm_type','createTime')
        
        
class VmLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmLogs
        fields = ('id', 'server_id', 'vm_name', 'content','user',
                  'status','isRead','create_time','result')