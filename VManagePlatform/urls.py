"""VManagePlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from VManagePlatform.views import vServer
from VManagePlatform.views import vInstance
from VManagePlatform.views import vStorage
from VManagePlatform.views import vVolume
from VManagePlatform.views import vComs
from VManagePlatform.views import vProfile
from VManagePlatform.views import vSnapshot
from VManagePlatform.views import vNetwork
from VManagePlatform.views import vDhcps
from VManagePlatform.views import vUser
from VManagePlatform.views import vTasks
from rest_framework.urlpatterns import format_suffix_patterns
from VManagePlatform.restfull import rest_vMserver,rest_vmlog


urlpatterns = [
#     url(r'^admin/', include(admin.site.urls)),
    url(r'^$',vComs.index),
    url(r'^login/',vComs.login),
    url(r'^register/',vUser.register),
    url(r'^user/$',vUser.user),
    url(r'^user/auth/(?P<id>[0-9]+)/$',vUser.usermanage),
    url(r'^group/$',vUser.group),
    url(r'^configTask/',vTasks.configTask),
    url(r'^viewTask/',vTasks.viewTask),
    url(r'^noperm/',vComs.permission),
    url(r'^addServer/',vServer.addVmServer),
    url(r'^listServer/',vServer.listVmServer),
    url(r'^viewServer/(?P<id>[0-9]+)/$',vServer.viewVmServer),
    url(r'^addInstance/(?P<id>[0-9]+)/$',vInstance.addInstance),
    url(r'^listInstance/(?P<id>[0-9]+)/$',vInstance.listInstance),
    url(r'^modfInstance/(?P<id>[0-9]+)/$',vInstance.modfInstance),
    url(r'^handleInstance/(?P<id>[0-9]+)/$',vInstance.handleInstance),
    url(r'^viewInstance/(?P<id>[0-9]+)/(?P<vm>\w.+)/$',vInstance.viewInstance),
    url(r'^status/cpu/(?P<id>[0-9]+)/(?P<vm>\w.+)/$',vInstance.instanceCpuStatus),
    url(r'^status/net/(?P<id>[0-9]+)/(?P<vm>\w.+)/$',vInstance.instanceNetStatus),
    url(r'^status/disk/(?P<id>[0-9]+)/(?P<vm>\w.+)/$',vInstance.instanceDiskStatus),
    url(r'^tempInstance/$',vInstance.tempInstance),
    url(r'^addStorage/(?P<id>[0-9]+)/$',vStorage.addStorage),
    url(r'^handleStorage/(?P<id>[0-9]+)/$',vStorage.handleStorage),
    url(r'^listStorage/(?P<id>[0-9]+)/$',vStorage.listStorage),
    url(r'^viewStorage/(?P<id>[0-9]+)/(?P<name>\w.+)/$',vStorage.viewStorage),  
    url(r'^handleVolume/$',vVolume.handleVolume),
    url(r'^api/vmserver/$', rest_vMserver.vmServer_list), 
    url(r'^api/vmserver/(?P<id>[0-9]+)/$', rest_vMserver.vmServer_detail), 
    url(r'^handleSnapshot/(?P<id>[0-9]+)/$',vSnapshot.handleSnapshot),
    url(r'^configNetwork/(?P<id>[0-9]+)/$',vNetwork.configNetwork),
    url(r'^handleNetwork/(?P<id>[0-9]+)/$',vNetwork.handleNetwork),
    url(r'^configDhcp/',vDhcps.configDhcp),
    url(r'^handleDhcp/',vDhcps.handleDhcp),
    url(r'^profile/',vProfile.profile),
    url(r'^vnc/(?P<id>[0-9]+)/(?P<vnc>\d+)/(?P<uuid>.*)/',vComs.run_vnc),
    url(r'^api/vmserver/(?P<id>[0-9]+)/$', rest_vMserver.vmServer_detail),
    url(r'^api/logs/$', rest_vmlog.vmlog_list),
    url(r'^api/logs/(?P<id>[0-9]+)/$', rest_vmlog.vmlog_detail),
    url('^api/log/(?P<username>.+)/$', rest_vmlog.LogsList.as_view()),
    url(r'^logout',vComs.logout),
]
urlpatterns = format_suffix_patterns(urlpatterns)
