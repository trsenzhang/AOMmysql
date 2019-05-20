# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 09:21:47 2019
功能：
1.自动化部署单实例mysql数据库
注意事项
@author: mzhang
"""

import os
from util.record_logging import RecordLog
from util.transSoft import OptRemote
import platform
import re
import sys
import pwd
import tarfile

"""
    设置安装目录和数据目录的权限
"""
MYSQL_DATA_DIR = '/data/mysql/'
MYSQL_BASE_DIR = '/usr/local/mysql/'
MYSQL_CNF_DIR = '/etc/'
MYSQL_BACK_DIR = '/data/backup/mysql/'

INSTALL_MYSQL_SOFT_DIR='/usr/local'
INSTALL_MYSQL_SOFT_IP='172.18.0.160'
INSTALL_MYSQL_SOFT_PORT='22'
INSTALL_MYSQL_SOFT_USER='root'
INSTALL_MYSQL_SOFT_PWD='root'

"""
    soft server center
"""
#这个目录是自己定义出来的，方面集中化定制管理
SERVER_SOFT_DIR='/dfile'
SOFT_NAME='mysql-5.7.24-linux-glibc2.12-x86_64.tar.gz'

global logger

    
    
def unzipMysqlInstallPackage(mysqlInstallPackage):
    """
        将tar包解压至base dirctory目录下
    """
    if not os.path.exists(mysqlInstallPackage):
        logger.error("mysql install package %s is not exists" % mysqlInstallPackage )
        sys.exit(1)
    else:
        try:
            os.chdir(os.path.dirname(mysqlInstallPackage))
            tf = tarfile.open(mysqlInstallPackage,'r:gz')
            file_names = tf.getnames()
            for file_name in file_names:
                tf.extract(file_name,MYSQL_BASE_DIR)
            tf.extractall()
            tf.close()
        except Exception as e:
            logger.error(str(e))
            


    
    

if __name__ == '__main__':
    """
        初始化日志格式
    """
    logger = RecordLog('auto_install_mysql').log()
    
    """
        平台判定
    """
    if(platform.system()=='Linux'):
            logger.info('The platform check pass.')
            """
                copy soft to remote servers,
                single porcess opt
                sendSoft(self,hostname,port,username,password)
                note:int(port) ，port必须是int类型
            """
            
            tr=OptRemote(logger,INSTALL_MYSQL_SOFT_IP,int(INSTALL_MYSQL_SOFT_PORT),INSTALL_MYSQL_SOFT_USER,INSTALL_MYSQL_SOFT_PWD)
            tr.sendSoft(os.path.join(SERVER_SOFT_DIR,SOFT_NAME),os.path.join(INSTALL_MYSQL_SOFT_DIR,SOFT_NAME))
            
            
            
            """
                初始化环境变量
            """
            ##检查是否有python环境            
            logger.info(tr.execRmotecmd("python --version"))
            
            
    else:
            logger.info('The ENV is not linux,waiting coding')