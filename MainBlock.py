'''
* Copyright (c) time,通软软件实验中心
* All right reserved.
*
* 文件名称：MainBlock.py
* 文件标识：
* 摘   要：包含各个小模块的结构体
*
* 当前版本:1.0
* 作   者:方世杰
* 完成日:
*
'''

# 主界面结构体
class MainBlock:
    
    '''
        支持有参构造、默认构造
    '''
    def __init__(self):

        self.__AQI_dict = {1:"优", 2:"良", 3:"轻度污染", 4:"中度污染", 5:"重度污染", 6:"严重污染", 0:"没有数据"} 

    '''唯一接口'''
    def GetJson(self,data):
        json_data = []
        json_data.append(self.__AQI_dict[data[0]+1])
        json_data.append(str(data[0]))
        json_data.append(data[1])
        json_data.append(str(data[2]))
        json_data.append(str(data[3]))
        return json_data

# 可视化模块
class Visualization:

    '''初始化可视化界面'''
    def __init__(self, AQI_arr=[], main_arr=[[],[]]):
        
        self.AQI_arr = AQI_arr
        self.main_arr = main_arr
        

    '''主要污染物数据'''
    def GetJson(self):
        json_data = []
        json_data.append("AQI:"+str(self.AQI_arr))
        json_data.append("main:"+str(self.main_arr))
        return json_data

if __name__ == "__main__":

    pass