#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
import commands

class DHCPConfig(object):
    
    def addOvsPort(self,brName,port):
        cmd = 'ovs-vsctl add-port {brName} {port} -- set Interface {port} type=internal'.format(brName=brName,port=port)
        status,output = commands.getstatusoutput(cmd)
        return status,output
    
    def delOvsPort(self,brName,port):
        cmd = 'ovs-vsctl del-port {brName} {port}'.format(brName=brName,port=port)
        status,output = commands.getstatusoutput(cmd)
        return status,output        
        
    def addBrctlPort(self,brName,port):
        cmd = 'brctl addif {brName} {port}'.format(brName=brName,port=port)
        status,output = commands.getstatusoutput(cmd)
        return status,output     
    
    def delBrctlPort(self,brName,port):
        cmd = 'brctl delif {brName} {port}'.format(brName=brName,port=port)
        status,output = commands.getstatusoutput(cmd)
        return status,output        
        
    def addNetns(self,netnsName):
        '''
        @param netnsName: dhcp-int|dhcp-ext
        '''        
        cmd = 'ip netns add {netnsName}'.format(netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output
    
    def delNetns(self,netnsName):
        '''
        @param netnsName: dhcp-int|dhcp-ext
        '''        
        cmd = 'ip netns delete {netnsName}'.format(netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output    
    
    def netnsIsAlive(self,netnsName):
        cmd = 'test -f /var/run/netns/{netnsName}'.format(netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output 
    
    def linkPort(self,netnsName,port):
        '''
        @param port: tap-qdhcp-int|tap-qdhcp-ext 
        '''
        cmd = 'ip link set {port} netns {netnsName}'.format(port=port,netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output     
    
    def setDHCPIpaddr(self,netnsName,port,ip):
        '''
        @param ip: 172.16.0.1/24
        '''         
        cmd = 'ip netns exec {netnsName} ip addr add {ip} dev {port}'.format(netnsName=netnsName,ip=ip,port=port)
        status,output = commands.getstatusoutput(cmd)
        return status,output 

    def setNetnsPortUp(self,netnsName,port):
        cmd = 'ip netns exec {netnsName} ip link set {port} up'.format(port=port,netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output    

    def setNetnsPortDown(self,netnsName,port):
        cmd = 'ip netns exec {netnsName} ip link set {port} down'.format(port=port,netnsName=netnsName)
        status,output = commands.getstatusoutput(cmd)
        return status,output    

    def enableNets(self,netnsName,brName, port,ip,drive):
        '''
        @param mode: ovs|brctl
        '''         
        if drive == 'ovs':
            self.addOvsPort(brName, port)
        elif drive == 'brctl':
            self.addBrctlPort(brName, port)
        result = self.addNetns(netnsName)
        if result[0] == 0:
            result = self.linkPort(netnsName, port)    
        if result[0] == 0:
            result = self.setDHCPIpaddr(netnsName, port, ip)
        if result[0] == 0:
            result = self.setNetnsPortUp(netnsName, port)    
        if result[0] == 0:
            result = self.setNetnsPortUp(netnsName, port='lo')  
        return result
    
    def disableNets(self,netnsName,brName, port,drive):
        '''
        @param mode: ovs|brctl
        '''               
        if drive == 'ovs':
            result = self.delOvsPort(brName, port)
        elif drive == 'brctl':
            result = self.delBrctlPort(brName, port)
        if result[0] == 0:    
            result = self.delNetns(netnsName)
        return result    
   
    
    def delete(self,netnsName,brName,port,drive,mode):
        result = self.delNetns(netnsName)
        if result[0] == 0:
            if drive == 'ovs':
                result = self.delOvsPort(brName, port) 
            elif drive == 'brctl':
                result = self.delBrctlPort(brName, port)(brName, port)        
            result = self.status(mode)
            if result[1] > 0:
                self.stop(mode)
        return result
            
            
    def start(self,netnsName,iprange,port,mode,gateway=None,dns=None): 
        '''
        @param iprange: 172.16.0.100,172.16.0.254
        @param mode: int|ext
        '''            
        if mode == 'int':  
            cmd = '''ip netns exec {netnsName} /usr/sbin/dnsmasq -u root -g root --no-hosts --no-resolv --strict-order --bind-interfaces --except-interface lo --interface {port} --dhcp-range={iprange},static,infinite --dhcp-leasefile=/var/run/dnsmasq/{port}.lease --pid-file=/var/run/dnsmasq-{mode}.pid --dhcp-lease-max=253 --dhcp-no-override --log-queries  --log-facility=/var/run/dnsmasq/dnsmasq-{mode}.log --dhcp-option-force=3,6  --conf-file='''.format(iprange=iprange,port=port,netnsName=netnsName,mode=mode)
        elif mode == 'ext':
            cmd = '''ip netns exec {netnsName} /usr/sbin/dnsmasq -u root -g root --no-hosts --no-resolv --strict-order --bind-interfaces --except-interface lo --interface {port} --dhcp-range={iprange},static,infinite --dhcp-leasefile=/var/run/dnsmasq/{port}.lease --pid-file=/var/run/dnsmasq-{mode}.pid --dhcp-lease-max=253 --dhcp-no-override --log-queries  --log-facility=/var/run/dnsmasq/dnsmasq-{mode}.log --dhcp-option=3,{gateway} --dhcp-option=6,{dns} --conf-file= '''.format(iprange=iprange,port=port,netnsName=netnsName,mode=mode,gateway=gateway,dns=dns)
        status,output = commands.getstatusoutput(cmd)            
        return status,output  
    
    def stop(self,mode):
        cmd = 'kill -9 `cat /var/run/dnsmasq-{mode}.pid`'.format(mode=mode) 
        status,output = commands.getstatusoutput(cmd)
        return status,output   
    
    def status(self,mode):
        pidCmd = 'cat /var/run/dnsmasq-{mode}.pid'.format(mode=mode) 
        status,output = commands.getstatusoutput(pidCmd)
        if status == 0:
            cmd = 'test -d /proc/{output}/'.format(output=output) 
            status,output = commands.getstatusoutput(cmd)
        return status,output                 