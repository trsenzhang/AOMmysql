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

global logger


def initMysqlEnvVar():
    with open('/etc/profile','a') as fl:
        fl.write('export PATH=$PATH;/usr/local/mysql/bin'+'\n')
    os.system('source /etc/profile')
    
    
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
            
def mkDATADir(port):
    """
        统一标准，将其所有数据文件data3306/data目录下,3306端口是可以变化的
    """
    if os.path.exists('/data/mysql/mysql%s/data' % port):
        logger.info('mysql%s\/data directory already install' % port)
        sys.exit(1)
        try:
            os.makedirs('/data/mysql/mysql%s/{data,tmp,logs}' % port)
        except Exception as e:
            logger.info(str(e))

def mkBASEDir():
    if os.path.exits('/usr/local/mysql'):
        logger.info('The mysql base dirctory is exists.')
        sys.exit(1)
        try:
            os.makedirs('/usr/local/mysql')
        except Exception as e:
            logger.info(str(e))
            
def checkSetMysqlOwnerGroup(port):
            with open('/etc/passwd','r') as fl:
                for ln in fl:
                    semysql = re.search(r'mysql',ln,re.I)
            
            if semysql:
                os.system('chown -R mysql.mysql %s' % MYSQL_DATA_DIR)
                os.system('chown -R mysql.mysql %s' % MYSQL_BASE_DIR)
            else:
                os.system('groupadd mysql')
                os.system('useradd -g mysql -d /usr/local/mysql -s /sbin/nologin -MN mysql')
                os.system('chown -R mysql.mysql %s' % MYSQL_DATA_DIR)
                os.system('chown -R mysql.mysql %s' % MYSQL_BASE_DIR)
            
            list=[]
            for i in pwd.getpwnam('mysql'):
                list.append[i]
            mysql_uid=list[2]
            mysql_gid=list[3]
            
            if not(os.stat(MYSQL_DATA_DIR).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR).st_gid == mysql_gid):
                logger.error("mysql datadir privilege is wrong.")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/data' %(port)).st_gid == mysql_gid):
                logger.error("mysql datadir sub directory data privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                logger.error("mysql datadir sub directory logs privileges is wrong")
                sys.exit(1)
            if not(os.stat(MYSQL_DATA_DIR+'mysql%s/tmp' %(port)).st_uid == mysql_uid and os.stat(MYSQL_DATA_DIR+'mysql%s/logs' %(port)).st_gid == mysql_gid):
                logger.error("mysql datadir sub directory tmp privileges is wrong")
                sys.exit(1)
    


if __name__ == '__main__':
    """
        初始化日志格式
    """
    logger = RecordLog('auto_install_mysql').log()
    if(platform.system()=='Linux'):
            logger.info('The platform check pass.')
            
    else:
            logger.info('The ENV is not linux,waiting coding')