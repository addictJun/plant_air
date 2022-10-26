import json
from flask import Flask, render_template, request
from pip import main
from MainBlock import MainBlock,Visualization    #主要的显示模块
from manager import Manager
from data_mysql import DataMysql
from Server import DataAir,TcpServer
from flask import jsonify


app = Flask(__name__,template_folder="templates")
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

#全局变量
class_list = [MainBlock(),Visualization()]
manager = Manager(app=app,
                class_list=class_list,
                data_mysql=DataMysql(),
                TcpServer=TcpServer('192.168.8.1',9989))  #只需要一行代码


#更新传感器参数
@app.route('/update', methods=['POST'])
def update():
    result = {}
    if request.method == 'POST':
        data = eval(request.get_data())
        result = manager.GetJson(int(data['flag']))   #调用接口
    return result

#获取前端页面
@app.route('/', methods=['GET', 'POST'])
def index():

    return render_template('index.html')

if __name__== '__main__':

    manager.run(host='0.0.0.0',port= 8080,debug= True)

