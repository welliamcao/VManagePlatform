## VManagePlatform是什么?
一个KVM虚拟化管理平台

## 开发语言与框架：
* 编程语言：Python2.7 + HTML + JScripts
* 前端Web框架：Bootstrap 
* 后端Web框架：Django  
* 后端Task框架：Celery + Redis

## VManagePlatform有哪些功能？

* Kvm虚拟机`生产周期`管理功能
    *  资源利用率（如：CPU、MEM、磁盘、网络）
    *  实例控制（如：生存周期管理、快照技术，Web Console等等）
    *  设备资源控制（如：在线调整内存、CPU资源、热添加、删除硬盘）
* 存储池管理
    *  增减卷，支持主流类型存储类型
    *  资源利用率
* 网络管理
    *  支持SDN，底层网络使用OpenVSwitch/Linux Bridge，支持子网隔离，IP地址分配，网卡流量限制等等。
* 用户管理
    *  支持用户权限，用户组，用户虚拟机资源分配等等 
* 宿主机
    *  资源利用率，实例控制

## 环境要求：
* 编程语言：Python2.7 
* 系统：CentOS 6
* 网络规划：管理网络接口=1，虚拟化数据网络>=1，如果只有一个网卡使用OpenVswitch时需要手动配置网络以免丢失网络
* SDN需求：OpenVswitch Or Linux Birdge

## TIPS：
* 控制服务器：执行1-10步骤 
* 节点服务器：执行2/3/4步骤，在控制服务器上执行5步骤中的ssh-copy-id
* 为了更好的体验，建议使用Chrome或者Foxfire

## 安装环境配置</br>

一、配置需求模块</br>
```
# pip install -r requirements.txt
```
二、安装kvm
```
1、关闭防火墙，selinux
# service iptables stop
# setenforce 0 临时关闭
# chkconfig NetworkManager off

2、安装kvm虚拟机
# yum install kvm libvirt libvirt-devel python-virtinst python-virtinst qemu-kvm virt-viewer bridge-utils virt-top libguestfs-tools ca-certificates libxml2-python audit-libs-python device-mapper-libs 
# 启动服务
# /etc/init.d/libvirtd start
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
# wget http://openvswitch.org/releases/openvswitch-2.3.1.tar.gz
# tar xfz openvswitch-2.3.1.tar.gz
# mkdir -p ~/rpmbuild/SOURCES
# cp openvswitch-2.3.1.tar.gz rpmbuild/SOURCES
# sed 's/openvswitch-kmod, //g' openvswitch-2.3.1/rhel/openvswitch.spec > openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
# rpmbuild -bb --without check ~/openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
# yum localinstall /root/rpmbuild/RPMS/x86_64/openvswitch-2.3.1-1.x86_64.rpm
如果出现python依赖错误
# vim openvswitch-2.3.1/rhel/openvswitch_no_kmod.spec
BuildRequires: openssl-devel
后面添加
AutoReq: no

# /etc/init.d/openvswitch start

```

四、配置Libvirt使用tcp方式连接
```
# vim /etc/sysconfig/libvirtd
LIBVIRTD_CONFIG=/etc/libvirt/libvirtd.conf
LIBVIRTD_ARGS="--listen"

# vim /etc/libvirt/libvirtd.conf
listen_tls = 0
listen_tcp = 1
tcp_port = "16509"
listen_addr = "0.0.0.0"
auth_tcp = "none"
```
五、配置SSH信任
```
# ssh-keygen -t  rsa
# ssh-copy-id -i ~/.ssh/id_rsa.pub  root@ipaddress
```

六、安装数据库(MySQL,Redis)
```
安装配置MySQL
# yum install mysql-server mysql-client mysql-devel
# service mysqld start
# mysql -u root -p 
mysql> create database vmanage;
mysql> grant all privileges on vmanage.* to 'username'@'%' identified by 'userpasswd';
mysql>quit

安装配置Redis
# wget http://download.redis.io/redis-stable.tar.gz
# tar –zxvf redis-stable.tar.gz
# cd redis-stable
# make && cd src && make install PREFIX=/usr/local/redis
# vim /usr/local/redis/etc/redis.conf
将daemonize的值改为yes
将./dir的值改为/usr/local/redis
# /usr/local/redis/bin/redis-server /usr/local/redis/etc/redis-conf
```

七、配置Django
```
# cd /yourpath/VManagePlatform/VManagePlatform/
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
     '/yourpath/VManagePlatform/VManagePlatform/static/',
    )
TEMPLATE_DIRS = (
#     os.path.join(BASE_DIR,'mysite\templates'),
    '/yourpath/VManagePlatform/VManagePlatform/templates',
)
```

八、生成VManagePlatform数据表
```
# cd /yourpath/VManagePlatform/VManagePlatform/
# python manage.py migrate
# python manage.py createsuperuser
```
九、启动VManagePlatform
```
# cd /yourpath/VManagePlatform/VManagePlatform/
# python manage.py runserver youripaddr:8000
```

十、配置任务系统
```
# echo_supervisord_conf > /etc/supervisord.conf
# vim /etc/supervisord.conf
最后添加
[program:celery-worker]
command=/usr/bin/python manage.py celery worker --loglevel=info -E -B  -c 2
directory=/yourpath/VManagePlatform
stdout_logfile=/var/log/celery-worker.log
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
numprocs=1

[program:celery-beat]
command=/usr/bin/python manage.py celery beat
directory=/yourpath/VManagePlatform
stdout_logfile=/var/log/celery-beat.log
autostart=true
autorestart=true
redirect_stderr=true
stopsignal=QUIT
numprocs=1

[program:celery-cam]
command=/usr/bin/python manage.py celerycam
directory=/yourpath/VManagePlatform
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


## 部分功能截图:
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
