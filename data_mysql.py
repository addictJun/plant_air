from msilib.schema import InstallUISequence

from pymysql import TIME
from mysql import Mysql
import pandas as pd
import numpy as np
import time

class DataMysql(Mysql):

    '''初始化'''
    def __init__(self):
        super(DataMysql, self).__init__()
        self.hours_columns = ['TIME','pm25','pm10','so2','co','no2','o3','o2','co2','ch4','h2s','humid','temper']
        self.aqi_cloumns = ['TIME','aqi','pm25','pm10','so2','co','no2','o3']
        self.can6_cloumns = ['pm25','pm10','so2','co','no2','o3']
        self.IAQI = [0,50,100,150,200,300,400,500]
        self.canshu = {'so2':[0,150,500,650,800,1600,2100,2620],
                       'o3':[0,160,200,300,400,800,1000,1200],
                       'no2':[0,100,200,700,1200,2340,3090,3840],
                       'co':[0,5,10,35,60,90,120,150],
                       'pm25':[0,35,75,115,150,250,350,500],
                       'pm10':[0,50,150,250,350,420,500,600]}
        self.now_time = self.__GetTime()
        self.__ClearHoursData()  #清楚上次数据的缓存

    '''存储小时数据'''
    def StorageHourData(self,data):
        current_time = self.__GetTime()
        if self.now_time == current_time:
            self.__StorageData(data)
        else:
            self.now_time = current_time #赋值
            self.__StorageAQIData() #触发AQI表格
            self.__ClearHoursData() # 清空表格
            self.__StorageData(data) #存进新的数据
        #----------------测试阶段的代码-----------------
        print(self.__GetAllAQIData('aqi').tail())
        print(self.__GetAllData('hours').tail())

    '''读取hours数据'''
    def FindMaxData(self):
        sql = "SELECT * FROM hours ORDER BY id DESC LIMIT 1;"
        self.SqlExecute(sql)
        data=self.cursor.fetchone()
        self.Close()
        if None == data:
            return [-1 for i in range(len(self.hours_columns))]
        return list(data[2:])

    '''AQI数据'''
    def FindAQIData(self):
        res = []
        data = self.__GetAllAQIData('aqi') #获取全部的数据
        time_list = list(data['TIME'])
        for i in range(24):   #0-23
            if i not in time_list:
                res.append(-1)
            else:
                res.append(int(data[data['TIME']==float(i)]['aqi']))
        return res

    '''找到主要污染物'''
    def FindPollData(self):
        res = []
        data = self.__GetAllAQIData('aqi') #获取全部的数据
        max_poll = data.drop(['TIME',"aqi"],axis=1).copy()
        time_list = list(data['TIME'])
        for i in range(24):   #0-23
            if i not in time_list:
                res.append(-1)
            else:
                res.append(int(data[data['TIME']==float(i)][max_poll.mean().idxmax()]))
        result= {
            "name":max_poll.mean().idxmax(),
            "data":res
        }
        return result

    '''提取主界面'''
    def FindMainData(self):
        res = []
        data1 = self.__GetAllAQIData('aqi')
        data2 = self.FindMaxData()
        res.append(self.__GetAqiRank(data1.mean().loc['aqi']))
        res.append(data1.drop(['TIME',"aqi"],axis=1).mean().idxmax())
        res.append(data2[-2])
        res.append(data2[-1])
        return res

    '''vis接口'''
    def FindVisData(self):
        res = {
            'aqi':[],
            'poll':[]
        }
        data = self.__GetAllAQIData('aqi') #获取全部的数据
        max_poll = data.drop(['TIME',"aqi"],axis=1).copy()
        time_list = list(data['TIME'])
        for i in range(24):   #0-23
            if i not in time_list:
                res['aqi'].append(-1)
                res['poll'].append(-1)
            else:
                res['aqi'].append(int(data[data['TIME']==float(i)]['aqi']))
                res['poll'].append(int(data[data['TIME']==float(i)][max_poll.mean().idxmax()]))
        result = {
            'aqi':res['aqi'],
            'poll':{
                'name':max_poll.mean().idxmax(),
                'data':res['poll']
            }
        }
        return result

    '''清空小时表格'''
    def __ClearHoursData(self):
        sql = "delete from hours"
        self.SqlExecute(sql)
        self.Close()
    
    '''处理AQI数据'''
    def __StorageAQIData(self):
        data = self.__GetAllData("hours")#1. 获取属于AQI的全部数据
        if data.empty:
            return
        doucent_time = int(data['TIME'][0])
        Table = data.drop(['TIME'], axis = 1).mean()  #2. 计算平均值
        AQI_value = self.__GetAQI(Table.to_dict())    # 计算AQI
        res = (str(doucent_time),AQI_value,Table.loc['pm25'],Table.loc['pm10'],Table.loc['so2'],Table.loc['co'],Table.loc['no2'],Table.loc['o3'])
        self.__StorageAQI(res) # 存储

    '''计算AQI指标'''
    def __GetAQI(self,data):
        IAQI_list = [self.__GetIAQI(i,data[i]) for i in self.can6_cloumns]
        # print("IAQI_list",max(IAQI_list))
        return max(IAQI_list)

    '''存储AQI数据'''
    def __StorageAQI(self,res):
        if self.__IsTimeTable(res[0]):  #存在
            self.__UpdateAqi(res)
        else: #存在
            self.__InputAqi(res)

    '''更新数据'''
    def __UpdateAqi(self, res):
        sql = f"update aqi set aqi={res[1]},pm25={res[2]},pm10={res[3]},so2={res[4]},co={res[5]},no2={res[6]},o3={res[7]} where TIME={res[0]}"
        self.SqlExecute(sql)
        self.Close()

    '''插入aqi数据'''
    def __InputAqi(self,res):
        sql = "insert into aqi(TIME,aqi,pm25,pm10,so2,co,no2,o3) values"+str(res)
        self.SqlExecute(sql)
        self.Close()

    '''判断是否存在'''
    def __IsTimeTable(self,doc_time):
        sql = "select * from aqi where TIME = " + "\"" + str(doc_time) +  "\""
        self.SqlExecute(sql)
        Tables = self.cursor.fetchall()
        self.Close()
        if Tables:
            return 1
        else:
            return 0
        
    '''计算IAQI'''
    def __GetIAQI(self,name,value):
        index = self.__GetIaqiRank(name,value)
        IAQI = 0
        if index != 7:
            IAQI = ((self.IAQI[index+1]-self.IAQI[index])/(self.canshu[name][index+1]-self.canshu[name][index])) \
                    * (value - self.canshu[name][index]) + self.IAQI[index]
        else:
            IAQI = self.IAQI[index]
        # print("__GetIAQI",index, name, value,IAQI)
        return IAQI

    def __GetAqiRank(self,value):
        for i in range(len(self.IAQI)):
            if value >= self.IAQI[i]:
                index = i
            else:
                break
        return index

    '''计算等级'''
    def __GetIaqiRank(self,name,value):
        for i in range(len(self.canshu[name])):
            if value >= self.canshu[name][i]:
                index = i
            else:
                break
        return index

    '''获取表格全部数据'''
    def __GetAllData(self, table_name):
        sql = "select * from " + table_name
        data = np.empty((0, len(self.hours_columns)))
        if self.SqlExecute(sql):
            value = self.cursor.fetchone()
            if None == value:
                df = pd.DataFrame(columns=self.hours_columns, data=data)
                return df
        while value is not None:
            res = [[float(value[i]) for i in range(1,len(self.hours_columns)+1)]]
            data = np.append(data, res, axis=0)
            value = self.cursor.fetchone()
        df = pd.DataFrame(columns=self.hours_columns, data=data)
        return df

    '''获取表格全部数据'''
    def __GetAllAQIData(self, table_name):
        sql = "select * from " + table_name
        data = np.empty((0, len(self.aqi_cloumns)))
        if self.SqlExecute(sql):
            value = self.cursor.fetchone()
            if None == value:
                df = pd.DataFrame(columns=self.aqi_cloumns, data=data)
                return df
        while value is not None:
            res = [[float(value[i]) for i in range(0,len(self.aqi_cloumns))]]
            data = np.append(data, res, axis=0)
            value = self.cursor.fetchone()
        df = pd.DataFrame(columns=self.aqi_cloumns, data=data)
        return df

    '''存储数据'''
    def __StorageData(self,data):
        
        try:
            data['TIME'] = self.now_time
            res = (data['TIME'],self.__ToNum(data['pm25']),self.__ToNum(data['pm10']),self.__ToNum(data['so2']),self.__ToNum(data['co']),self.__ToNum(data['no2']), \
                    self.__ToNum(data['o3']),self.__ToNum(data['o2']),self.__ToNum(data['co2']),self.__ToNum(data['ch4']),self.__ToNum(data['h2s']),self.__ToNum(data['humid']), \
                        self.__ToNum(data['temper']))
        except KeyError:
            print("数据中没有该数据")
            return;
        sql = "insert into hours(TIME,pm25,pm10,so2,co,no2,o3,o2,co2,ch4,h2s,humid,temper) values"+str(res)
        self.SqlExecute(sql)
        self.Close()

    '''获取时间'''
    def __GetTime(self):
        return time.localtime(time.time())[3]

    """数据类型转换"""
    def __ToNum(self,val):
        return int(val*10)/10

if __name__ == "__main__":
    mysql = DataMysql()
    
    # #创建小时表
    # sql = """CREATE TABLE hours(id integer primary key auto_increment,
    #                             TIME CHAR(20),
    #                             pm25 float,
    #                             pm10 float,
    #                             so2 float,
    #                             co float,
    #                             no2 float,
    #                             o3 float,
    #                             o2 float,
    #                             co2 float,
    #                             ch4 float,
    #                             h2s float,
    #                             humid float,
    #                             temper float)"""
    # if 1 == mysql.SqlExecute(sql):
    #     print("创建成功")
    #     mysql.Close()
    # else:
    #     print("创建失败")

    # #创建AQI表
    # sql = """CREATE TABLE aqi( TIME CHAR(20) not null primary key,
    #                             aqi float,
    #                             pm25 float,
    #                             pm10 float,
    #                             so2 float,
    #                             co float,
    #                             no2 float,
    #                             o3 float)"""
    # if 1 == mysql.SqlExecute(sql):
    #     print("创建成功")
    #     mysql.Close()
    # else:
    #     print("创建失败")

    data = {'co': 4.0, 'o2': 2.0, 'ch4': 3.0, 'o3': 0.0, 'h2s': 0.0, 'so2': 0.0, 'nh3': 0.0, 'no2': 4.0, 'no': 0.0, 'pm1': 0.0, 'pm10': 0.0, 'pm25': 0.0, 'humid': 0.0, 'temper': 0.0, 'co2': 0.0}
    mysql.StorageHourData(data)
    print(mysql.FindMaxData())
    print(mysql.FindAQIData())
    print(mysql.FindPollData())
    print(mysql.FindVisData())
    print(mysql.FindMainData())