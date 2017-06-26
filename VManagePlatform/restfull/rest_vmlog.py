#!/usr/bin/env python  
# _#_ coding:utf-8 _*_
from VManagePlatform.serializers import VmLogsSerializer
from rest_framework import status
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from VManagePlatform.models import VmLogs
from rest_framework import generics
from django.db.models import Q 

@api_view(['GET', 'POST' ])
def vmlog_list(request,format=None):
    """
    List all order, or create a server assets order.
    """
    if request.method == 'GET':      
        snippets = VmLogs.objects.all()
        serializer = VmLogsSerializer(snippets, many=True)
        return Response(serializer.data)  
       
    
@api_view(['GET', 'PUT', 'DELETE'])
def vmlog_detail(request, id,format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = VmLogs.objects.get(id=id)
    except VmLogs.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
 
    if request.method == 'GET':
        serializer = VmLogsSerializer(snippet)
        return Response(serializer.data)
 
    elif request.method == 'PUT':
        serializer = VmLogsSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
     
    elif request.method == 'DELETE':
        if not request.user.has_perm('vmanageplatform.delete_vmserver'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT) 
    
class LogsList(generics.ListAPIView):
    serializer_class = VmLogsSerializer 
    def get_queryset(self):
        user = self.request.user
        username = self.kwargs['username']
        if str(user) == str(username):
            return VmLogs.objects.filter(user=user,isRead=0).order_by("id")
        else:return []