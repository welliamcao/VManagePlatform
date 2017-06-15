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
from VManagePlatform.restfull import rest_vMserver


urlpatterns = [
#     url(r'^admin/', include(admin.site.urls)),
    url(r'^$',vComs.index),
    url(r'^login/',vComs.login),
    url(r'^register/',vUser.register),
    url(r'^usermanage/',vUser.usermanage),
    url(r'^groupmanage/',vUser.groupmanage),
    url(r'^configTask/',vTasks.configTask),
    url(r'^viewTask/',vTasks.viewTask),
    url(r'^noperm/',vComs.permission),
    url(r'^addServer/',vServer.addVmServer),
    url(r'^listServer/',vServer.listVmServer),
    url(r'^viewServer/',vServer.viewVmServer),
    url(r'^addInstance/',vInstance.addInstance),
    url(r'^listInstance/',vInstance.listInstance),
    url(r'^modfInstance/',vInstance.modfInstance),
    url(r'^handleInstance/$',vInstance.handleInstance),
    url(r'^viewInstance/$',vInstance.viewInstance),
    url(r'^tempInstance/$',vInstance.tempInstance),
    url(r'^addStorage/$',vStorage.addStorage),
    url(r'^handleStorage/$',vStorage.handleStorage),
    url(r'^listStorage/$',vStorage.listStorage),
    url(r'^viewStorage/$',vStorage.viewStorage),  
    url(r'^handleVolume/$',vVolume.handleVolume),
    url(r'^api/vmserver/$', rest_vMserver.vmServer_list), 
    url(r'^api/vmserver/(?P<id>[0-9]+)/$', rest_vMserver.vmServer_detail), 
    url(r'^handleSnapshot/',vSnapshot.handleSnapshot),
    url(r'^configNetwork/',vNetwork.configNetwork),
    url(r'^handleNetwork/',vNetwork.handleNetwork),
    url(r'^configDhcp/',vDhcps.configDhcp),
    url(r'^handleDhcp/',vDhcps.handleDhcp),
    url(r'^profile/',vProfile.profile),
    url(r'^vnc/',vComs.run_vnc),
    url(r'^api/vmserver/(?P<id>[0-9]+)/$', rest_vMserver.vmServer_detail),
    url(r'^logout',vComs.logout),
]
urlpatterns = format_suffix_patterns(urlpatterns)