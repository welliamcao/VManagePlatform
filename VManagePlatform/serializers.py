#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from rest_framework import serializers
from VManagePlatform.models import VmServer

class VmServerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VmServer
        fields = ('id', 'server_ip', 'hostname', 'uri','instance',
                  'max_vcpu','mem','cpu_mhz','cpu_models','status',
                  'cpu_arch','cpu_total','vm_type','vm_version')