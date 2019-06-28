#/usr/bin/python


"""
限制条件：
1.无法修复一个事务中包含多个DML语句导致的1032
2.无法修复复合主键导致的1032和1062
3.无在修复只读slave上1032和1062
4.无法修复并行复制slave上1032和1062
5.没有记录1062和1032操作前的数据记录

"""

import sys
import os
import re
import optparse
import pymysql
import platform
from util.record_logging import RecordLog

global logger


MYSQL_SHOW_SLAVE_STATUS     = 'SHOW SLAVE STATUS;'
GTID_MODE = "select @@gtid_mode;"
com_mysqlbinlog = "/usr/local/mysql/bin/mysqlbinlog"

r1062 = r"Could not execute Write_rows event on table (.*); Duplicate entry '(.*)' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log (.*), end_log_pos (\d+)"

'''
Could not execute Write_rows event on table intrepaydb.t_dpay_third_collect; Row size too large (> 8126). Changing some columns to TEXT or BLOB or using ROW_FORMAT=DYNAMIC or ROW_FORMAT=COMPRESSED may help. In current row format, BLOB prefix of 768 bytes is stored inline., Error_code: 139; Duplicate entry '1906260940571966027' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log mysql-bin.000173, end_log_pos 112185003, Error_code: 1062
'''

r1062_0 = r"Could not execute Write_rows event on table (.*); Row size too large (.*); Duplicate entry '(.*)' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log (.*), end_log_pos (\d+)"

u1032 = r"Could not execute (.*)_rows event on table (.*); Can't find record in (.*), Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log (.*), end_log_pos (\d+)"

GET_FROM_LOG2="%s -v --base64-output=decode-rows -R --host='%s' --port=%d --user='%s' --password='%s' --start-position=%d --stop-position=%d %s |grep @%s|head -n 1"
GET_FROM_LOG="%s -v --base64-output=decode-rows -R --host='%s' --port=%d --user='%s' --password='%s' --start-position=%d --stop-position=%d %s |egrep '###'"
GET_FROM_LOG_DML_COUNT="%s -v --base64-output=decode-rows -R --host='%s' --port=%d --user='%s' --password='%s' --start-position=%d --stop-position=%d %s |egrep '### WHERE' |wc -l"

FLAGS = optparse.Values()
parser = optparse.OptionParser()


def DEFINE_string(name, default, description, short_name=None):
    if default is not None and default != '':
        description = "%s (default: %s)" % (description, default)
    args = [ "--%s" % name ]
    if short_name is not None:
        args.insert(0, "-%s" % short_name)

    parser.add_option(type="string", help=description, *args)
    parser.set_default(name, default)
    setattr(FLAGS, name, default)

def DEFINE_integer(name, default, description, short_name=None):
    if default is not None and default != '':
        description = "%s (default: %s)" % (description, default)
    args = [ "--%s" % name ]
    if short_name is not None:
        args.insert(0, "-%s" % short_name)

    parser.add_option(type="int", help=description, *args)
    parser.set_default(name, default)
    setattr(FLAGS, name, default)

DEFINE_integer('port', '3306', 'The slave of occur error database port ')
DEFINE_string('user', 'root', 'The slave of occur error mysql user')
DEFINE_string('password', 'root', 'The slave of occur error mysql password')
DEFINE_string('host', '127.0.0.1', 'The slave of occur error ip address')


def ShowUsage():
    parser.print_help()
    
def ParseArgs(argv):
    usage = sys.modules["__main__"].__doc__
    parser.set_usage(usage)
    unused_flags, new_argv = parser.parse_args(args=argv, values=FLAGS)
    return new_argv

def get_conn():
    return pymysql.connect(host=FLAGS.host, port=int(FLAGS.port), user=FLAGS.user,passwd=FLAGS.password)

def get_tb_pk(db_table):
    db, tb = db_table.split('.')
    conn = get_conn()
    sql = "select column_name,ordinal_position,column_type from information_schema.columns where table_schema='%s' and table_name='%s' and column_key='PRI';" % (db, tb)
    cursor = conn.cursor()
    cursor.execute(sql)
    r = cursor.fetchone()
    cursor.close()
    conn.close()
    return r


def get_rpl_mode(conn):
    cursor = conn.cursor()
    cursor.execute(GTID_MODE)
    r = cursor.fetchone()
    print('get_rpl_mode r -> %s' % r)
    if (r[0] == "ON"):
        return 1
    else:
        return 0

def get_only_status(conn):
    conn2=get_conn()
    sql="select @@super_read_only;"
    cursor = conn2.cursor()
    cursor.execute(sql)
    r = cursor.fetchone()
    print('super_read_ony : %s' % r[0])
    conn2.close()
    return r[0]

def optMulitMDL():
        pass

class parallelReplCheck(object):
        pass

class singleReplCheck(object): 
    @staticmethod
    def handler_1062(r,rpl):
        m = re.search(r1062,r['Last_SQL_Error'])
        
        if m is not None: 
            db_table = m.group(1)
            pk_v = m.group(2)
        else:
            m2=re.search(r1062_0,r['Last_SQL_Error'])
            db_table = m2.group(1)
            pk_v = m2.group(3)
            
        conn = get_conn()
        tgp=get_tb_pk(db_table)
        pk_col = tgp[0]
        col_type = str(tgp[2][:3])
        logger.info("col_type:%s" % col_type)
        
        
        if col_type == 'int':
            sql = "delete from %s where %s=%s" % (db_table, pk_col, pk_v)
        else:
            sql = "delete from %s where %s='%s'" % (db_table,pk_col,pk_v)
            
        logger.info("1062sql :%s" % sql)
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            print("1062 excute sql error: %s" % str(e))
            logger.info("1062 excute sql error: %s" % str(e))
        cursor.execute("start slave sql_thread")
        cursor.close()
        conn.commit()
        conn.close()
        return(1)
    
        
    @staticmethod
    def handler_1032(r, rpl):
        p = re.compile(u1032)
        m = p.search(r['Last_SQL_Error'])
        db_table = m.group(2)
        #tb_name = m.group(3)
        log_file_name = m.group(4)
        log_stop_position = m.group(5)
        log_start_position = r['Exec_Master_Log_Pos']
        pk_seq = get_tb_pk(db_table)[1]   
        print ("pk_seq : %s" % pk_seq)
        gfld_c = GET_FROM_LOG_DML_COUNT % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position), int(log_stop_position),log_file_name)
       
        do_getlog = GET_FROM_LOG % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position), int(log_stop_position),log_file_name)
        do_getlog2 = GET_FROM_LOG2 % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position), int(log_stop_position),log_file_name,pk_seq)
        
        '''       
        c=os.popen(gfld_c).readlines()[0]
        print('c: %s' % c)
        if (c > '1'): 
            print('opt multi row 1032')
            p=os.popen(do_getlog).read()
            pk_value=1
        else:
            print('opt 1 row 1032')
        '''
        pk_value = os.popen(do_getlog2).readlines()[0].split("=",2)[1].rstrip() 
        
        print ("pk_value : %s" % pk_value)
        sql = repairSql_1032(db_table, pk_value, pk_seq)
        print("sql : %s" % sql)
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("set session sql_log_bin=0;")
        cursor.execute(sql)
        #cursor.execute("set  session sql_log_bin=1")
        cursor.execute("start slave sql_thread")    
        conn.commit()
        cursor.close()
        conn.close()
        return(1)
        
    
def chk_master_slave_gtid():
    pass
    

def repairSql_1032(db_table, pk_value, pk_seq):
    db, tb_name = db_table.split(".")
    r = "replace into %s.%s "%(db,tb_name)
    
    sql = "select column_name, ORDINAL_POSITION from information_schema.columns where table_schema='%s' and table_name='%s' and IS_NULLABLE='NO';" % (db, tb_name)
    
    col_list=''
    value_list=''
    
    conn = get_conn()
    cusror = conn.cursor()
    cusror.execute(sql)
    result = cusror.fetchall()
    for col in result:
        if (col[1] == pk_seq):
            col_list = col_list +"%s," % (col[0])
            value_list = value_list + "'%s'," % (pk_value)
        else:
            col_list = col_list +"%s," % (col[0])
            value_list = value_list + "'%s'," % ('1')
    print (value_list)
    r = r+"(%s) values(%s)" % ( col_list.rstrip(','), value_list.rstrip(','))
    cusror.close()
    conn.close()
    return r.rstrip(',')
        


def get_slave_status(conn):
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(MYSQL_SHOW_SLAVE_STATUS)
    result = cursor.fetchone()
    return result


def main():
    try:
        conn = get_conn()
    except Exception as e:
        print('Can\'t connect to mysql %s:%s ' %(FLAGS.host,FLAGS.port))
        sys.exit(0)
        
    
    r = get_slave_status(conn)
    
    if (r['Slave_IO_Running'] == "Yes" and r['Slave_SQL_Running'] == "Yes"):
        print("Rpl Ok")
        if (r['Seconds_Behind_Master'] > 0):
            print(r['Seconds_Behind_Master'])            
        conn.close()
        sys.exit(0) 
    
    count = 0 #控制一次循环里status状态因服务器性能问题导致误判的计数器
    while(1):
        #time.sleep(1)#延迟1秒查看slave状态，太快，导致状态检查不准确
        r = get_slave_status(conn)
        #logger.info('Slave_IO_Running: %s,Slave_SQL_Running:%s,Last_Errno:%s' %(r['Slave_IO_Running'],r['Slave_SQL_Running'],r['Last_Errno']) )
        if (r['Slave_IO_Running'] == "Yes" and r['Slave_SQL_Running'] == "No"):
            rpl_mode = get_rpl_mode(conn)
            print("rpl_mode %s " % rpl_mode)
            print(r['Last_Errno'])
            if ( r['Last_Errno'] == 1062 ):
                singleReplCheck.handler_1062(r, rpl_mode)
                #
            if ( r['Last_Errno'] == 1032 ):
               singleReplCheck.handler_1032(r, rpl_mode)
        else:
            count += 1
            logger.info('count :%s' % count)
            if count >=1000000000:
                break
    
    logger.info("slave repaired.")                  
    conn.close()

if __name__ == '__main__':
        logger = RecordLog('auto_check_repl_status_repair').log()
        
        if(platform.system()=='Linux'):
            logger.info('The platform check pass.')
            new_argv = ParseArgs(sys.argv[1:])
            print(new_argv)
            print(FLAGS)
            main()
        else:
            logger.info('The ENV is not linux,waiting coding')
            
        
