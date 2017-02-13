"""
WSGI config for VManagePlatform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
from django.conf import settings
from multiprocessing import Process

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "VManagePlatform.settings")

application = get_wsgi_application()


def worker():
    '''
        Multi process service VNC start
    '''
    websockify_path = os.path.join(os.getcwd(), 'vnc', 'utils', 'websockify')
    web_path =  os.path.join(os.getcwd(), 'vnc', 'utils')
    cmd = u'python %s --web=%s --target-config=%s %s' %(websockify_path, web_path, settings.VNC_TOKEN_PATH, settings.VNC_PROXY_PORT)
    os.system(cmd)

def start_websockify():
    '''
        Start the VNC agent service
        ./vnc/utils/websockify --web=. --target-config=vnc_tokens 6080
        {'target_cfg': '/home/xiaofei/work/noVNC/vnc_tokens', 'listen_port': 6080}
    '''

    print u'start vnc proxy..'

    t = Process(target=worker, args=())
    t.start()

    print u'vnc proxy started..'

start_websockify()