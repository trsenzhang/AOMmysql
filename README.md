# AOMmysql
* 目的：
  
  本项目针对mysql数据库上各种自动化小功能实现，每个小功能里完成一个单一性的功能，例如autoInstall.py完成了推送方式安装，部署mysql软件；
  
* 要求：

1.要求运行python的版本在3.x

    环境配置
    ``` shell
    wget https://www.python.org/ftp/3.7.0/Python-3.7.0.tgz
    yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel libffi-devel gcc make
    ./configure --prefix=/opt/python --enable-optimizations
    make && make install 
    ```
2.测试中安装的mysql服务器的python环境2.7.x可通过

3.软件服务中心服务器到mysql服务器网络上具有连通性



# 自动化推送安装部署mysql软件 (主体逻辑autoInstall.py)

* 流程图如下：

![image](https://github.com/trsenzhang/AOMmysql/blob/master/doc/auto_install_mysql_soft.PNG)

* 运行如下脚本：
``` python
/dfile/python/env/anaconda3/bin/python autoInstall.py
```

* 日志目录：

1.在AOMmysql/logs下面产生主干程序的日志信息

2.在目标服务器上/tmp目录下回产生相关日志信息



# 自动进行MYSQL UAT库部署 preDBcreate.py

* 限制条件:

 1.本脚本只适合linux环境
 
 2.mysql存放的数据目录必须是在LVM上

 3.基于mysql复制架构及LINUX LVM SNAPSHOT技术

 4.一些端口信息已经限制

##### [实际环境部署可参考](http://www.trsenzhangdb.com/?p=1232)

* 运行方式:
``` shell
sh preDBcreate.sh
```
或者放crontab中，定期，我所在的实际生产中放置crontab中进行定期调度


# 修复1032和1062错误 replCheckStatus.py 

* 工具介绍：

2019-06-27添加自动修复1062错误；通过在slave端运行repl.sh即可修复1062和1032错误（在5.7；5.6版本测试均已没有问题）；

本工具依赖mysqlbinlog及pymysql

* 原理：

1.1062错误因主键冲突，所以通过报错信息将重复的主键在slave端删除，然后重新开启sql_thread

2.1032错误因delete或者update数据主库不存在（默认每张表必须要有主键），通过binlog分析首先在备库中insert一条数据后，再开启sql_thread

* 要求：

 1.binlog必须是row格式

 2.GTID是否开启没有做强制要求（实际及测试中的环境都是基于GTID模式）

* bug 修复：
  
  1.20190702修复master端DELETE数据时发生1032错误，不可用


1062错误案例中日志信息记录：
```
....
2019-06-27 09:54:23.981953 : INFO : col_type:var
2019-06-27 09:54:23.981953 : INFO : 1062sql :delete from trsen.trsen where id='1906260946257477619'
2019-06-27 09:54:23.981953 : INFO : repaired 1062 error finished, error row:1
2019-06-27 09:54:23.981953 : INFO : Slave_IO_Running: Yes,Slave_SQL_Running:No,Last_Errno:1062
2019-06-27 09:54:23.981953 : INFO : col_type:var
2019-06-27 09:54:23.981953 : INFO : 1062sql :delete from trsen.trsenwhere id='1906260946257477620'
2019-06-27 09:54:23.981953 : INFO : repaired 1062 error finished, error row:1
2019-06-27 09:54:23.981953 : INFO : Slave_IO_Running: Yes,Slave_SQL_Running:No,Last_Errno:1062
2019-06-27 09:54:23.981953 : INFO : col_type:var
2019-06-27 09:54:23.981953 : INFO : 1062sql :delete from trsen.trsenwhere id='1906260946257487621'
2019-06-27 09:54:23.981953 : INFO : repaired 1062 error finished, error row:1
2019-06-27 09:54:23.981953 : INFO : Slave_IO_Running: Yes,Slave_SQL_Running:No,Last_Errno:1062
2019-06-27 09:54:23.981953 : INFO : col_type:var
2019-06-27 09:54:23.981953 : INFO : 1062sql :delete from trsen.trsen where id='1906260946257487622'
2019-06-27 09:54:23.981953 : INFO : repaired 1062 error finished, error row:1
```


#####[1032错误测试模拟](http://www.trsenzhangdb.com/?p=1241)









# 联系作者:
QQ邮箱：736421094@qq.com


















