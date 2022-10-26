'''
* Copyright (c) time,通软软件实验中心
* All right reserved.
*
* 文件名称：
* 文件标识：
* 摘   要：数据库的抽象类，包含连接，关闭，判断表格是否存在，表格的删除等基础操作
*
* 当前版本：1.0
* 作   者：方世杰
* 完成日期：2022.9.22
*
'''
from sqlite3 import Cursor
import pymysql


class Mysql:

    '''用户名，密码，主机地址'''
    def __init__(self,host="127.0.0.1", user='root', password="root", db="data", port=3306, charset = "utf8mb4"):
        #获取基础信息
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self.conn = None     #连接
        self.cursor = None   #数据库操作游标
        self.sql = ""  #查询语句

    '''连接数据库'''
    def Connect(self):
        self.conn = pymysql.connect(host = self.host,
                                    port = self.port,
                                    user = self.user,
                                    password = self.password,
                                    database = self.db,
                                    charset = self.charset)
        if self.conn != None:
            print("连接数据库，成功")
            self.cursor = self.conn.cursor()
        else:
            print("连接数据库，失败")

    '''关闭连接'''
    def Close(self):
        if self.cursor != None:
            self.cursor.close()
        if self.conn != None:
            self.conn.close()
        self.conn = None
        self.cursor = None
        print("关闭数据库，成功")

    '''查询该表是否存在'''
    def FindTable(self, name):
        if self.conn == None:
            self.Connect()
        sql = "show tables"
        self.SqlExecute(sql)
        row = self.cursor.fetchone()
        while row is not None:
            if row[0] == name:
                self.Close()  
                return 1
            row = self.cursor.fetchone()
        self.Close()  
        return 0

    '''执行sql语句'''
    def SqlExecute(self, sql):
        try:
            if self.conn != None:
                self.cursor.execute(sql)
            else:
                self.Connect()
                self.cursor.execute(sql)
            self.conn.commit()
            print(f"{sql} : 执行成功")
            return 1
        except:
            print(f"{sql} : 执行失败")
            return 0

    '''获取表的字段名'''
    def GetTableColumn(self,table_name):

        sql = "show columns from " + table_name
        self.SqlExecute(sql)
        row = self.cursor.fetchone()
        res = []
        while row is not None:
            res.append(row[0])
            row = self.cursor.fetchone()
        self.Close()
        return res
    

if __name__== '__main__':

    mysql = Mysql()

    #链接
    mysql.Connect()

    #创建表格
    sql = """CREATE TABLE test1(TIME CHAR(20) not null primary key,
                                PM25 float,
                                PM10 float,
                                SO2 float,
                                CO float,
                                NO2 float,
                                O3 float)"""
    if 1 == mysql.SqlExecute(sql):
        print("创建成功")
        mysql.Close()
    else:
        print("创建失败")
    

    #查询表格
    print("*"*20 + "下一步" + "*"*20)
    if 0 == mysql.FindTable("test"):
        print("没有找到")
    else:
        print("找到该表")

    #查询表格
    print("*"*20 + "下一步" + "*"*20)
    if 0 == mysql.FindTable("test1"):
        print("没有找到")
    else:
        print("找到该表")

    print("*"*20 + "下一步" + "*"*20)
    print(mysql.GetTableColumn("test1"))
   