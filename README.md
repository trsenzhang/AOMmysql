# AOMmysql
目的：
  
  本项目针对mysql数据库上各种自动化小功能实现，每个小功能里完成一个单一性的功能，例如autoInstall.py完成了推送方式安装，部署mysql软件；
  

要求：

1.要求运行python的版本在3.x

2.测试中安装的mysql服务器的python环境2.7.x可通过

3.软件服务中心服务器到mysql服务器网络上具有连通性


功能运行方式：

一.自动化推送安装部署mysql软件 (主体逻辑autoInstall.py)

流程图如下：

![image](https://github.com/trsenzhang/AOMmysql/blob/master/doc/auto_install_mysql_soft.PNG)

运行如下脚本：

/dfile/python/env/anaconda3/bin/python autoInstall.py


日志信息：

1.在AOMmysql/logs下面产生主干程序的日志信息

2.在目标服务器上/tmp目录下回产生相关日志信息



二.自动进行MYSQL UAT库部署（主体逻辑preDBcreate.py）

限制:

1.本脚本只适合linux环境

2.mysql存放的数据目录必须是在LVM上

3.基于mysql复制架构及LINUX LVM SNAPSHOT技术

4.一些端口信息已经限制

实际环境部署可参考blog:

http://www.trsenzhangdb.com/?p=1232

运行方式:

sh  	preDBcreate.sh

或者放crontab中，定期，我所在的实际生产中放置crontab中进行定期调度






















##########################################################################
#代码问题：请联系QQ:736421094 ,并注明疑问
##########################################################################
