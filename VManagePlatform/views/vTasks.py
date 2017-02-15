#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
from django.http import JsonResponse
from django.shortcuts import render_to_response
from djcelery.models  import PeriodicTask,CrontabSchedule,WorkerState,TaskState,IntervalSchedule
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from celery.registry import tasks
from celery.five import keys, items
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('djcelery.change_periodictask',login_url='/noperm/')
def configTask(request):
    if request.method == "GET":
        #获取注册的任务
        regTaskList = []
        for task in  list(keys(tasks)):
            if task.startswith('VManagePlatform'):regTaskList.append(task)
        try:
            crontabList = CrontabSchedule.objects.all().order_by("-id")
            intervalList = IntervalSchedule.objects.all().order_by("-id")
            taskList = PeriodicTask.objects.all().order_by("-id")
        except:
            crontabList = []
            intervalList = []
            taskList = []
        return render_to_response('vmTasks/config_task.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"任务调度","url":'#'},
                                                                    {"name":"配置中心","url":"/configTask"}],
                                    "crontabList":crontabList,"intervalList":intervalList,"taskList":taskList,
                                    "regTaskList":regTaskList},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        op = request.POST.get('op') 
        if op in ['addCrontab','delCrontab','addInterval',
                  'delInterval','addTask','editTask',
                  'delTask'] and request.user.has_perm('djcelery.change_periodictask'):
            if op == 'addCrontab':
                try:
                    CrontabSchedule.objects.create(minute=request.POST.get('minute'),hour=request.POST.get('hour'),
                                                      day_of_week=request.POST.get('day_of_week'),
                                                      day_of_month=request.POST.get('day_of_month'),
                                                      month_of_year=request.POST.get('month_of_year'),
                                                      )
                    return  JsonResponse({"code":200,"data":None,"msg":"添加成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"添加失败"})
            elif op == 'delCrontab':
                try:
                    CrontabSchedule.objects.get(id=request.POST.get('id')).delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"删除成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"删除失败"})  
            elif op == 'addInterval':
                try:
                    IntervalSchedule.objects.create(every=request.POST.get('every'),period=request.POST.get('period'))
                    return  JsonResponse({"code":200,"data":None,"msg":"添加成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"添加失败"})    
            elif op == 'delInterval':
                try:
                    IntervalSchedule.objects.get(id=request.POST.get('id')).delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"删除成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"删除失败"})
            elif op == 'addTask':
                try:
                    PeriodicTask.objects.create(name=request.POST.get('name'),
                                                interval_id=request.POST.get('interval',None),
                                                task=request.POST.get('task',None),
                                                crontab_id=request.POST.get('crontab',None),
                                                args = request.POST.get('args','[]'),
                                                kwargs = request.POST.get('kwargs','{}'),
                                                queue = request.POST.get('queue',None),
                                                enabled = int(request.POST.get('enabled',1)),
                                                expires = request.POST.get('expires',None)
                                                      )
                    return  JsonResponse({"code":200,"data":None,"msg":"添加成功"})
                except Exception,e:
                    return  JsonResponse({"code":500,"data":e,"msg":"添加失败"})    
            elif op == 'delTask':
                try:
                    PeriodicTask.objects.get(id=request.POST.get('id')).delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"删除成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"删除失败"})
            elif op == 'editTask':
                try:
                    task = PeriodicTask.objects.get(id=request.POST.get('id'))
                    task.name = request.POST.get('name')
                    task.interval_id = request.POST.get('interval',None)
                    task.crontab_id = request.POST.get('crontab',None)
                    task.args = request.POST.get('args')
                    task.kwargs = request.POST.get('kwargs')
                    task.queue = request.POST.get('queue',None)
                    task.expires = request.POST.get('expires',None)
                    task.enabled = int(request.POST.get('enabled'))
                    task.save()
                    return  JsonResponse({"code":200,"data":None,"msg":"修改成功"})
                except Exception,e:
                    return  JsonResponse({"code":500,"data":e,"msg":"修改失败"})
                             
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})            
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})   
    
    
    
@login_required
@permission_required('djcelery.read_periodictask',login_url='/noperm/')
def viewTask(request):
    if request.method == "GET":
        try:
            task = {}
            for ds in PeriodicTask.objects.all():
                task[ds.task] = ds.name
            taskLog = []
            for ds in TaskState.objects.all().order_by("-id")[0:300]:
                if task.has_key(ds.name):ds.name = task[ds.name]
                ds.args = ds.args.replace('[u','[')
                taskLog.append(ds)
        except:
            taskLog = []
        return render_to_response('vmTasks/view_task.html',
                                  {"user":request.user,"localtion":[{"name":"首页","url":'/'},{"name":"任务调度","url":'#'},
                                                                    {"name":"运行日志","url":"/viewTask"}],
                                    "taskLog":taskLog},
                                  context_instance=RequestContext(request))
    elif request.method == "POST":
        op = request.POST.get('op')
        if op in ['view','delete'] and request.user.has_perm('djcelery.change_taskstate'):
            try:
                task = {}
                for ds in PeriodicTask.objects.all():
                    task[ds.task] = ds.name
                taskLog = TaskState.objects.get(id=request.POST.get('id'))
            except:
                return JsonResponse({"code":500,"data":None,"msg":"任务不存在"})
            if op == 'view':
                try:
                    data = dict()
                    work = WorkerState.objects.get(id=taskLog.worker_id)
                    data['id'] = taskLog.id
                    data['task_id'] = taskLog.task_id
                    data['worker'] = work.hostname
                    if task.has_key(taskLog.name):data['name'] = task[taskLog.name]
                    else:data['name'] = taskLog.name
                    data['tstamp'] = taskLog.tstamp
                    data['args'] = taskLog.args.replace('[u','[')
                    data['kwargs'] = taskLog.kwargs
                    data['result'] = taskLog.result
                    data['state'] = taskLog.state
                    data['runtime'] = taskLog.runtime
                    return  JsonResponse({"code":200,"data":data,"msg":"操作成功"})
                except Exception,e:
                    return  JsonResponse({"code":500,"data":None,"msg":"日志查看失败。"})
            elif op == 'delete':
                try:
                    taskLog.delete()
                    return  JsonResponse({"code":200,"data":None,"msg":"删除成功"})
                except:
                    return  JsonResponse({"code":500,"data":None,"msg":"日志删除失败"})
        else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的操作或者您没有权限操作操作此项。"})            
    else:return  JsonResponse({"code":500,"data":None,"msg":"不支持的HTTP操作"})