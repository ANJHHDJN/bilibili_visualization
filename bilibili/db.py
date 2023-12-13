import time
import pymysql
import threading
from dbutils.pooled_db import PooledDB,SharedDBConnection
import os,sys
import pandas as pd
class MySQLhelper(object ):
    def __init__(self, host, port, dbuser, password, database):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=host,
            port=int(port),
            user=dbuser,
            password=password,
            database=database,
            charset='utf8'
        )

    def create_conn_cursor(self):
        conn = self.pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return conn,cursor

    def fetch_all(self, sql, args=None):
        conn,cursor = self.create_conn_cursor()
        cursor.execute(sql,args)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result


    def insert_one(self,sql, args=None):
        conn,cursor = self.create_conn_cursor()
        res = cursor.execute(sql,args)
        conn.commit()
        print(res)
        conn.close()
        return res

    def update(self,sql, args=None):
        conn,cursor = self.create_conn_cursor()
        res = cursor.execute(sql,args)
        conn.commit()
        print(res)
        conn.close()
        return res

    def delete(self, sql, args):
        conn, cursor = self.create_conn_cursor()
        res = cursor.execute(sql, args)
        conn.commit()
        print(res)
        conn.close()
        return res

default_sqlhelper = MySQLhelper(host="localhost", port="3306", dbuser="root", password="", database="mysql")

# 将csv文件内的内容写入数据库，数据库存储的类型均为varchar
def write_database(con,cur,file_path,table_name):
    cur.execute("set names utf8")
    cur.execute("SET character_set_connection=utf8;")

    with open(file_path, 'r', encoding='utf8') as f:
        reader = f.readline()
        # print(reader)
        # 做成列表
        devide = reader.split(',')
        # 去除最后的换行符
        devide[-1] = devide[-1].rstrip('\n')
        print(devide)
        if devide[0]=='':
            devide[0] = 'index_'
        elif devide[0]=='Unnamed: 0':
            devide[0] = 'Unnamed'
        print(devide)

    column = ''
    for dd in devide:
        # 如果列名里存在不规则命名，则把命名规则化删去
        if '/' in dd:
            column = column + dd.replace('/', '_') + ' varchar(255),'
        elif '-' in dd:
            column = column + dd.replace('-', '_') + ' varchar(255),'
        elif '\\N' in dd:
            column = column + dd.replace('\\N', 'None') + ' varchar(255),'
        elif ' ' in dd:
            column = column + dd.replace(' ', '_') + ' varchar(255),'
        elif 'from' in dd:
            column = column + dd.replace('from', 'from_') + ' varchar(255),'
        elif 'out' in dd:
            column = column + dd.replace('out', 'out_') + ' varchar(255),'
        # elif ' ' in dd:
        #     column = column + dd.replace(' ', 'index') + ' varchar(255),'
        else:
            column = column + dd + ' varchar(255),'

    # 去除最后一个多余的，
    col = column.rstrip(',')
    # print(column[:-1])

    create_table_sql = 'create table if not exists {} ({}) DEFAULT CHARSET=utf8'.format(table_name, col)
    print(create_table_sql)
    # print(file_path.replace('\\','/'))
    file_path = file_path.replace('\\','/')
    print(file_path)
    data = 'LOAD DATA LOCAL INFILE \'' + file_path + '\'REPLACE INTO TABLE ' + table_name + \
           ' CHARACTER SET UTF8 FIELDS TERMINATED BY \',\' ENCLOSED BY \'\"\' LINES TERMINATED BY \'\n\' IGNORE 1 LINES;'
    cur.execute(create_table_sql)
    cur.execute(data.encode('utf8'))
    # cur.execute(data)
    print(cur.rowcount)
    con.commit()

# 读取某个文件夹下的所有文件
def eachFile(path):
    pathDir =os.listdir(path)
    pathFile=[]
    for allDir in pathDir:
        child = os.path.join(path, allDir)
        tmp={}
        tmp[ 'fulldir' ]=child
        tmp [ 'dirname' ],tmp[ 'filename' ]=os.path.split(child)
        tmp[ 'fname' ],tmp [ 'fename' ]=os.path.splitext(tmp[ 'filename' ])
        pathFile.append(tmp)
    return pathFile

# 从数据库读出的dataframe每行的最后一列数据会带有\r，将这个换行符删去
def clear_changeRow(df):
    name = list(df.columns)
    change_data = name[-1]
    for i in range(len(df)):
        df[change_data][i]=df[change_data][i].replace('\r','')
    # print(df.head())
    return df

# 将数据库内的每个表的数据读出存为dataframe，每个数据的类型均为字符串
def read_table(tablename):
    con = pymysql.connect(user="root",
                          passwd="mysql123456.",
                          db="labor",
                          host="81.68.227.116",
                          port=3306,
                          local_infile=1,
                          )
    con.set_charset('utf8')
    cur = con.cursor()

    try:
        sql = "select * from "+tablename
        cur.execute(sql)
        result = cur.fetchall()
        cols = cur.description
        col = []
        for i in cols:
            col.append(i[0])
    finally:
        con.close();
    df = pd.DataFrame(result,columns=col)#转换成DataFrame格式
    df = clear_changeRow(df)
    return df

if __name__ == '__main__':

    # print(read_table('flow_data').to_dict())
    con = pymysql.connect(user="root",
                          passwd="",
                          db="bili",
                          host="127.0.0.1",
                          port=3306,
                          local_infile=1,
                          )
    con.set_charset('utf8')
    cur = con.cursor()
    fileList=eachFile('F:\data_b\校园学习')
    print(fileList)
    for file in fileList:
        table_name = file['filename'][:-4]
        print(file['fulldir'])
        # print(table_name)
        write_database(con,cur,file['fulldir'],table_name)

    sqlhelper = default_sqlhelper

    # res = sqlhelper.fetch_all("select * from user")

    # sqlhelper.delete("delete from visitor where id > %s", 1)

    # sqlhelper.insert_one("insert into user VALUES (%s,%s)",("jinwangba",4))

    # sqlhelper.update("update user SET name=%s WHERE  id=%s",("yinwangba",1))

    # print(res)