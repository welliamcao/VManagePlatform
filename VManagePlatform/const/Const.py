#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
def StorageTypeXMLConfig(pool_type,pool_name,pool_spath=None,pool_tpath=None,pool_host=None):
    storage_pool_xml = {
                    'dir':'''
                        <pool type='dir'>
                          <name>{pool_name}</name>
                          <target>
                            <path>{pool_tpath}</path>
                            <permissions>
                              <mode>0755</mode>
                              <owner>-1</owner>
                              <group>-1</group>
                            </permissions>
                          </target>
                        </pool>                            
                        ''',
                    'disk':'''
                            <pool type="disk">
                              <name>{pool_name}</name>
                              <source>
                                <device path='{pool_spath}'/>
                              </source>
                              <target>
                                <path>{pool_tpath}</path>
                              </target>
                            </pool>                        
                        ''',
                    'logical':'''
                            <pool type="logical">
                              <name>{pool_name}</name>
                              <source>
                                <device path="{pool_spath}"/>
                              </source>
                              <target>
                                <path>{pool_tpath}</path>
                              </target>
                            </pool>                            
                        ''',
                    'nfs':'''
                            <pool type="netfs">
                              <name>{pool_name}</name>
                              <source>
                                <host name="{pool_host}"/>
                                <dir path="{pool_spath}"/>
                                <format type='nfs'/>
                              </source>
                              <target>
                                <path>{pool_tpath}</path>
                              </target>
                            </pool>                    
                        ''',
                    'iscsi':'''
                            <pool type="iscsi">
                              <name>{pool_name}</name>
                              <source>
                                <host name="{pool_host}"/>
                                <device path="{pool_spath}"/>
                              </source>
                              <target>
                                <path>{pool_tpath}</path>
                              </target>
                            </pool>                        
                        ''',
                     'gluster':'''
                            <pool type="gluster">
                              <name>{pool_name}</name>
                              <source>
                                <name>{pool_name}</name>
                                <host name='{pool_host}'/>
                                <dir path='{pool_spath}'/>
                              </source>
                            </pool>                     
                         ''',
                    'zfs':'''
                            <pool type="zfs">
                              <name>{pool_name}</name>
                              <source>
                                <name>{pool_name}</name>
                                <device path="{pool_spath}"/>
                              </source>
                            </pool>                    
                        '''
                    }
    if storage_pool_xml.has_key(pool_type):
        pool_xml = storage_pool_xml.get(pool_type)
        pool_xml = pool_xml.format(pool_type=pool_type,pool_name=pool_name,pool_spath=pool_spath,
                                   pool_tpath=pool_tpath,pool_host=pool_host,)
        return pool_xml
    else:
        return False
    
def CreateBridgeNetwork(name,bridgeName,mode): 
    '''创建桥接网络'''
    network_xml = '''
            <network>
                  <name>{name}</name>
                  <forward mode='bridge'/>
                  <bridge name='{bridgeName}'/>
    '''.format(name=name,bridgeName=bridgeName)             
    if mode == 'openvswitch':network_xml += '''<virtualport type='openvswitch'/>'''
    network_xml += '''</network>'''
    return network_xml 
    
def CreateNatNetwork(netName,dhcpIp,dhcpMask,dhcpStart,dhcpEnd): 
    '''创建nat网络'''
    network_xml = '''
        <network>
          <name>{netNam}</name>
          <bridge name="{netNam}" />
          <forward mode="nat"/>
          <ip address="{dhcpIp}" netmask="{dhcpMask}">
            <dhcp>
              <range start="{dhcpStart}" end="{dhcpEnd}" />
            </dhcp>
          </ip>
        </network>'''
    network_xml = network_xml.format(netNam=netName,dhcpIp=dhcpIp,dhcpMask=dhcpMask,
                                     dhcpStart=dhcpStart,dhcpEnd=dhcpEnd)
    return network_xml 
    
        
def CreateNetcard(nkt_br,ntk_name,data,nkt_vlan=0):
    if   data.get('mode') == 'openvswitch' and data.get('type') == 'bridge' :
        ntk_xml = '''
                <interface type='bridge'>
                    <start mode='onboot'/>
                    <source bridge='{nkt_br}'/>
                    <model type='virtio'/>
                    <virtualport type='openvswitch' />
                    <vlan>
                      <tag id='{nkt_vlan}'/>
                    </vlan>  
                    <target dev='{ntk_name}'/>                   
                </interface> 
            '''
        ntk_xml = ntk_xml.format(nkt_br=nkt_br,nkt_vlan=nkt_vlan,ntk_name=ntk_name) 
    elif  data.get('mode') == 'brctl' and data.get('type') == 'bridge': 
        ntk_xml = '''
              <interface type='bridge'>
                <start mode='onboot'/>
                <source bridge='{nkt_br}'/>
                <target dev='{ntk_name}'/>
                <model type='virtio'/>
              </interface>
            '''      
        ntk_xml = ntk_xml.format(nkt_br=nkt_br,nkt_vlan=nkt_vlan,ntk_name=ntk_name)          
    elif data.get('mode') == 'brctl' and data.get('type') == 'nat':
        ntk_xml = '''
            <interface type='network'>
               <source network='{nkt_br}'/>
               <model type='virtio'/>
               <target dev='{ntk_name}'/>
            </interface>              
            '''      
        ntk_xml = ntk_xml.format(nkt_br=nkt_br,ntk_name=ntk_name)                      
    return ntk_xml

def CreateDisk(volume_path,diskSn=None):    
    if diskSn:
        disk_xml = '''
            <disk type='file' device='disk'>
              <driver name='qemu' type='qcow2' cache='none'/>
              <source file='{volume_path}'/>
              <target dev='{diskSn}' bus='virtio'/>
            </disk>                
            '''
        disk_xml = disk_xml.format(volume_path=volume_path,diskSn=diskSn)
    else:
        disk_xml = '''
                <disk type='file' device='disk'>
                  <driver name='qemu' type='qcow2' cache='none'/>
                  <source file='{volume_path}'/>
                  <target dev='vda' bus='virtio'/>
                </disk>                
        '''
        disk_xml = disk_xml.format(volume_path=volume_path)
    return disk_xml

def CreateCdrom(isoPath,diskSn):
    xml = '''
            <disk type='file' device='cdrom'>
              <driver name='file'/>
              <source file='{isoPath}'/>
              <target dev='{diskSn}'/>
              <readonly/>
            </disk>            
        '''.format(isoPath=isoPath,diskSn=diskSn)
    return xml
       
def CreateIntanceConfig(dom_name,maxMem,mem,cpu,disk,iso_path,network):
    if isinstance(mem, int) and isinstance(maxMem, int):
        mem = mem*1024  
        maxMem = maxMem*1024
    dom_xml = '''
        <domain type='kvm'>  
                <name>{dom_name}</name>
                <memory unit='KiB'>{mem}</memory>
                <currentMemory unit='KiB'>{mem}</currentMemory>
                  <memtune>
                    <hard_limit unit='KiB'>{maxMem}</hard_limit>
                    <soft_limit unit='KiB'>{maxMem}</soft_limit>
                  </memtune>
                <vcpu placement='static'  current="{cpu}">32</vcpu>
                <os>  
                  <type arch='x86_64' machine='pc'>hvm</type>  
                  <boot dev='hd'/>
                  <boot dev='cdrom'/> 
                  <bootmenu enable='yes' timeout='3000'/>
               </os>  
               <features>  
                 <acpi/>  
                 <apic/>  
                 <pae/>  
               </features>  
               <clock offset='localtime'/>  
               <devices>  
                 <emulator>/usr/libexec/qemu-kvm</emulator>  
                {disk} 
                <disk type='file' device='cdrom'>  
                    <source file='{iso_path}'/> 
                    <target dev='hda' bus='ide'/>  
                </disk>  
                {network}
                <channel type='unix'>
                   <target type='virtio' name='org.qemu.guest_agent.0'/>
                </channel>
                <input type='mouse' bus='ps2'/>  
                 <graphics type='vnc' port='-1' autoport='yes' listen = '0.0.0.0' keymap='en-us'/>
                <input type='tablet' bus='usb'/>
               </devices>  
             </domain>        
    '''
    dom_xml = dom_xml.format(dom_name=dom_name,mem=mem,cpu=cpu,maxMem=maxMem,
                             disk=disk,iso_path=iso_path,network=network)
    return dom_xml


