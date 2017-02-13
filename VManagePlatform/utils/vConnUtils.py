#!/usr/bin/env python  
# _#_ coding:utf-8 _*_ 
'''共用工具类方法'''
from random import choice
import string,hashlib
from django.conf import settings 


class TokenUntils(): 
    @staticmethod
    def writeVncToken(filename,token):
#         if os.path.exists(settings.VNC_TOKEN_PATH +"/" + filename) is False:
        with open(settings.VNC_TOKEN_PATH +"/" + filename,r'wb') as f:
            f.write(token)
            f.write("\n")
            f.close()
    @staticmethod
    def makeToken(str):
        m = hashlib.md5()   
        m.update(str)
        return m.hexdigest()         
        
class CommTools():
    @staticmethod
    def radString(length=8,chars=string.ascii_letters+string.digits):
        return ''.join([choice(chars) for i in range(length)])
    
    @staticmethod
    def argsCkeck(args,data):
        if isinstance(args, list) and isinstance(data, dict):
            count = 0
            for arg in args:
                if data.has_key(arg):
                    count = count + 1
            if count == len(args):return True
            else:return False         