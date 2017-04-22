#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
import libvirt,time,os
from datetime import datetime
from xml.dom import minidom
from xml.etree import ElementTree
from VManagePlatform.apps.Base import BaseLogging
from VManagePlatform.const import Const
from VManagePlatform.utils.vConnUtils import CommTools,TokenUntils
from VManagePlatform.utils import vMUtil

class LibvirtErrorMsg():
    CTX = '**[Error]** '

class LibvirtError():
    """Subclass virError to get the last error information."""
    def __init__(self, ctx,err):
        msg = ctx + err[2]
        BaseLogging.Logger(msg, level='error')

libvirt.registerErrorHandler(LibvirtError,LibvirtErrorMsg.CTX)

class VMBase(object):
    def connect(self,uri):
        try:
            self.conn = libvirt.open(uri)
        except libvirt.libvirtError:
            self.conn = False
        return self.conn        
    
    def getVolumeByPath(self,path):
        return self.conn.storageVolLookupByPath(path)
    
    def getIfaces(self):
        interface = []
        for inface in self.conn.listInterfaces():
            interface.append(inface)
        for inface in self.conn.listDefinedInterfaces():
            interface.append(inface)
        return interface
    
    def getStorages(self):
        storages = []
        for pool in self.conn.listStoragePools():
            storages.append(pool)
        for pool in self.conn.listDefinedStoragePools():
            storages.append(pool)
        return storages
    
    def getNetwork(self, net):
        return self.conn.networkLookupByName(net)
    
    def close(self):
        try:
            return self.conn.close()
        except:
            return self.conn.close() 
            return False           

class VMServer(VMBase):
    def __init__(self,conn):
        self.conn = conn

    def defineXML(self, xml):
        '''定义传入的xml'''
        return self.conn.defineXML(xml)  

    def getServerInfo(self):
        '''获取宿主机基本信息'''
        data = self.conn.getInfo()
        return {"cpu_arch":data[0],"mem":data[1],"cpu_total":data[2],"cpu_mhz":data[3]}


    def getVmServerisAlive(self):
        status = self.conn.isAlive()
        if status == 1:return 0
        else:return 1

    def getAliveInstance(self):
        '''获取所有激活的实例'''
        domList = []
        for Id in self.conn.listDomainsID():
            dom = self.conn.lookupByID(Id)
            domList.append(dom.name())
        return domList
            
    
    def createInstance(self,dom_xml):
        '''创建虚拟机'''
        try:
            dom = self.conn.defineXML(dom_xml)
            return dom.create()
        except Exception:
            return False
     
    def getVmStorageInfo(self):
        storage = []
        try:               
            vMdisk = self.conn.listStoragePools()
            for vM in vMdisk:
                data = {}
                pool = self.conn.storagePoolLookupByName(vM)
                pool_xml = pool.XMLDesc(0)
                pool_xml = minidom.parseString(pool_xml)
                try:
                    data['pool_type'] = pool_xml.getElementsByTagName('pool')[0].getAttribute('type')
                except:
                    data['pool_type'] = None
                try:
                    data['pool_path'] = pool_xml.getElementsByTagName('path')[0].childNodes[0].data
                except:
                    data['pool_path'] = None
                data['pool_name'] = pool.name()
                data['pool_size'] = pool.info()[1] / 1024/ 1024/ 1024
                data['pool_available'] = pool.info()[3] / 1024/ 1024/ 1024
                data['pool_per'] = round((float(data['pool_size'] - data['pool_available']) / data['pool_size'])*100,2)
                data['pool_volumes'] = pool.numOfVolumes()
                data['pool_active'] = pool.isActive()
                storage.append(data)
            return storage
        except Exception:                    
            return storage
        
    def getVmIsoList(self):
        isoList = []
        try:               
            vMdisk = self.conn.listStoragePools()
            for vM in vMdisk:
                pool = self.conn.storagePoolLookupByName(vM)
                stgvols = pool.listVolumes()
                for stgvolname in stgvols:
                    volData = dict()
                    stgvol = pool.storageVolLookupByName(stgvolname)
                    info = stgvol.info()
                    try:
                        volXml = stgvol.XMLDesc(0)
                        xml = minidom.parseString(volXml)
                        volData['vol_type'] = xml.getElementsByTagName('target')[0].getElementsByTagName('format')[0].getAttribute('type')
                    except:
                        volData['vol_type'] = 'unkonwn'
                    volData['vol_name'] = stgvol.name()
                    volData['vol_size'] = info[1] / 1024/ 1024/ 1024
                    volData['vol_available'] = info[2] / 1024/ 1024/ 1024
                    volData['vol_path'] = stgvol.path()
                    if volData['vol_type'].endswith('.iso') or volData['vol_path'].endswith('.iso'):isoList.append(volData)
            return isoList
        except Exception:                    
            return isoList
        

    def getVmServerInfo(self):  
        '''获取主机信息'''
        try:
            data = self.conn.getInfo()
        except Exception:
            return False
        try:
            sysXml = minidom.parseString(self.conn.getSysinfo())
            cpu_model = sysXml.getElementsByTagName('processor')[0].getElementsByTagName('entry')[4].childNodes[0].data
        except: 
            cpu_model = None
        try:
            vm_type = self.conn.getType()
        except: 
            vm_type = None    
        try:    
            version = self.conn.getVersion()
        except:  
            version = None 
        try:    
            max_vcpu = self.conn.getMaxVcpus(None)
        except: 
            max_vcpu = None                           
        try:   
            active =  self.conn.numOfDomains()
            inactice = self.conn.numOfDefinedDomains()
            total = active + inactice                
        except:
            total = 0  
        if  self.conn.isAlive() == 1:status = 0
        else:status = 1
        try:
            mem_per =  round((float(self.conn.getMemoryStats(0).get('total') - self.conn.getMemoryStats(0).get('free')) / self.conn.getMemoryStats(0).get('total'))*100,2)
        except:
            mem_per = 0
        vmStatus = self.getVmInstatus()
        return {"cpu_arch":data[0],"mem":data[1],"cpu_total":data[2],"mem_per":mem_per,
                'max_vcpu':max_vcpu,"status":status,"cpu_mhz":data[3],'ins':total,
                'type':vm_type,"version":version,'cpu_model':cpu_model,"vmStatus":vmStatus}                


    def getVmInstatus(self):
        '''获取实例状态'''           
        rList = [] 
        pList = [] 
        sList = [] 
        data = dict()       
        for dom in self.conn.listAllDomains():
            domStatus = dom.state()[0]  
            if  domStatus ==  3:pList.append(dom.name())
            elif  domStatus ==  1:rList.append(dom.name())
            elif   domStatus ==  5:sList.append(dom.name())   
        data['stop'] = sList
        data['running'] = rList
        data['pause'] =  pList
        return data  


    def getVmInstanceBaseInfo(self,server_ip,server_id):
        '''获取所有实例的基本信息'''
        dataList = []
        for ins in self.conn.listAllDomains():
            raw_xml = ins.XMLDesc(0)
            xml = minidom.parseString(raw_xml)       
            try:
                cpu = xml.getElementsByTagName('vcpu')[0].getAttribute('current') 
                if len(cpu) == 0: cpu = xml.getElementsByTagName('vcpu')[0].childNodes[0].data   
            except:
                cpu = 0    
            try:
                mem = ins.info()[2] / 1024
            except:
                mem = 0   
            #获取vnc端口信息
            try:
                vnc_port = xml.getElementsByTagName('graphics')[0].getAttribute("port") 
            except:
                vnc_port = 0 
            ntkList = []
            #获取主机Mac地址
            for nk in xml.getElementsByTagName('interface'):
                if nk.getElementsByTagName('mac') and nk.getElementsByTagName('target'):
                    ntkData = dict()
                    mac = nk.getElementsByTagName('mac')[0].getAttribute('address')
                    name = nk.getElementsByTagName('target')[0].getAttribute("dev")
                    ntkData['name'] = name
                    ntkData['mac'] = mac
                    ntkList.append(ntkData)
            data = dict()
            data["name"] = ins.name()
            data["status"] = ins.state()[0]
            data["cpu"] = cpu
            data["server_ip"] = server_ip
            data["server_id"] = server_id
            data["mem"] = mem
            data["vnc"] = vnc_port
            data['token'] = TokenUntils.makeToken(str=server_ip+data["name"])
            data['netk'] = ntkList
            dataList.append(data)
        return dataList
    
    def getVmInstanceInfo(self,server_ip):  
        '''查询所有实例信息'''
        active =  self.conn.numOfDomains()
        inactice = self.conn.numOfDefinedDomains()
        total = active + inactice
        vms_active = []
        vms_inactive = []
        domain_list = self.conn.listDomainsID() + self.conn.listDefinedDomains() 
        vmPoolList = []
        pools = self.conn.listAllStoragePools(0)
        #获取存储池里面的卷
        for pls in pools:
            for vol in pls.listVolumes():
                data = {}
                data[pls.name()] = pls.storageVolLookupByName(vol).path()
                vmPoolList.append(data)
        for dom in domain_list:
            domData = {}
            if isinstance(dom,int): insName = self.conn.lookupByID(dom).name()
            else:insName = dom
            instance = self.conn.lookupByName(insName)
            status = instance.state()
            domData['status'] = status[0]   
            raw_xml = instance.XMLDesc(0)
            xml = minidom.parseString(raw_xml)
            diskList = []
            #获取实例的磁盘信息
            for disk in xml.getElementsByTagName('disk'):
                #判断设备类型是不是磁盘
                if disk.getAttribute("device") == 'disk':
                    if disk.getElementsByTagName('source'):
                        data = {}
                        try:
                            disk_name = disk.getElementsByTagName('source')[0].getAttribute("file") 
                        except:
                            disk_name = disk.getElementsByTagName('source')[0].getAttribute("dev")
                        #判断卷存在那个存储池里面
                        for vol in vmPoolList:
                            for p,v in vol.iteritems():
                                if disk_name == v:data['disk_pool'] = p
                        data['disk_path'] = disk_name
                        data['disk_sn'] = disk.getElementsByTagName('target')[0].getAttribute("dev")
                        try:
                            data['disk_size'] = instance.blockInfo(disk_name)[0]  / 1024 /1024/1024
                            data['disk_capacity'] = instance.blockInfo(disk_name)[1]   / 1024 /1024/1024
                            data['disk_per'] = round(float(data['disk_capacity'])/data['disk_size']*100,2)
                        except:
                            data['disk_size'] = 0
                            data['disk_capacity'] = 0  
                            data['disk_per'] = 0                   
                        diskList.append(data)
            #获取虚拟机实例的网卡名称
            nkList = []
            for nk in xml.getElementsByTagName('interface'):
                if nk.getElementsByTagName('target'):
                    nk_name = nk.getElementsByTagName('target')[0].getAttribute("dev")                           
                    nkList.append(nk_name)                     
            #获取虚拟机实例内存的容量信息
            try:
                mem = instance.info()[2] / 1024
            except:
                mem = 0   
                
            #mem利用率与ip地址
            try:
                if status[0] == 5:domData['mem_per'] = 0
                else:
                    mem_per =  round(float(instance.memoryStats().get('rss')) / instance.memoryStats().get('actual')*100,2)
                    if mem_per > 100:domData['mem_per'] = 100
                    else:domData['mem_per'] = mem_per
                    
            except Exception,e:     
                domData['mem_per'] = 0
            #获取虚拟机实例CPU信息
            try:
                cpu = xml.getElementsByTagName('vcpu')[0].getAttribute('current') 
                if len(cpu) == 0: cpu = xml.getElementsByTagName('vcpu')[0].childNodes[0].data   
            except:
                cpu = 0    
            
            #获取vnc端口信息
            try:
                vnc_port = xml.getElementsByTagName('graphics')[0].getAttribute("port") 
            except:
                vnc_port = 0    
                                                                      
            domData['name'] = insName
            domData['disks'] = diskList
            domData['netk'] = nkList
            domData['mem'] = mem 
            domData['cpu'] = cpu
            domData['vnc'] = vnc_port
            
            #生成noVNC需要的token
            domData['token'] = TokenUntils.makeToken(str=server_ip+domData['name'])             
        
            if isinstance(dom,int):vms_active.append(domData)
            else:vms_inactive.append(domData)   
        return {"total":total,
                "active":{"total":active,"number":vms_active},
                "inactice":{"total":inactice,"number":vms_inactive}}                 
 

   
                 
class VMStorage(VMBase):
    def __init__(self,conn):
        self.conn =  conn
  
    def defineXML(self, xml):
        '''定义传入的xml'''
        return self.conn.defineXML(xml)  
     
    def getStoragePool(self,pool_name):
        '''查询存储池'''
        try:
            pool = self.conn.storagePoolLookupByName(pool_name) 
            return pool
        except:
            return False
    
    def getPoolXMLDesc(self,pool_name):
        try:
            pool = self.conn.storagePoolLookupByName(pool_name) 
            return pool.XMLDesc(0)
        except Exception,e:  
            return False    
    
    def getVolumeXMLDesc(self,pool,volume_name):
        try: 
            volume = pool.storageVolLookupByName(volume_name)
            return volume.XMLDesc(0)
        except Exception,e: 
            return False 

    
    def getStorageInfo(self,pool_name):
        '''获取单个存储池的信息'''
        data = {}
        try:           
            pool = self.conn.storagePoolLookupByName(pool_name)
            pool_xml = pool.XMLDesc(0)
            pool_xml = minidom.parseString(pool_xml)
            try:
                data['pool_type'] = pool_xml.getElementsByTagName('pool')[0].getAttribute('type')
            except:
                data['pool_type'] = None
            try:
                data['pool_path'] = pool_xml.getElementsByTagName('path')[0].childNodes[0].data
            except:
                data['pool_path'] = None
            data['pool_name'] = pool.name()
            data['pool_size'] = pool.info()[1] / 1024/ 1024/ 1024
            data['pool_available'] = pool.info()[3] / 1024/ 1024/ 1024
            data['pool_per'] = round((float(data['pool_size'] - data['pool_available']) / data['pool_size'])*100,2)
            data['pool_volumes'] = pool.numOfVolumes()
            data['pool_active'] = pool.isActive()
            volList = []
            stgvols = pool.listVolumes()
            for stgvolname in stgvols:
                volData = dict()
                stgvol = pool.storageVolLookupByName(stgvolname)
                info = stgvol.info()
                try:
                    volXml = stgvol.XMLDesc(0)
                    xml = minidom.parseString(volXml)
                    volData['vol_type'] = xml.getElementsByTagName('target')[0].getElementsByTagName('format')[0].getAttribute('type')
                except:
                    volData['vol_type'] = 'unkonwn'
                volData['vol_name'] = stgvol.name()
                volData['vol_size'] = info[1] / 1024/ 1024/ 1024
                volData['vol_available'] = info[2] / 1024/ 1024/ 1024
                volData['vol_path'] = stgvol.path()
                try:
                    volData['vol_per'] = round((float(volData['vol_available']) / volData['vol_size'])*100,2)
                except:
                    volData['vol_per'] = 100
                volList.append(volData)
            data['pool_vols'] = volList
            return data
        except:                   
            return data 
 
    def getStorageVolume(self,pool,volume_name):
        '''查询卷是否存在'''
        try:
            return pool.storageVolLookupByName(volume_name)
        except:  
            return False        
        
    def createStoragePool(self,pool_xml):
        '''创建存储池'''
        try:
            pool = self.conn.storagePoolDefineXML(pool_xml, 0)
            if pool:
                pool.build(0)
                pool.create(0)    
                pool.setAutostart(1)
                pool.refresh()#刷新刚刚添加的存储池，加载存储池里面存在的文件
                return pool
        except:
            return False
    
    def refreshStoragePool(self,pool):
        '''刷新存储池'''
        try:
            pool.refresh()
            return True
        except:
            return False
    
    def createVolumes(self,pool,volume_name,volume_capacity,drive=None):
        if drive is None:drive = 'qcow2'
        volume_xml = """<volume>
                            <name>{volume_name}</name>
                            <allocation>0</allocation>
                            <capacity unit="G">{volume_capacity}</capacity>
                            <target> 
                                <format type="{drive}"/> 
                            </target>                             
                        </volume>
        """        
        volume_xml = volume_xml.format(volume_name=volume_name,volume_capacity=volume_capacity,drive=drive)
        try:
            volume = pool.createXML(volume_xml, 0)
            if volume:return volume
            else:return False
        except:
            return False

        
    def deleteVolume(self,pool,volume_name):
        volume = pool.storageVolLookupByName(volume_name)
#             volume.wipe(0)
        try:
            return volume.delete(0)#volume.delete(0)从存储池里面删除,volume.wipe(0),从磁盘删除
        except Exception,e:
            return str(e)

        
    def autoStart(self,pool):
        '''设置存储池自启动'''
        if pool.autostart() == True:
            return pool.setAutostart(0)
        else:
            return pool.setAutostart(1)
        
    
    def deleteStoragePool(self,pool):
        '''删除存储池'''
        try:
            pool.destroy()
            pool.undefine()
            return True  
        except:
            return False 
    

    
    def getStorageMode(self,pool_name):
        '''获取存储池的类型'''
        return  vMUtil.get_xml_path(self.getPoolXMLDesc(pool_name), "/pool/@type")
    
    def getStorageVolumeXMLDesc(self,pool,name):
        vol = self.getStorageVolume(pool,name)
        return vol.XMLDesc(0)
    
    
    def getStorageVolumeType(self, pool,name):
        '''获取卷的类型'''
        vol_xml = self.getStorageVolumeXMLDesc(name)
        return vMUtil.get_xml_path(vol_xml, "/volume/target/format/@type")
    
    def clone(self, pool,pool_name,name, clone, format=None):
        '''克隆卷'''
        storage_type = self.getStorageMode(pool_name)
        if storage_type == 'dir':
            clone += '.img'
        vol = self.getStorageVolume(pool,name)
        if vol:
            if not format:
                format = self.getStorageVolumeType(name)
            xml = """
                <volume>
                    <name>%s</name>
                    <capacity>0</capacity>
                    <allocation>0</allocation>
                    <target>
                        <format type='%s'/>
                    </target>
                </volume>""" % (clone, format)
            return self.createXMLFrom(xml, vol, 0)
            
    def createXMLFrom(self,pool,xml, vol, flags):
        return pool.createXMLFrom(xml, vol, flags)        
        
class VMInstance(VMBase):
    def __init__(self,conn):
        self.conn = conn         

    def queryInstance(self,id=None,name=None):
        '''查询虚拟机实例是否存在'''
        instance = None
        if isinstance(id, int):
            try:
                instance = self.conn.lookupByID(id)
                return instance
            except:
                return False
        elif isinstance(name, str):
            try:
                instance = self.conn.lookupByName(name)
                return instance
            except:
                return False
            
    def defineXML(self, xml):
        '''定义传入的xml'''
        return self.conn.defineXML(xml)     
            
    def getInsXMLDesc(self,instance,flag):
        return instance.XMLDesc(flag)
    
    def managedSave(self, instance):
        return instance.managedSave(0)

    def managedSaveRemove(self, instance):
        return instance.managedSaveRemove(0)
    
    
    def umountIso(self,instance, dev, image):
        '''卸载Cdrom'''
        '''
        @param dev: 设备序号，比如hda
        @param images: /opt/iso/CentOS-6.3-x86_64-bin-DVD1.iso  
        '''
        cdrom = None
        tree = ElementTree.fromstring(self.getInsXMLDesc(instance,0))
        for disk in tree.findall('devices/disk'):
            if disk.get('device') == 'cdrom':
                for elm in disk:
                    if elm.tag == 'source':
                        if elm.get('file') == image:
                            src_media = elm
                    if elm.tag == 'target':
                        if elm.get('dev') == dev:
                            disk.remove(src_media)
                cdrom = disk
        if len(cdrom) >0:
            if instance.state()[0] == 1:
                xml_disk = ElementTree.tostring(cdrom)
                print xml_disk
                instance.attachDevice(xml_disk)
                xmldom = self.getInsXMLDesc(instance,1)
            if instance.state()[0] == 5:
                xmldom = ElementTree.tostring(tree)
            if self.defineXML(xmldom):return 0
        
        
    
    def mountIso(self,instance,dev, image):
        cdrom = None
        tree = ElementTree.fromstring(self.getInsXMLDesc(instance,0))
        for disk in tree.findall('devices/disk'):
            if disk.get('device') == 'cdrom':
                for elm in disk:
                    if elm.tag == 'target':
                        if elm.get('dev') == dev:
                            src_media = ElementTree.Element('source')
                            src_media.set('file', image)
                            disk.insert(2, src_media)
                cdrom = disk  
        if len(cdrom) >0 :          
            if instance.state()[0] == 1:
                xml = ElementTree.tostring(cdrom)
                instance.attachDevice(xml)
                xmldom = self.getInsXMLDesc(instance,1)
            if instance.state()[0] == 5:
                xmldom = ElementTree.tostring(tree)
            if self.defineXML(xmldom):return 0    
    
     
    def changeSettings(self,instance,description, cur_memory, memory, cur_vcpu, vcpu):
        """
        Function change ram and cpu on vds.
        """
        memory = int(memory) * 1024
        cur_memory = int(cur_memory) * 1024

        xml = instance.XMLDesc(1)
        tree = ElementTree.fromstring(xml)

        set_mem = tree.find('memory')
        set_mem.text = str(memory)
        set_cur_mem = tree.find('currentMemory')
        set_cur_mem.text = str(cur_memory)
        set_desc = tree.find('description')
        set_vcpu = tree.find('vcpu')
        set_vcpu.text = vcpu
        set_vcpu.set('current', cur_vcpu)

        if not set_desc:
            tree_desc = ElementTree.Element('description')
            tree_desc.text = description
            tree.insert(2, tree_desc)
        else:
            set_desc.text = description

        new_xml = ElementTree.tostring(tree)
        return self.defineXML(new_xml)     
       
    
    def getVmInstanceInfo(self,instance,server_ip,vMname):
        '''查询单个实例信息'''
        vmPoolList = []
        pools = self.conn.listAllStoragePools(0)
        #获取存储池里面的卷
        for pls in pools:
            for vol in pls.listVolumes():
                data = {}
                data[pls.name()] = pls.storageVolLookupByName(vol).path()
                vmPoolList.append(data) 
        if instance:
            domData = {}
            status = instance.state()
            domData['status'] = status[0]   
            raw_xml = instance.XMLDesc(0)
            xml = minidom.parseString(raw_xml)
            diskList = []
            #获取实例的磁盘信息
            for disk in xml.getElementsByTagName('disk'):
                #判断设备类型是不是磁盘
                if disk.getAttribute("device") == 'disk':
                    if disk.getElementsByTagName('source'):
                        data = {}
                        try:
                            disk_name = disk.getElementsByTagName('source')[0].getAttribute("file") 
                        except:
                            disk_name = disk.getElementsByTagName('source')[0].getAttribute("dev")
                        #判断卷存在那个存储池里面
                        for vol in vmPoolList:
                            for p,v in vol.iteritems():
                                if disk_name == v:data['disk_pool'] = p
                        data['disk_path'] = disk_name
                        data['disk_sn'] = disk.getElementsByTagName('target')[0].getAttribute("dev")
                        try:
                            data['disk_size'] = instance.blockInfo(disk_name)[0]  / 1024 /1024/1024
                            data['disk_capacity'] = instance.blockInfo(disk_name)[1]   / 1024 /1024/1024
                            data['disk_per'] = round(float(data['disk_capacity'])/data['disk_size']*100,2)
                        except:
                            data['disk_size'] = 0
                            data['disk_capacity'] = 0  
                            data['disk_per'] = 0                   
                        diskList.append(data)
            #获取虚拟机实例的网卡名称
            nkList = []
            for nk in xml.getElementsByTagName('interface'):
                if nk.getElementsByTagName('target'):
                    nk_name = nk.getElementsByTagName('target')[0].getAttribute("dev")                           
                    nkList.append(nk_name)                     
            #获取虚拟机实例内存的容量信息
            try:
                mem = instance.info()[2] / 1024
            except:
                mem = 0   
            #mem利用率与ip地址
            try:
                if status[0] == 5:domData['mem_per'] = 0
                else:
                    mem_per =  round(float(instance.memoryStats().get('rss')) / instance.memoryStats().get('actual')*100,2)
                    if mem_per > 100:domData['mem_per'] = 100
                    else:domData['mem_per'] = mem_per
                    
            except Exception,e:     
                domData['mem_per'] = 0
            #获取虚拟机实例CPU信息
            try:
                cpu = xml.getElementsByTagName('vcpu')[0].getAttribute('current') 
                if len(cpu) == 0: cpu = xml.getElementsByTagName('vcpu')[0].childNodes[0].data   
            except:
                cpu = 0    
            #获取vnc端口信息
            try:
                vnc_port = xml.getElementsByTagName('graphics')[0].getAttribute("port") 
            except:
                vnc_port = 0    
                                                                      
            domData['disks'] = diskList
            domData['netk'] = nkList
            domData['mem'] = mem 
            domData['cpu'] = cpu
            domData['vnc'] = vnc_port
            domData['name'] = vMname
            #生成noVNC需要的token
            domData['token'] = TokenUntils.makeToken(str=server_ip+vMname) 
            return domData

    def getMediaDevice(self,instance):
        '''获取cdrom'''
        def disks(ctx):
            result = []
            dev = None
            volume = None
            storage = None
            src_path = None
            for media in ctx.xpathEval('/domain/devices/disk'):
                device = media.xpathEval('@device')[0].content
                if device == 'cdrom':
                    try:
                        dev = media.xpathEval('target/@dev')[0].content
                        try:
                            src_path = media.xpathEval('source/@file')[0].content
                            vol = self.getVolumeByPath(src_path)
                            volume = vol.name()
                            stg = vol.storagePoolLookupByVolume()
                            storage = stg.name()
                        except:
                            src_path = media.xpathEval('source/@file')[0].content
                            volume = media.xpathEval('source/@file')[0].content.split('/')[-1]
                    except:
                        pass
                    finally:
                        result.append({'dev': dev, 'image': volume, 'storage': storage, 'path': src_path})
            return result
        return vMUtil.get_xml_path(self.getInsXMLDesc(instance,0), func=disks)
    
    
    def delDisk(self,instance):
        '''删除虚拟机时删除磁盘'''
        disks = self.getDiskDevice(instance)
        for disk in disks:
            try:
                vol = self.getVolumeByPath(disk.get('path'))
                vol.delete(0)
            except:
                pass
    
    def getDiskDevice(self,instance):
        '''获取实例的磁盘设备'''
        def disks(ctx):
            result = []
            dev = None
            volume = None
            storage = None
            src_path = None
            for disk in ctx.xpathEval('/domain/devices/disk'):
                device = disk.xpathEval('@device')[0].content
                if device == 'disk':
                    try:
                        dev = disk.xpathEval('target/@dev')[0].content
                        src_path = disk.xpathEval('source/@file|source/@dev|source/@name')[0].content
                        try:
                            vol = self.getVolumeByPath(src_path)
                            volume = vol.name()
                            stg = vol.storagePoolLookupByVolume()
                            storage = stg.name()
                        except:
                            volume = src_path
                    except:
                        pass
                    finally:
                        result.append({'dev': dev, 'image': volume, 'storage': storage, 'path': src_path})
            return result
        return vMUtil.get_xml_path(self.getInsXMLDesc(instance,0), func=disks)
    
    
    def clone(self, instance,clone_data):
        '''克隆实例'''
        clone_dev_path = []
        xml = self.getInsXMLDesc(instance, flag=1)
        tree = ElementTree.fromstring(xml)
        name = tree.find('name')
        name.text = clone_data['name']
        uuid = tree.find('uuid')
        tree.remove(uuid)
        for num, net in enumerate(tree.findall('devices/interface')):
            elm = net.find('mac')
            inter = net.find('target')
            brName = net.find('source').get('bridge')
            inter.set('dev',brName + '-' + CommTools.radString(4))
            elm.set('address', vMUtil.randomMAC())
        
        for disk in tree.findall('devices/disk'):
            if disk.get('device') == 'disk':
                elm = disk.find('target')
                device_name = elm.get('dev')
                if device_name:
                    target_file = clone_data['disk']
                    try:
                        meta_prealloc = clone_data['meta']
                    except:
                        meta_prealloc = False
                    elm.set('dev', device_name)
                elm = disk.find('source')
                source_file = elm.get('file')
                if source_file:
                    clone_dev_path.append(source_file)
                    clone_path = os.path.join(os.path.dirname(source_file),
                                              target_file)
                    elm.set('file', clone_path)
                    vol = self.getVolumeByPath(source_file)
                    vol_format = vMUtil.get_xml_path(vol.XMLDesc(0),"/volume/target/format/@type")
                    if vol_format == 'qcow2' and meta_prealloc:
                        meta_prealloc = True
                    vol_clone_xml = """
                                    <volume>
                                        <name>%s</name>
                                        <capacity>0</capacity>
                                        <allocation>0</allocation>
                                        <target>
                                            <format type='%s'/>
                                        </target>
                                    </volume>""" % (target_file, vol_format)
                    stg = vol.storagePoolLookupByVolume()
                    stg.createXMLFrom(vol_clone_xml, vol, meta_prealloc)
        if self.defineXML(ElementTree.tostring(tree)):return 0
    
    def getCpuUsage(self,instance):       
        if instance.state()[0] == 1:
            nbcore = self.conn.getInfo()[2]
            cpu_use_ago = instance.info()[4]
            time.sleep(1)
            cpu_use_now = instance.info()[4]
            diff_usage = cpu_use_now - cpu_use_ago
            cpu_per = 100 * diff_usage / (1 * nbcore * 10 ** 9L)
        else:
            cpu_per = 0
        return cpu_per
    
    def addInstanceDisk(self,instance,volPath):
        diskSn = 'vda'
        diskList = ['vd'+chr(i) for i in range(97,123)]
        domXml = instance.XMLDesc(0)
        tree = ElementTree.fromstring(domXml)
        for ds in tree.findall('devices/disk'):
            device = ds.get('device')
            vdisk = ds.find('target').get('dev')
            if device == 'disk' and vdisk in diskList:diskSn = diskList[diskList.index(vdisk) + 1]
        diskXml = Const.CreateDisk(volume_path=volPath, diskSn=diskSn)
        try:
            result = instance.attachDeviceFlags(diskXml,3)#如果是关闭状态则标记flags为3，保证添加的硬盘重启不会丢失 
        except:
            return False
        if result == 0:return True
        else:return False
    
    
    def addInstanceInterface(self,instance,brName):
        netk = self.getNetwork(brName)
        if netk:
            xml = netk.XMLDesc(0)
            tree = ElementTree.fromstring(xml)
            try:
                mode = tree.find('virtualport').get('type')  
            except:
                mode = 'brct'         
            interXml = Const.CreateNetcard(nkt_br=brName, ntk_name=brName +'-'+CommTools.radString(length=4), mode=mode)
            try:
                return instance.attachDeviceFlags(interXml,3)#如果是关闭状态则标记flags为3，保证添加的硬盘重启不会丢失 
            except Exception,e:
                return e
        else:return False 

        
    def delInstanceInterface(self,instance,interName): 
        '''删除网络设备''' 
        interXml = None
        raw_xml = instance.XMLDesc(0)
        domXml = minidom.parseString(raw_xml)
        for ds in domXml.getElementsByTagName('interface'):
            try:
                dev = ds.getElementsByTagName('target')[0].getAttribute('dev')
            except:
                continue
            if dev == interName:interXml = ds.toxml()  
        if  interXml:
            try:
                return instance.detachDeviceFlags(interXml,3)
            except Exception,e:
                return e
        else:return False  
        
    def delInstanceDisk(self,instance,volPath):
        '''删除硬盘'''
        diskXml = None
        raw_xml = instance.XMLDesc(0)
        domXml = minidom.parseString(raw_xml)
        for ds in domXml.getElementsByTagName('disk'):
            try:
                path = ds.getElementsByTagName('source')[0].getAttribute('file')
            except:
                continue
            if path == volPath:diskXml = ds.toxml()  
        if diskXml:
            try:
                return instance.detachDeviceFlags(diskXml,3)
            except Exception,e:
                return e
        else:return False
    
    def getInterFace(self,instance,inter_name):
        '''获取网卡类型'''
        def interface(ctx):
            result = dict()
            for media in ctx.xpathEval('/domain/devices/interface'):
                interface = media.xpathEval('target/@dev')[0].content
                if interface == inter_name:
                    try:
                        mode = media.xpathEval('virtualport/@type')[0].content
                    except:
                        mode = 'brct'
                    result['name'] =  interface
                    result['type'] = mode  
            return result
        return vMUtil.get_xml_path(instance.XMLDesc(0) , func=interface)        
            
    def setInterfaceBandwidth(self,instance,port,bandwidth):
        '''限制流量'''
        domXml = instance.XMLDesc(0)
        root = ElementTree.fromstring(domXml)
        try:
            for dev in root.findall('.//devices/'):
                if dev.tag == 'interface':
                    for iter in dev:
                        if iter.tag == 'target' and iter.get('dev') == port:
                            bwXml = ElementTree.SubElement(dev,'bandwidth')   
                            inbdXml = ElementTree.Element('inbound')
                            inbdXml.set('average',str(int(bandwidth)*1024))
                            inbdXml.set('peak',str(int(bandwidth)*1024))
                            inbdXml.set('burst','1024')
                            outbdXml = ElementTree.Element('outbound')
                            outbdXml.set('average',str(int(bandwidth)*1024))
                            outbdXml.set('peak',str(int(bandwidth)*1024))
                            outbdXml.set('burst','1024')
                            bwXml.append(inbdXml)
                            bwXml.append(outbdXml)
            domXml = ElementTree.tostring(root)
        except Exception,e:
            return {"status":"faild",'data':e}
        if self.defineXML(domXml):return {"status":"success",'data':None} 
    
    def cleanInterfaceBandwidth(self,instance,port):
        '''清除流量限制'''
        domXml = instance.XMLDesc(0)
        root = ElementTree.fromstring(domXml)
        try:
            for dev in root.findall('.//devices/'):
                if dev.tag == 'interface':
                    for iter in dev:
                        if iter.get('dev') == port:
                            for iter in dev:
                                if iter.tag == 'bandwidth':dev.remove(iter) 
            domXml = ElementTree.tostring(root)
        except Exception,e:
            return {"status":"faild",'data':e}
        if self.defineXML(domXml):return {"status":"success",'data':None}     
        
    def getInstanceIsActive(self,instance):
        if instance.isActive():status = 0  
        else:status = 1      
        return status      
    
    def setVcpu(self,instance,cpu):
        '''调整CPU个数'''
        if isinstance(cpu, int):
            try:
                return instance.setVcpusFlags(cpu,0)
            except:
                return False
        else:
            return False        
    
    def setMem(self,instance,mem):
        '''调整内存大小'''
#         if instance.state()[0] == 5:flags = 2
#         else:flags = 0
        if isinstance(mem, int):
            mem = mem*1024
            try:
                return instance.setMemoryFlags(mem,flags=0)
            except:
                return False
        else:
            return False
    
    def migrate(self,instance,uri,dname,tcp_path):
        '''虚拟机迁移'''
        return instance.migrate(uri,True,dname,tcp_path,0) 
    
    def snapShotCteate(self,instance,snapName):
        '''为实例的所有磁盘创建实例'''
        snpXML = '''<domainsnapshot>
                        <name>{snapName}</name> 
                        <description>Snapshot of {snapName}</description>
                        <disks>
                        </disks>
                    </domainsnapshot>
        '''
        snpXML = snpXML.format(snapName=snapName)
        return instance.snapshotCreateXML(snpXML,0)
    
    def snapShotDelete(self,instance,snapName):
        '''删除实例快照'''
        snap = instance.snapshotLookupByName(snapName)   
        return snap.delete()
    
    def snapShotView(self,instance,snapName):
        '''查看实例快照'''
        try:
            snap = instance.snapshotLookupByName(snapName) 
        except:
            return False  
        return snap.getXMLDesc()    
    
    def snapShotList(self,instance):
        '''列出实例快照'''
        snapList = []
        try:
            for snap in instance.snapshotListNames():
                data = dict()
                data['name'] = snap
                snap = instance.snapshotLookupByName(snap)
                snapCtime = vMUtil.get_xml_path(snap.getXMLDesc(0), "/domainsnapshot/creationTime")
                data['last'] = snap.isCurrent()
                data['ctime'] = datetime.fromtimestamp(int(snapCtime))
                snapList.append(data)
        except:
            return snapList
        return snapList
    
    def revertSnapShot(self,instance,snapName):
        '''快照恢复'''
        snap = instance.snapshotLookupByName(snapName)
        return instance.revertToSnapshot(snap,0)
    
    def delete(self,instance):
        '''删除实例'''
        try:
            if instance.state()[0] == 5:
                return instance.undefineFlags()
            else:
                instance.undefineFlags()
                return instance.destroy() #执行成返回值为0
        except Exception,e:
            return e           
     
    def suspend(self,instance):  
        '''暂停实例'''
        try:
            return instance.suspend()
        except Exception,e:
            return e           
        
    def resume(self,instance):
        '''恢复实例'''
        try:
            return instance.resume()
        except Exception,e:
            return e         
        
    def reboot(self,instance):
        '''恢复实例'''
        try:
            return instance.reboot()
        except Exception,e:
            return e         
    
    def shutdown(self,instance):
        '''关闭实例'''
        try:
            return instance.shutdown()
        except Exception,e:
            return e         

    def destroy(self,instance):
        '''强制关闭实例'''
        try:
            return instance.destroy()
        except Exception,e:
            return e
    
    def state(self,instance):
        '''检查实例的状态'''
        try:
            return instance.state()
        except Exception,e:
            return e
            
    def start(self,instance):
        '''启动实例'''
        try:
            return instance.create()
        except Exception,e:
            return e     
        

class VMNetwork(VMBase):
    def __init__(self,conn):
        self.conn =  conn
     
    def defineXML(self, xml):
        '''定义传入的xml'''
        return self.conn.defineXML(xml)       
     
    def getNetwork(self,netk_name):
        '''查询网络是否存在'''
        try:
            netk = self.conn.networkLookupByName(netk_name)
            return netk
        except:
            return False 
        
    def getNetworkType(self,netk_name):
        '''获取网络类型'''
        netk = self.getNetwork(netk_name)
        if netk:
            xml = netk.XMLDesc(0)
            tree = ElementTree.fromstring(xml)
            try:
                mode = tree.find('virtualport').get('type') 
            except:
                mode = 'brct'
            return mode
        else:return False
        
    def getInterface(self, name):
        '''获取网络接口'''
        try:
            return self.conn.interfaceLookupByName(name)
        except:
            return False

    def getInterfaceInfo(self, name):
        iface = self.getInterface(name)
        xml = iface.XMLDesc(0)
        mac = iface.MACString()
        itype = vMUtil.get_xml_path(xml, "/interface/@type")
        ipType = vMUtil.get_xml_path(xml, "/interface/protocol/@family")
        if ipType == 'ipv4':
            ipv4 = vMUtil.get_xml_path(xml, "/interface/protocol/ip/@address")
            mask = vMUtil.get_xml_path(xml, "/interface/protocol/ip/@prefix")
        else:
            ipv4 = None
            mask = None
        state = iface.isActive()
        return {'name': name, 'type': itype, 'state': state, 'mac': mac,'ipv4':ipv4,'mask':mask}
    
    def defineInterface(self, xml, flag=0):
        '''定义网络接口'''
        self.conn.interfaceDefineXML(xml, flag)

    def createBridgeInterface(self, netdev,brName,ipv4_addr,mask,stp,mac,delay=0.01):
        '''创建网桥类型接口'''
        print netdev,brName,ipv4_addr,mask,stp
        xml = """<interface type='bridge' name='{brName}'>
                    <start mode='onboot'/>""".format( brName=brName)
        if ipv4_addr and mask:
            xml += """ <protocol family='ipv4'>
                            <ip address='{ipv4_addr}' prefix='{mask}'/>
                        </protocol>""".format(ipv4_addr=ipv4_addr,mask=mask)
        xml += """<bridge stp='{stp}' delay='{delay}'>
                        <interface name='{netdev}' type='ethernet'/>
                        <mac address='{mac}'/>
                      </bridge>""".format(stp=stp, delay=delay,mac=mac ,netdev=netdev)
        xml += """</interface>"""
        self.defineInterface(xml)
        iface = self.getInterface(brName)
        iface.create()    

    def stopInterface(self,iface):
        try:
            iface.destroy()
            return True
        except:
            return False

    def startInterface(self,iface):
        try:
            iface.create()
            return True
        except:
            return False

    def deleteInterface(self,iface):
        try:
            iface.undefine()
            return True
        except:
            return False
        
    def createNetwork(self,xml):
        '''创建网络并且设置自启动'''
        try:
            netk = self.conn.networkDefineXML(xml)
            if netk.create() == 0:return netk.setAutostart(1)
            else:return False
        except:
            return False        
        
    def deleteNetwork(self,netk):
        '''删除网络'''
        try:
            netk.destroy()
            return netk.undefine()
        except:
            return False  
        
        
    def listNetwork(self):
        '''列出所有网络'''
        dataList = []
        try:
            for netk in self.conn.listAllNetworks():
                data = dict()
                data['name'] = netk.name()
                data['alive'] = netk.isActive()
                data['pers'] = netk.isPersistent()
                dataList.append(data) 
        except:
            pass
        return dataList    
    
    def listInterface(self):
        '''列出所有接口'''
        dataList = []
        try:
            for ins in self.conn.listAllInterfaces():
                data = dict()
                data['name'] = ins.name()
                data['alive'] = ins.isActive()
                dataList.append(data) 
        except:
            pass
        return dataList                 

class LibvirtManage(object):
    def __init__(self,uri):
        self.vMconn = VMBase()
        self.conn = self.vMconn.connect(uri)
        
    def genre(self,model):
        if self.conn:
            if model == 'storage':
                return VMStorage(conn=self.conn)
            elif model == 'instance':
                return VMInstance(conn=self.conn)
            elif model == 'server':
                return VMServer(conn=self.conn)
            elif model == 'network':
                return VMNetwork(conn=self.conn)            
            else:
                return False
        else:
            return False
        
    def close(self):
        return self.vMconn.close()
        
        
if __name__ == '__main__':
    LIB = LibvirtManage(uri='qemu+tcp://192.168.1.233/system')
    server = LIB.genre(model='server')
    print server.getVmServerisAlive()
    print LIB.close()
