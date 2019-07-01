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

r1062_0 = r"Could not execute Write_rows event on table (.*); Row size too large (.*); Duplicate entry '(.*)' for key 'PRIMARY', Error_code: 1062; handler error HA_ERR_FOUND_DUPP_KEY; the event's master log (.*), end_log_pos (\d+)"

u1032 = r"Could not execute (.*)_rows event on table (.*); Can't find record in (.*), Error_code: 1032; handler error HA_ERR_KEY_NOT_FOUND; the event's master log (.*), end_log_pos (\d+)"

GET_FROM_LOG2="%s -v --base64-output=decode-rows -R --host='%s' --port=%d --user='%s' --password='%s' --start-position=%d --stop-position=%d %s"
GET_FROM_LOG="%s -v --base64-output=decode-rows -R --host='%s' --port=%d --user='%s' --password='%s' --start-position=%d %s"

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


def get_col_info(table_name):
    conn = get_conn()
    col_num = 0
    col_list = []
    cursor = conn.cursor()
    cursor.execute('show create table {table_name}'.format(table_name=table_name))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for item in result[0][1].split("\n")[1:]:
        r = re.search("^`", item.strip())
        if r:
            col_list.append(item.split()[0].strip("`"))
            col_num += 1
    col_list.append(col_num)
    return col_list

def find_row_recode_from_binlog(event, table_name, result):
    table_map_flag = 0
    event_flag = 0
    where_flag = 1
    option_flag = 0
    option_keyword = '### ' + event.split('_')[0].upper()
    new_table_name = '`{schema_name}`.`{table_name}`'.format(schema_name=table_name.split('.')[0],
                                                             table_name=table_name.split('.')[1])
    recode_list = []

    for line in result:

        if line.startswith('#') and re.search("Table_map", line) and re.search(new_table_name, line):
            table_map_flag = 1
        if line.startswith('#') and re.search(event, line):
            event_flag = 1
        if re.search('WHERE', line):
            where_flag = 1
        if line.startswith(option_keyword):
            recode_list.append('---line---')
            option_flag = 1
        if line.startswith('### SET'):
            where_flag = 0
            continue
        if line.startswith('###') and table_map_flag and event_flag and where_flag and option_flag:
            recode_list.append(line.strip())
    recode_list.append('---line---')
    return recode_list

def split_sql(recode_list, col_info):
    num = len(col_info)
    sql_file = []
    id = 0
    for item in recode_list[1:]:
        item = item.strip('### ')
        if id <= num:
            if re.search("^@", item):
                if re.search("^@1", item):
                    a = re.sub("^@1", col_info[id], item)
                else:
                    a = re.sub("^@[\d]+", 'and ' + col_info[id], item)
                if a:
                    id += 1
                    sql_file.append(a)
                else:
                    id = 0
                    sql_file.append(item)
            else:
                id = 0
                sql_file.append(item)
    return sql_file


def create_sql(split_sql_list):
    run_sql = ''
    for item in split_sql_list:
        if item == '---line---':
            run_sql += ';'
            yield run_sql
            run_sql = ''
        else:
            run_sql += ' ' + item
            
            
def delete_or_update_to_insert(delete_sql):
    sql_1 = delete_sql.strip().replace('WHERE', 'VALUES(')
    sql_2 = sql_1.replace('and', ',')
    sql_3 = re.sub(' (\w)+=', ' ', sql_2)
    sql_4 = re.sub(';', ');', sql_3)
    run_sql = re.sub('DELETE FROM|UPDATE', 'INSERT INTO', sql_4)
    return run_sql

def get_SMT_END_F(r,do_getlog2):
    m = re.search("# (.*) end_log_pos (\d+) (.*)",do_getlog2)
    print("m : %s" % m.group(1))
    end_log_pos = int(m.group(1))
    dlog = GET_FROM_LOG2 % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position), end_log_pos,log_file_name)
    
        
    
class singleReplCheck(object): 
        
    @staticmethod
    def handler_1032(r, rpl):
        err_msg = r['Last_SQL_Error']
        col_info=[]
        event = err_msg.split('event')[0].split('execute')[1].strip()
        
        ####test.test
        table_name = err_msg.split('on table')[1].split(';')[0].strip()
        col_info = get_col_info(table_name)
        
        log_file_name = err_msg.split('master log')[1].split(',')[0].strip()
        log_stop_position = err_msg.split('master log')[1].split(',')[1].split()[1]
        log_start_position = r['Exec_Master_Log_Pos']
        
        print('-----')
        do_getlog2 = GET_FROM_LOG2 % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position), int(log_stop_position),log_file_name)
        print(do_getlog2)
        #isn't multi DML in the transaction
        for line in do_getlog2:
            if line.startswith('#') and re.search("flags: STMT_END_F", line):
                print("have SMTM_END_F,is ok.")
                binlog_result=os.popen(do_getlog2).readlines()
                break
            else:
                dlog = GET_FROM_LOG % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position),log_file_name)
                for line in dlog:
                    if line.startswith('#') and re.search("flags: STMT_END_F", line):
                        print("have SMTM_END_F,is ok.")
                        m = re.search("# (.*) end_log_pos (\d+) (.*)",do_getlog2)
                        print("m : %s" % m.group(1))
                        end_log_pos = int(m.group(1))
                        break
                break
                dlog1 = GET_FROM_LOG2 % (com_mysqlbinlog, r['Master_Host'], int(r['Master_Port']),FLAGS.user,FLAGS.password, int(log_start_position),end_log_pos,log_file_name)
                binlog_result=os.popen(dlog1).readlines()
                        
        print("binlog_result :%s" % binlog_result)
        row_recode = find_row_recode_from_binlog(event,table_name,binlog_result)
        print("row_recode :%s" % row_recode)
        split_sql_list = split_sql(row_recode, col_info)
        print("split_sql_list :%s" % split_sql_list)
        ret = create_sql(split_sql_list)
        print(ret)
        conn = get_conn()
        cursor = conn.cursor() 
        print('--0--')
        for line in ret:
            print('--1--')
            if event == "Delete_rows":
                select_sql = line.replace('DELETE','SELECT 1')
            else:
                select_sql = line.replace('UPDATE','SELECT 1 from')
            
            
            print('--2--')
            cursor.execute(select_sql)
            result = cursor.fetchall()
        
            print('--3--')
            if not result:
                insert_sql = delete_or_update_to_insert(line)
                run_sql = ' Error_code: 1032 -- run SQL:  %s' % insert_sql
                
                print('warning %s' % run_sql)
    
                cursor.execute(insert_sql)
                cursor.execute("start slave sql_thread")
            
        cursor.close()
        conn.close()
        print('--4--')
        return(1)
        
    
def chk_master_slave_gtid():
    pass    
        
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
        r = get_slave_status(conn)
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
            if count >=100:
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
            
        
