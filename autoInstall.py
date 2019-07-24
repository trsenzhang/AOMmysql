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
import configparser 

"""
    设置安装目录和数据目录的权限
"""
'''
#MYSQL_DATA_DIR = '/data/mysql/'
MYSQL_BASE_DIR = '/usr/local/mysql/'
MYSQL_CNF_DIR = '/etc/'
MYSQL_BACK_DIR = '/data/backup/mysql/'

INSTALL_MYSQL_SOFT_DIR='/usr/local'

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
'''

INSTALL_MYSQL_SOFT_IP='172.18.0.160'

"""
 path for  program running.
"""
CUR_PATH = os.path.dirname(os.path.realpath(__file__))

global logger

def readCfg(flag,name):
    _filename='%s/targetinfo/info.cfg' % (CUR_PATH)
    config=configparser.ConfigParser() 
    with open(_filename,'r') as cfgfile:
        config.read_file(cfgfile)
        value=config.get(flag,name) 
        return(value)


def newI():
    INSTALL_MYSQL_SOFT_PORT=readCfg('port','INSTALL_MYSQL_SOFT_PORT')
    INSTALL_MYSQL_SOFT_USER=readCfg('user','INSTALL_MYSQL_SOFT_USER')
    INSTALL_MYSQL_SOFT_PWD=readCfg('user','INSTALL_MYSQL_SOFT_PWD')
    tr=OptRemote(logger,INSTALL_MYSQL_SOFT_IP,int(INSTALL_MYSQL_SOFT_PORT),INSTALL_MYSQL_SOFT_USER,INSTALL_MYSQL_SOFT_PWD)
    return(tr)


if __name__ == '__main__':
    """
        初始化文件目录，文件名称等
    """
    SERVER_SOFT_DIR=readCfg('path','SERVER_SOFT_DIR')
    SOFT_NAME=readCfg('file','SOFT_NAME')
    INSTALL_MYSQL_SOFT_DIR=readCfg('path','INSTALL_MYSQL_SOFT_DIR')
    
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
                
                _dict={'initMysqlENV.py':'pullpy/initMysqlENV.py',
                       'info.cfg':'targetinfo/info.cfg',
                       'record_logging.py':'util/record_logging.py'}
                for key,value in _dict:
                    _R_PYFILE='/tmp/%s' % key
                    _L_PYFILE='%s/%s' %(CUR_PATH,value)
                    newI().sendSoft(_L_PYFILE,_R_PYFILE)
                
                #初始化remote server mysql安装环境
                newI().execRmotecmd("python /tmp/initMysqlENV.py mkdatadir")
                newI().execRmotecmd("python /tmp/initMysqlENV.py unzipm")
                newI().execRmotecmd("python /tmp/initMysqlENV.py addusergroup")
                newI().execRmotecmd("python /tmp/initMysqlENV.py initenv")
                
                
            else:
                logger.info("please check target servers py env.")
            
            
                
            
            
    else:
            logger.info('The ENV is not linux,waiting coding')
    