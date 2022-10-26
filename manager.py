
import pandas as pd
import numpy as np
import threading
from data_mysql import DataMysql
from Server import DataAir,TcpServer
import time

from mysql import Mysql

class Manager():

    '''初始化'''
    def __init__(self,class_list=[],app=None,TcpServer=None,data_mysql=None):
        super(Manager, self).__init__()

        # 1.初始化变量
        self.mysql = data_mysql   #数据库管理
        self.app = app    #线程2
        self.tcp_server = TcpServer #服务器
        self.class_list = class_list  #线程1
        self.thread_list = {}   #线程管理
        self.thread_dict = {}
        self.id = 0
        
    '''开炮'''
    def run(self,host,port,debug):
        self.__AddThread(self.__Database)    # 1.创建数据库线程的管理
        self.__AddThread(self.__Datamanager)    # 2.管理守护线程
        self.__FrontEnd(host,port,debug) # 3.前端运行

        '''前端运行'''
    def __FrontEnd(self,host,port,debug):
        if None == self.app:
            print("this is a test program")
            while(1):
                time.sleep(10)
        else:
            self.app.run(host=host,port= port,debug= debug)
        
    '''传输数据'''
    def __Database(self):
        if None == self.tcp_server:
            print("请设置tcp服务器")
            return
        self.tcp_server.tcpInit()
        self.tcp_server.tcpBind()
        self.tcp_server.tcpListen()
        fd_client,client_addr = self.tcp_server.tcpAccept()
        while(1):
            recv_data = self.tcp_server.tcpRecv(fd_client)
            print("recv_data:",recv_data)
            if b"" == recv_data:
                break
            print(DataAir(recv_data.decode()).result)
            self.mysql.StorageHourData(DataAir(recv_data.decode()).result)
        self.tcp_server(fd_client)

    '''线程管理'''
    def __Datamanager(self):
        while(1):
            # 检索线程
            keys = []
            for i,t in self.thread_list.items():
                print(i,t.name)
                if t.is_alive():
                    print(t.name + "is alive")
                else:
                    print(t.name + "is fail, start again……")
                    self.thread_list[i] = threading.Thread(target=self.thread_dict[i],daemon=True)
                    self.thread_list[i].start()
            time.sleep(5) #定时监测

    '''前端交互'''
    def GetJson(self,flag):
        if 1 == flag:   #传感器数据
            return self.__GetJsonSensor()
        elif 2 == flag:  #主界面数据
            return self.__GetJsonMain()
        elif 3 == flag:   #AQI可视化
            return self.__GetJsonAQI()
        elif 4 == flag:   #主要污染物
            return self.__GetJsonPoll()
        elif 0 == flag:  #全部数据
            return self.__GetAllJson()
        
    '''传感器数据'''
    def __GetJsonSensor(self):
        return self.mysql.FindMaxData()

    '''AQI可视化数据'''
    def __GetJsonAQI(self):
        return self.mysql.FindAQIData()

    '''主要污染物'''
    def __GetJsonPoll(self):
        return self.mysql.FindPollData()

    '''主界面数据'''
    def __GetJsonMain(self):
        return self.class_list[0].GetJson(self.mysql.FindMainData())

    """all数据"""
    def __GetAllJson(self):
        res = self.mysql.FindVisData()
        res['sensor'] = self.mysql.FindMaxData()
        print("*"*25 + "传感器数据" + "*"*25)
        print(res['sensor'])
        res['main'] = self.class_list[0].GetJson(self.mysql.FindMainData())
        return res

    '''添加线程'''
    def __AddThread(self,run):
        t = threading.Thread(target=run,daemon=True)  # 设置为守护进程
        self.id += 1
        self.thread_list[self.id] = t
        self.thread_dict[self.id] = run
        t.start()
    '''重启线程'''
    def __AgainThread(self, run):
        self.thread_list[self.id] = threading.Thread(target=run,daemon=True)
        self.thread_dict[self.id] = run
        self.thread_list[self.id].start()

if __name__== '__main__':

    manager = Manager(data_mysql=DataMysql(),
            TcpServer=TcpServer('192.168.8.1',9989))

    manager.run(host='0.0.0.0',port= 8080,debug= True)