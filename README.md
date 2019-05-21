# AOMmysql
目的：
  
  本项目针对mysql数据库上各种自动化小功能实现，每个小功能里完成一个单一性的功能，例如autoInstall.py完成了推送方式安装，部署mysql软件；
  

要求：

1.要求运行python的版本在3.x

2.测试中安装的mysql服务器的python环境2.7.x可通过

3.软件服务中心服务器到mysql服务器网络上具有连通性


功能运行方式：

1.自动化安装
流程图如下：
![image](https://github.com/trsenzhang/AOMmysql/blob/master/doc/auto_install_mysql_soft.PNG)

/dfile/python/env/anaconda3/bin/python autoInstall.py


日志信息：

1.在AOMmysql/logs下面产生主干程序的日志信息

2.在目标服务器上/tmp目录下回产生相关日志信息
