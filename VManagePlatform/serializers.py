#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from rest_framework import serializers
from VManagePlatform.models import VmServer,VmLogs

class VmServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmServer
        fields = ('id', 'server_ip', 'hostname', 'uri','instance',
                  'max_vcpu','mem','cpu_mhz','cpu_models','status',
                  'cpu_arch','cpu_total','vm_type','vm_version')
        
        
class VmLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmLogs
        fields = ('id', 'server_id', 'vm_name', 'content','user',
                  'status','isRead','create_time')