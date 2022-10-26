
'''
服务端类TcpServer,DataAir数据类说明:
    1. 作为服务端监听串口,tcpServer.tcpInit('192.168.1.1',7070) 实际为7080端口\
                        tcpServer.tcpBind() \
                        tcpServer.Listen() 
    2. 有连接(SAP)则返回客户端的fd以及地址信息,fd_client,addr_client = tcpServer.tcpAccept()
    3. 接受数据,recvData = tcpServer.tcpSend()
    4. 创建DataAir类,dataAir = DataAir(recvData.decode())    此处套接字接受的为python Bytes类型, 调用decode()方法转为str
    5. 获取数据字典 dict = dataAir.getData()
    6. 关闭客户端套接字,释放设备描述符 tcpServer.tcpClose(fd_client),此处不释放下次连接会出问题,服务端socket写到析构函数中,不用考虑    
'''

from socket import *
import time

class DataAir:  
    def __init__(self,str_data):

        if "" == str_data:
            print("结束")
            return ""

        print(str_data)

        self.AQI_list = {'o3':48,'so2':64,'no2':46,'pm10':0,'pm25':0}   #六参
        self.EPS = 0.00001
        self.result = {}

        #获取数据
        res = str_data.split(",")
        for i in res:
            name,value = i.split(":")
            #数据判断
            if float(value) + 999 < self.EPS:
                self.result[name] = 0.0
            elif name in self.AQI_list.keys():
                self.result[name] = self.unit(float(value), self.AQI_list[name])
            elif name == 'co':
                self.result[name] = self.unit(float(value)/1000,28)
            else:
                self.result[name] = float(value)
        
    def unit(self,value, M, T = 25, P = 101325):
        return value*(M/22.4)*(273.15/(273.15+T)*P/101325)


class TcpServer:

    #初始化
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.fd_lan = -1

    #初始化监听套接字
    def tcpInit(self):
        self.fd_lan = socket(AF_INET,SOCK_STREAM)
        self.fd_lan.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)

    #绑定
    def tcpBind(self):
        address = (self.ip , self.port)
        self.fd_lan.bind(address)

    #监听    
    def tcpListen(self):
        self.fd_lan.listen(30)

    #返回连接得客户端
    def tcpAccept(self):
        print("accept……")
        fd_client,client_addr = self.fd_lan.accept()
        return fd_client,client_addr

    #接受数据
    def tcpRecv(self,fd_client):
        recv_data = fd_client.recv(1024)
        return recv_data

     #关闭套接字
    def tcpClose(self,fd_client):
        fd_client.close()

if __name__ == "__main__":

    str_data ="co:-999.000000,02:-999.000000,ch4:-999.000000,o3:-999.000000,h2s:-999.000000,so2:-999.000000,nh3:-999.000000,no2:-999.000000,No:-999.000000,pm1:-999.000000,pm10:-999.000000,pm25:-999.000000,humid:-999.000000,temper:-999.000000,co2:-999.000000"
    data = DataAir(str_data)
    print(data.result)
    c = TcpServer('192.168.8.1',9989)
    c.tcpInit()
    c.tcpBind()
    c.tcpListen()
    fd_client,client_addr = c.tcpAccept()

    i= 0 
    while i<200:

        recv_data = c.tcpRecv(fd_client) 
        print(DataAir(recv_data.decode()).result)
        time.sleep(0.5)
        i+=1
        print(i)
    c.tcpClose(fd_client)



