

1. 构建基础镜像(修改requirements.txt后需要重新构建)
   根目录下执行：
   docker build -t vmp-base  -f docker/Dockerfile-base .
   或者使用脚本：docker/build-base.sh

2. 修改Django配置文件OpsManage/setting.py

    - 需要使用Django来访问静态文件时需要修改DEBUG = True(Django仅在调试模式下能对外提供静态文件访问)
    - 修改DATABASES，数据库改成使用sqlite3

4. 构建应用镜像

   根目录下执行：
   docker build -t vmp-app -f docker/Dockerfile-app .

   或者使用脚本：docker/build-app.sh

5. 构建静态文件镜像(可选)

    根目录下执行：
    docker build -t vmp-static -f docker/Dockerfile-static .

6. 启动容器
   #mkdir -p /data/docker-vol/opsmanage   #数据卷文件夹
   #chmod a+rw /data/docker-vol/opsmanage
   #touch /data/docker-vol/opsmanage/id_rsa   #这个文件根据需要写入用户SSH密钥

   docker run -d --name vmp -p 8000:8000 vmp-app
   #-v /data/docker-vol/opsmanage/id_rsa:/root/.ssh/id_rsa \
   #-v /data/docker-vol/opsmanage/upload:/data/apps/opsmanage/upload \
   #172.31.0.6:5000/vmp-app

7. 初始化数据库
    $ docker run -it --rm vmp-app bash
    python manage.py migrate
    python manage.py createsuperuser
    (按Ctrl+P Ctrl+Q退出)

8. 访问页面
    http://<ip>:8000


