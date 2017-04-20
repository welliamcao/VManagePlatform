#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
import paramiko


class SSHBase(object):
    def __init__(self,hostname,port=None):
        self.hostname = hostname
        self.port = port

    def ssh(self):
        try:
            self.ssh = paramiko.SSHClient()
            self.ssh.load_system_host_keys() ####获取ssh key密匙，默认在~/.ssh/knows_hosts
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(hostname = self.hostname,port=self.port) 
        except Exception,e:
            self.ssh = False 
        return self.ssh       
    
    def close(self):
        self.ssh.close()

class OvsConfig(SSHBase):
    def __init__(self,ssh):
        self.ssh = ssh      
    
    def ovsAddBr(self,brName):
        '''ovs添加网桥命令'''
        try:
            data = dict()
            cmd = 'ovs-vsctl add-br {brName}'.format(brName=brName) 
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:  
            data["msg"] = str(e)
            return  data

    def ovsDelBr(self,brName):
        '''ovs删除网桥命令'''
        try:
            data = dict()
            cmd = 'ovs-vsctl --if-exists del-br {brName}'.format(brName=brName)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data

    def ovsConfStp(self,brName):
        '''ovs网桥配置STP'''
        try:
            data = dict()
            cmd = 'set bridge {brName} stp_enable=true'.format(brName=brName)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:             
            data["msg"] = str(e)
            return  data

    def ovsAddInterface(self,brName,interface):
        '''ovs网桥添加端口'''
        try:
            data = dict()
            cmd = 'ovs-vsctl add-port {brName} {interface}'.format(brName=brName,interface=interface)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd) 
            print    stdin,stdout,stderr        
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:             
            data["msg"] = str(e)
            return  data
 
    def ovsDelInterface(self,brName,interface):
        '''ovs网桥删除端口'''
        try:
            data = dict()
            cmd = 'ovs-vsctl del-port {brName} {interface}'.format(brName=brName,interface=interface)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)             
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:             
            data["msg"] = str(e)
            return  data 
    
    def ovsConfPath(self,brName,sport,tport):        
        '''ovs配置patch'''
        try:
            data = dict()
            cmd = 'ovs-vsctl add-port {brName} {sport} -- set Interface {sport} type=patch options:peer={tport}'.format(brName=brName,sport=sport,tport=tport)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)             
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:             
            data["msg"] = str(e)
            return  data  
        
    def ovsConfBandwidth(self,port,bandwidth):  
        '''限制带宽''' 
        try:
            rate_cmd = 'ovs-vsctl set interface {port} ingress_policing_rate=$(({bandwidth}*1000))'.format(port=port,bandwidth=bandwidth)
            burst_cmd = 'ovs-vsctl set interface {port} ingress_policing_burst=$(({bandwidth}*100))'.format(port=port,bandwidth=bandwidth) 
            qos_cmd =  'ovs-vsctl set port {port} qos=@newqos -- --id=@newqos create qos type=linux-htb queues=0=@q0 other-config:max-rate=$(({bandwidth}*1000000)) -- --id=@q0 create queue other-config:min-rate=$(({bandwidth}*1000000)) other-config:max-rate=$(({bandwidth}*1000000))'.format(port=port,bandwidth=bandwidth)
            for cmd in rate_cmd,burst_cmd,qos_cmd:
                data = dict()
                stdin,stdout,stderr = self.ssh.exec_command(cmd)                 
                data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
                exit_status = stdout.channel.recv_exit_status() 
                if exit_status > 0:
                    data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                    data["status"] = 'faild'
                    return data
                else:
                    data["status"] = 'success'
            return  data                   
        except Exception,e:             
            data["msg"] = str(e)
            return  data  
        
    def ovsCleanBandwidth(self,port): 
        '''清除带宽'''   
        try:
            rate_cmd = 'ovs-vsctl set interface {port} ingress_policing_rate=0'.format(port=port)
            burst_cmd = 'ovs-vsctl set interface {port} ingress_policing_burst=0'.format(port=port) 
            qos_cmd =  'ovs-vsctl  clear Port {port} qos'.format(port=port)
            for cmd in rate_cmd,burst_cmd,qos_cmd:
                data = dict()
                stdin,stdout,stderr = self.ssh.exec_command(cmd)                
                data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
                exit_status = stdout.channel.recv_exit_status() 
                if exit_status > 0:
                    data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                    data["status"] = 'faild'
                    return data
                else:
                    data["status"] = 'success'
            return  data                   
        except Exception,e:            
            data["msg"] = str(e)
            return  data         

class BrctlConfig(SSHBase):
    def __init__(self,ssh):
        self.ssh = ssh 
        
    def brctlAddBr(self,iface,brName,stp=None):
        '''添加网桥'''
        try:
            data = dict()
            if stp:cmd = 'virsh iface-bridge {iface} {brName}'.format(iface=iface,brName=brName)
            else:cmd = 'virsh iface-bridge {iface} {brName} --no-stp'.format(iface=iface,brName=brName)  
            stdin,stdout,stderr = self.ssh.exec_command(cmd)              
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:data["status"] = 'faild'
            else:data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data          
        
    def brctlDelBr(self,brName):
        '''删除网桥'''
        try:
            data = dict()
            cmd = 'brctl delbr {brName}'.format(brName=brName)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)             
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            clean = "sed -i '/{brName}/d' /etc/rc.d/rc.local".format(brName=brName) 
            stdin,stdout,stderr = self.ssh.exec_command(clean)
            return  data                   
        except Exception,e: 
            data["msg"] = str(e)
            return  data         
    
    def brctlUpBr(self,brName):
        '''启动网桥'''
        try:
            data = dict()
            cmd = 'ifconfig {brName} up'.format(brName=brName)  
            stdin,stdout,stderr = self.ssh.exec_command(cmd)              
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data 
        
    def brctlDownBr(self,brName):
        '''关闭网桥'''
        try:
            data = dict()
            cmd = 'virsh iface-unbridge {brName}'.format(brName=brName)  
            stdin,stdout,stderr = self.ssh.exec_command(cmd)              
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:data["status"] = 'faild'
            else:data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data
    
    def brctlAddIf(self,brName,interface):
        '''添加端口'''
        try:
            data = dict()
            cmd = 'brctl addif {brName} {interface} '.format(brName=brName,interface=interface)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                clean = "sed -i '/{cmd}/d' /etc/rc.d/rc.local".format(cmd=cmd) 
                stdin,stdout,stderr = self.ssh.exec_command(clean)
                save = "echo  '{cmd}' >>  /etc/rc.d/rc.local".format(cmd=cmd)
                stdin,stdout,stderr = self.ssh.exec_command(save)
                data["status"] = 'success'
            return  data                   
        except Exception,e:      
            data["msg"] = str(e)
            return  data      

    def brctlDelIf(self,brName,interface):
        '''删除端口'''
        try:
            data = dict()
            cmd = 'brctl delif {brName} {interface}'.format(brName=brName,interface=interface)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data  
 
    def brctlBrStp(self,brName,mode):
        '''网桥STP'''
        try:
            data = dict()
            cmd = 'brctl stp {brName} {mode}'.format(brName=brName,mode=mode)   
            stdin,stdout,stderr = self.ssh.exec_command(cmd)
            data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
            exit_status = stdout.channel.recv_exit_status() 
            if exit_status > 0:
                data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
                data["status"] = 'faild'
            else:
                save = "echo  '{cmd}' >>  /etc/rc.d/rc.local".format(cmd=cmd)
                stdin,stdout,stderr = self.ssh.exec_command(save)
                data["status"] = 'success'
            return  data                   
        except Exception,e:
            data["msg"] = str(e)
            return  data 
     
#     def brctlSave(self,brName,interface):
#         '''保存配置设置开启启动'''
#         try:
#             brCmd = 'brctl addbr {brName}'.format(brName=brName)
#             brIfcmd = 'brctl addif {brName} {interface} '.format(brName=brName,interface=interface)
#             for cmd in brCmd,brIfcmd:
#                 data = dict()
#                 clean = "sed -i '/{str}/d' /etc/rc.d/rc.local".format(str=cmd)
#                 stdin,stdout,stderr = self.ssh.exec_command(clean)     
#                 save = "echo  '{str}' >>  /etc/rc.d/rc.local".format(str=cmd)
#                 stdin,stdout,stderr = self.ssh.exec_command(save)
#             data["stdout"] = ''.join(stdout.readlines()).replace("\n","<br>")
#             exit_status = stdout.channel.recv_exit_status() 
#             if exit_status > 0:
#                 data["stderr"] =  "%s" % (''.join(stderr.readlines())).replace("\n","<br>")
#                 data["status"] = 'faild'
#             else:
#                 data["status"] = 'success'
#             return  data                   
#         except Exception,e:      
#             data["msg"] = str(e)
#             return  data   
            
class BRManage(object):
    def __init__(self,hostname,port=None):
        sshTools = SSHBase(hostname,port=port)
        self.ssh = sshTools.ssh()
    def genre(self,model):
        if self.ssh:
            if model == 'ovs':
                return OvsConfig(ssh=self.ssh)  
            elif model == 'brctl':
                return BrctlConfig(ssh=self.ssh)                  
            else:
                return False
        else:
            return False
        
    def close(self):
        return self.ssh.close()