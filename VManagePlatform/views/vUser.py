#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from django.contrib.auth.models import User,Permission,Group
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required


def register(request):
    if request.method == "POST":
        if request.POST.get('password') == request.POST.get('c_password'):
            try:
                user = User.objects.filter(username=request.POST.get('username'))
                if len(user)>0:return JsonResponse({"code":500,"data":None,"msg":"注册失败，用户已经存在。"})
                else: 
                    user = User()
                    user.username = request.POST.get('username')
                    user.email = request.POST.get('email')
                    user.is_staff = 0
                    user.is_active = 0
                    user.is_superuser = 0                        
                    user.set_password(request.POST.get('password'))
                    user.save()
                    return JsonResponse({"code":200,"data":None,"msg":"用户注册成功"})
            except Exception,e:
                return JsonResponse({"code":500,"data":None,"msg":"用户注册失败"}) 
        else:return JsonResponse({"code":500,"data":None,"msg":"密码不一致，用户注册失败。"}) 
        

@login_required      
@permission_required('auth.change_group',login_url='/noperm/')    
def groupmanage(request):
    if request.method == "GET":
        op = request.GET.get('op')
        if op == 'list':
            permList = Permission.objects.all()
            try:
                groupList = []
                for group in  Group.objects.all():
                    data = dict()
                    data['id'] = group.id
                    data['name'] = group.name 
                    permIdList = []
                    #获取组权限
                    for perm in group.permissions.values():
                        permIdList.append(perm.get('id'))
                    data['perm_id'] = permIdList
                    groupList.append(data)
            except Exception,e:
                print e
                groupList = []
            return render_to_response('vmUser/group_manage.html',{"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"用户组管理","url":'/groupmanage/?op=list'}],
                                                "groupList":groupList,"permList":permList},
                                  context_instance=RequestContext(request)) 
    elif request.method == "POST":
        op = request.POST.get('op')
        if op == 'add' and request.user.has_perm('auth.add_group'):
            try:
                group = Group()
                group.name = request.POST.get('name')
                group.save()
                permList = [ int(i) for i in request.POST.get('perm').split(',')]
                for permId in permList:
                    perm = Permission.objects.get(id=permId)
                    group.permissions.add(perm)
                group.save()
                return  JsonResponse({"code":200,"data":None,"msg":"用户组添加成功"})
            except Exception,e:
                print e
                return  JsonResponse({"code":500,"data":None,"msg":"用户组添加失败"}) 
        if op in ['delete','modify'] and request.user.has_perm('VManagePlatform.change_group'):
            try:
                group = Group.objects.get(id=request.POST.get('id'))
            except:
                return JsonResponse({"code":500,"data":None,"msg":"操作失败用户组不存在"})
            if op == 'delete':
                try:
                    group.delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"用户组删除失败，用户组不存在"})   
            elif op == 'modify':
                try:
                    group.name = request.POST.get('name')
                    #如果权限key不存在就单做清除权限
                    if request.POST.get('perm') is None:group.permissions.clear()
                    else:
                        groupPermList = []
                        for perm in group.permissions.values():
                            groupPermList.append(perm.get('id'))
                        permList = [ int(i) for i in request.POST.get('perm').split(',')]
                        addPermList = list(set(permList).difference(set(groupPermList)))
                        delPermList = list(set(groupPermList).difference(set(permList)))
                        #添加新增的权限
                        for permId in addPermList:
                            perm = Permission.objects.get(id=permId)
                            Group.objects.get(id=request.POST.get('id')).permissions.add(perm)
                        #删除去掉的权限
                        for permId in delPermList:
                            perm = Permission.objects.get(id=permId)
                            Group.objects.get(id=request.POST.get('id')).permissions.remove(perm) 
                    group.save()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except Exception,e:
                    return  JsonResponse({"code":500,"data":e,"msg":"操作失败。"}) 
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})            
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})
          
@login_required    
@permission_required('auth.change_user',login_url='/noperm/')   
def usermanage(request):
    if request.method == "GET":
        op = request.GET.get('op')
        if op == 'list':
            try:
                userList = User.objects.all()
            except Exception,e:
                userList = []
            return render_to_response('vmUser/user_manage.html',{"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"用户管理","url":'/usermanage/?op=list'}],
                                                "userList":userList},
                                  context_instance=RequestContext(request))
        elif op == 'view':
            userPermList = [] 
            userGroupList = []
            try:
                user = User.objects.get(id=request.GET.get('id'))
                #获取用户权限列表
                for perm in user.user_permissions.values():
                    userPermList.append(perm.get('id'))
                #获取用户组列表
                for group in user.groups.values():
                    userGroupList.append(group.get('id'))
                permList = Permission.objects.all()
                groupList = Group.objects.all()
            except Exception,e:
                user = None
                permList = []
                groupList = []
                userPermList = []
            return render_to_response('vmUser/view_user.html',{"user":request.user,
                                                               "localtion":[{"name":"首页","url":'/'},
                                                                            {"name":"用户管理","url":'/usermanage/?op=list'}],
                                                "user":user,"permList":permList,"groupList":groupList,
                                                "userPermList":userPermList,"userGroupList":userGroupList},
                                  context_instance=RequestContext(request))
            
    elif request.method == "POST":
        op = request.POST.get('op')
        if op in ['active','superuser','delete','modify']:
            try:
                user = User.objects.get(id=request.POST.get('id'))
            except:
                return JsonResponse({"code":500,"data":None,"msg":"操作失败用户不存在"})
            if op == 'active':
                try:
                    user.is_active = int(request.POST.get('status'))
                    user.save()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"用户激活失败，用户不存在"})
            elif op == 'superuser':
                try:
                    user.is_superuser = int(request.POST.get('status'))
                    user.save()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"用户激活失败，用户不存在"})
            elif op == 'delete':
                try:
                    user.delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"用户删除失败，用户不存在"})
            elif op == 'modify':
                try:
                    user.is_active = int(request.POST.get('is_active'))
                    user.is_superuser = int(request.POST.get('is_superuser'))
                    user.email = request.POST.get('email')
                    user.username = request.POST.get('username')
                    #如果权限key不存在就单做清除权限
                    if request.POST.get('perm') is None:user.user_permissions.clear()
                    else:
                        userPermList = []
                        for perm in user.user_permissions.values():
                            userPermList.append(perm.get('id'))
                        permList = [ int(i) for i in request.POST.get('perm').split(',')]
                        addPermList = list(set(permList).difference(set(userPermList)))
                        delPermList = list(set(userPermList).difference(set(permList)))
                        #添加新增的权限
                        for permId in addPermList:
                            perm = Permission.objects.get(id=permId)
                            User.objects.get(id=request.POST.get('id')).user_permissions.add(perm)
                        #删除去掉的权限
                        for permId in delPermList:
                            perm = Permission.objects.get(id=permId)
                            User.objects.get(id=request.POST.get('id')).user_permissions.remove(perm) 
                    #如果用户组key不存在就单做清除用户组  
                    if request.POST.get('group') is None:user.groups.clear()
                    else:
                        userGroupList = []
                        for group in user.groups.values():
                            userGroupList.append(group.get('id'))
                        groupList = [ int(i) for i in request.POST.get('group').split(',')]
                        addGroupList = list(set(groupList).difference(set(userGroupList)))
                        delGroupList = list(set(userGroupList).difference(set(groupList)))
                        #添加新增的用户组
                        for groupId in addGroupList:
                            group = Group.objects.get(id=groupId)
                            user.groups.add(group)
                        #删除去掉的用户组
                        for groupId in delGroupList:
                            group = Group.objects.get(id=groupId)
                            user.groups.remove(group)
                    user.save()
                    return  JsonResponse({"code":200,"data":None,"msg":"操作成功"})
                except Exception,e:
                    return  JsonResponse({"code":500,"data":e,"msg":"操作失败。"}) 
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})            
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})