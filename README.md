## VManagePlatform是什么?
一个KVM虚拟化管理平台

**开源协议**：[GNU General Public License v2](http://www.gnu.org/licenses/old-licenses/gpl-2.0.html)

**开源声明**：欢迎大家star或者fork我的开源项目，如果大家在自己的项目里面需要引用该项目代码，请在项目里面申明协议和版权信息。
## 开发语言与框架：
* 编程语言：Python2.7 + HTML + JScripts
* 前端Web框架：Bootstrap 
* 后端Web框架：Django  
* 后端Task框架：Celery + Redis

## QQ交流群
![image](https://github.com/welliamcao/OpsManage/blob/master/demo_imgs/qq_group.png)

## VManagePlatform有哪些功能？

* Kvm虚拟机`生产周期`管理功能
    *  资源利用率（如：CPU、MEM、磁盘、网络）
    *  实例控制（如：生存周期管理、快照技术，Web Console等等）
    *  设备资源控制（如：在线调整内存、CPU资源、热添加、删除硬盘）
* 存储池管理
    *  增减卷，支持主流类型存储类型
    *  资源利用率
* 网络管理
    *  支持SDN，底层网络使用OpenVSwitch/Linux Bridge，IP地址分配，网卡流量限制等等。
* 用户管理
    *  支持用户权限，用户组，用户虚拟机资源分配等等 
* 宿主机
    *  资源利用率，实例控制

## 环境要求：
* 编程语言：Python2.7 
* 系统：CentOS 7 
* 网络规划：管理网络接口=1，虚拟化数据网络>=1，如果只有一个网卡使用OpenVswitch时需要手动配置网络以免丢失网络
* SDN需求：OpenVswitch Or Linux Birdge

## TIPS：
* 控制服务器：执行1-10步骤 
* 节点服务器：执行2/3/4步骤，在控制服务器上执行5步骤中的ssh-copy-id
* 为了更好的体验，建议使用Chrome或者Foxfire，如果要获取虚拟机ip，请在虚拟机里面安装qemu-guest-agent(centos 6需要安装libvirt>=2.3.0以上)
* 主机列表跟用户中心-我的虚拟机的数据更新，需要在任务调度里面配置task

## 虚拟机添加流程：
* 第一步，平台先添加宿主机（计算节点） 
* 第二步，添加数据类型存储池与镜像存储池
	* 镜像存储池： 计算节点添加dir类型存储池，把ISO镜像文件放到存储池里面或者可以将ISO镜像文件做成NFS共享，添加存储池的时候选择nfs模式。（注：以便添加虚拟机的时候能加载到系统镜像）
	* 数据存储池：按照页面添加即可，主要用来存储虚拟机硬盘。
* 第三步，计算节点添加网络，可选择bridge与nat模式
* 第四步，为计算节点分配虚拟机
* 第五步，配置任务调度，自动更新计算节点虚拟机资源信息


## 安装环境配置</br>

一、配置需求模块</br>
```
# yum install zlib zlib-devel readline-devel bzip2-devel openssl-devel gdbm-devel libdbi-devel ncurses-libs kernel-devel libxslt-devel libffi-devel python-devel libvirt libvirt-client libvirt-devel gcc git mysql-devel -y
# mkdir -p /opt/apps/ && cd /opt/apps/
# git clone https://github.com/welliamcao/VManagePlatform.git
# cd VManagePlatform
# pip install -r requirements.txt
```
二、安装kvm
```
1、关闭防火墙，selinux
# systemctl stop firewalld.service && systemctl disable firewalld.service
# setenforce 0 临时关闭
# systemctl stop NetworkManager
# systemctl disable NetworkManager


2、安装kvm虚拟机
# yum install python-virtinst qemu-kvm virt-viewer bridge-utils virt-top libguestfs-tools ca-certificates libxml2-python audit-libs-python device-mapper-libs 
# 启动服务
# systemctl start libvirtd
注：下载virtio-win-1.5.2-1.el6.noarch.rpm，如果不安装window虚拟机或者使用带virtio驱动的镜像可以不用安装
# rpm -ivh virtio-win-1.5.2-1.el6.noarch.rpm

节点服务器不必执行
# yum -y install dnsmasq
# mkdir -p /var/run/dnsmasq/
```

三、安装OpenVswitch（如果使用底层网络使用Linux Bridge可以不必安装）
```
安装openvswitch
# yum install gcc make python-devel openssl-devel kernel-devel graphviz kernel-debug-devel autoconf automake rpm-build redhat-rpm-config libtool 
# cd /usr/local/src
# wget http://openvswitch.org/releases/openvswitch-2.3.1.tar.gz
# tar xfz openvswitch-2.3.1.tar.gz
# mkdir -p ~/rpmbuild/SOURCES
# cp openvswitch-2.3.1.tar.gz ~/rpmbuild/SOURCES
# sed 's/openvswitch-kmod, //g' openvswitch-2.3.1/rhel/openvswitch.spec > openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
# rpmbuild -bb --without check openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
# yum localinstall ~/rpmbuild/RPMS/x86_64/openvswitch-2.3.1-1.x86_64.rpm
如果出现python依赖错误
# vim openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
BuildRequires: openssl-devel
后面添加
AutoReq: no

# systemctl start openvswitch

```

四、配置Libvirt使用tcp方式连接
```
# vim /etc/sysconfig/libvirtd
LIBVIRTD_CONFIG=/etc/libvirt/libvirtd.conf
LIBVIRTD_ARGS="--listen"

# vim /etc/libvirt/libvirtd.conf  #最后添加
listen_tls = 0
listen_tcp = 1
tcp_port = "16509"
listen_addr = "0.0.0.0"
auth_tcp = "none"
# systemctl restart libvirtd 
```
五、配置SSH信任
```
# ssh-keygen -t  rsa
# ssh-copy-id -i ~/.ssh/id_rsa.pub  root@ipaddress
```

六、安装数据库(MySQL,Redis)
```
安装配置MySQL
# yum install mysql-server mysql-client 
# systemctl start mysqld.service
# mysql -u root -p 
mysql> create database vmanage;
mysql> grant all privileges on vmanage.* to 'username'@'%' identified by 'userpasswd';
mysql>quit

安装配置Redis
# wget http://download.redis.io/releases/redis-3.2.8.tar.gz
# tar -xzvf redis-3.2.8.tar.gz
# cd redis-3.2.8
# make
# make install
# vim redis.conf
daemonize yes
loglevel warning
logfile "/var/log/redis.log"
bind 你的服务器ip地址
# cd ../
# mv redis-3.2.8 /usr/local/redis
# /usr/local/redis/src/redis-server /usr/local/redis/redis.conf
```

七、配置Django
```
# cd /opt/apps/VManagePlatform/VManagePlatform/
# vim settings.py
7.1、修改BROKER_URL：改为自己的地址
7.2、修改DATABASES：
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.mysql',
        'NAME':'vmanage',
        'USER':'自己的设置的账户',
        'PASSWORD':'自己的设置的密码',
        'HOST':'MySQL地址'
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
7.3、修改STATICFILES_DIRS
STATICFILES_DIRS = (
     '/opt/apps/VManagePlatform/VManagePlatform/static/',
    )
TEMPLATE_DIRS = (
#     os.path.join(BASE_DIR,'mysite\templates'),
    '/opt/apps/VManagePlatform/VManagePlatform/templates',
)
```

八、生成VManagePlatform数据表
```
# cd /opt/apps/VManagePlatform/
# python manage.py migrate
# python manage.py createsuperuser
```
九、启动VManagePlatform
```
# cd /opt/apps/VManagePlatform/
# python manage.py runserver youripaddr:8000
```

十、配置任务系统
```
# echo_supervisord_conf > /etc/supervisord.conf
# vim /etc/supervisord.conf
最后添加
[program:celery-worker]
command=/usr/bin/python manage.py celery worker --loglevel=info -E -B  -c 2
directory=/opt/apps/VManagePlatform
stdout_logfile=/var/log/celery-worker.log
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
numprocs=1

[program:celery-beat]
command=/usr/bin/python manage.py celery beat
directory=/opt/apps/VManagePlatform
stdout_logfile=/var/log/celery-beat.log
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
numprocs=1

[program:celery-cam]
command=/usr/bin/python manage.py celerycam
directory=/opt/apps/VManagePlatform
stdout_logfile=/var/log/celery-celerycam.log
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
numprocs=1

启动celery
# /usr/local/bin/supervisord -c /etc/supervisord.conf
# supervisorctl status
```

## 提供帮助

如果您觉得VManagePlatform对您有所帮助，可以通过下列方式进行捐赠，谢谢！

![image](https://github.com/welliamcao/OpsManage/blob/master/demo_imgs/donate.png)

## 部分功能截图:
    用户中心
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/user.png)</br>
    登录页面
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/login.png)</br>
    用户注册需要admin激活才能登陆</br>
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/register.png)</br>
    主页
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/index.png)</br>
    任务调度
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/task.png)</br>
    宿主机资源</br>
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/server.png)</br>
    虚拟机资源</br>
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/instance.png)</br>
    Web Console</br>
![](https://github.com/welliamcao/VManagePlatform/raw/master/demo_images/consle.png)</br>
