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
SOFT_NAME_FILE='mysql-5.7.24-linux-glibc2.12-x86_64'
CUR_PATH = os.path.dirname(os.path.realpath(__file__))

global logger
            



def newI():
    tr=OptRemote(logger,INSTALL_MYSQL_SOFT_IP,int(INSTALL_MYSQL_SOFT_PORT),INSTALL_MYSQL_SOFT_USER,INSTALL_MYSQL_SOFT_PWD)
    return(tr)

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
                      
            newI().sendSoft(os.path.join(SERVER_SOFT_DIR,SOFT_NAME),os.path.join(INSTALL_MYSQL_SOFT_DIR,SOFT_NAME))
                        
            """
                初始化环境变量
            """
            ##检查是否有python环境           
            
            if(newI().execRmotecmd("python --version")==0):
                logger.info("the remote server have py env.")
                #push py files
                _L_PYFILE='%s/pullpy/initMysqlENV.py' %(CUR_PATH)
                _R_PYFILE='/tmp/initMysqlENV.py'
                newI().sendSoft(_L_PYFILE,_R_PYFILE)
                
                #初始化remote server mysql安装环境
                if(newI().execRmotecmd("python /tmp/initMysqlENV.py mkdatadir")==0):
                    logger.info('remote servers data directory create success.')  
                    if(newI().execRmotecmd("python /tmp/initMysqlENV.py unzipm")==0):
                        logger.info('remote servers mysql soft unzip success.')
                        if(newI().execRmotecmd("python /tmp/initMysqlENV.py addusergroup")==0):
                            logger.info('remote servers create user and group success.')
                            if(newI().execRmotecmd("python /tmp/initMysqlENV.py initenv")==0):
                                logger.info('remote servers /etc/profile update success.')
                
                
            else:
                logger.info("please check target servers py env.")
            
            
                
            
            
    else:
            logger.info('The ENV is not linux,waiting coding')