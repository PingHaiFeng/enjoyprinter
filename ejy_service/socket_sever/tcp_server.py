import sys,os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # __file__获取执行文件相对路径，整行为取上一级的上一级目录
sys.path.append(BASE_DIR)
import ast
import json
import socket  # 导入 socket 模块
import time
from threading import Thread
import requests

from plugins.redis_serve import r

socket_mapping = {} # 设置一个字典，用来保存每一个客户端的连接 和 身份信息
sever = socket.socket()  # 创建 socket 对象
host = "172.16.0.2"  # 获取本地主机名
port = 5301  # 设置端口
sever.bind((host, port))  # 绑定端口
sever.listen(500)  # 监听连接,传入连接请求的最大数

def startServer():
    while True:
        try:
            sc, addr = sever.accept()  # 建立客户端连接
            Thread(target=recieve, args=(sc,addr)).start()# 为每一个客户端开启一个线程、保证程序的高效运行
            time.sleep(0.5)
            print("====")
        except Exception as e :
            print("出现错误一次",e)
            continue
def recieve(sc,addr):
    while True:
        instruct_data = sc.recv(1024*1024).decode('utf-8')
        host_ip = addr[0]
        time.sleep(1)
        print(instruct_data)
        if instruct_data:
            try:
                instruct_data=ast.literal_eval(instruct_data)
                if instruct_data['instruct_id']!=1001:
                    Thread(target=parse, args=(sc, socket_mapping,host_ip,instruct_data)).start()# 为每一个客户端开启一个线程、保证程序的高效运行
            except Exception as e :
                print("出现错误：",e)
                continue
        else:
            startServer()
def save_host_ip(token,host_ip):
    url = "http://localhost:5300/pc/save_host_ip"
    data = {
        "token":token,
        "host_ip":host_ip
    }
    res = requests.post(url=url,data=data).text
    return res

'''
1001 —— 服务端询问客户端是否在线指令
1002 —— 服务端发送客户端打印指令
2001 —— 客户端登陆获取Token请求
2002 —— 客户端响应数据反馈
2003 —— 客户端传送设备、营业信息
2004 —— 客户端心跳包
'''
def parse(sc,socket_mapping,host_ip,instruct_data):
# 1代表服务端 2代表客户端 3代表TCP中转站 4代表小程序


    try:
        socket_mapping[host_ip] = sc
        local_client_socket = socket_mapping[host_ip]
        instruct_id=instruct_data['instruct_id']

        if instruct_id==2001:  #2001 pc端联机请求
            
            token=instruct_data["instruct_dict"]["token"]
            store_id=instruct_data["instruct_dict"]["store_id"]
            save_host_ip(token,host_ip)
            print("pc端（{}）联机成功".format(host_ip))
            r.set("ONLINE_STATE_"+store_id,"Y",60)

        if instruct_id==2002:  #2002 pc端响应打印反馈
            pass

        if instruct_id==2003:  #2003 pc端传输打印机等信息
           instruct_dict=instruct_data['instruct_dict']
        #    default_printer =instruct_dict["default_printer"]
           print("pc端传输打印机等信息")

        if instruct_id==2004: #2004 pc端心跳包
            print("收到心跳包")
            store_id=instruct_data['instruct_dict']["store_id"]
            r.set("ONLINE_STATE_"+store_id,"Y",60)

        if instruct_id==3002:  #3002 中转站打印请求
            print("发送指令")
            try:
                instruct_data['instruct_id']=1002
                goal_ip=instruct_data["instruct_dict"]["goal_ip"] #目标ip地址
                goal_client_socket = socket_mapping[goal_ip]
                goal_client_socket.send(json.dumps(instruct_data).encode('utf-8'))
                data={"take_id":instruct_data["instruct_dict"]["take_id"]}
                res={"state":1,"msg":"发送成功","data":data}
                print("成功发送")
            except KeyError:
                res={"state":0,"msg":"该店铺账号未登陆"}
                print("发送失败，该店铺账号未登陆")
            except ConnectionResetError:
                res={"state":0,"msg":"该店铺账号强行下线关闭"}
                print("发送失败,该店铺账号强行下线关闭")
            local_client_socket.send(json.dumps(res).encode('utf-8'))

        # if instruct_id==4001:# 4001小程序询问商家端是否在线请求
        #     try:
        #         instruct_data['instruct_id']=1001
        #         goal_ip=instruct_data["instruct_dict"]["goal_ip"] #目标ip地址
        #         goal_client_socket = socket_mapping[goal_ip]
        #         goal_client_socket.send(json.dumps(instruct_data).encode('utf-8'))
        #         res={"state":1,"msg":"目标店铺在线"}
        #         print("成功发送")
        #     except KeyError:
        #         res={"state":0,"msg":"该店铺账号未登陆"}
        #         print("发送失败，该店铺账号未登陆")
        #     except ConnectionResetError:
        #         res={"state":0,"msg":"该店铺账号强行下线关闭"}
        #         print("发送失败,该店铺账号强行下线关闭")
        #     except ConnectionAbortedError:
        #         res={"state":0,"msg":"主机终止了连接"}
        #     local_client_socket.send(json.dumps(res).encode('utf-8'))
          
    except KeyError:
        raise



if __name__ =="__main__":
    startServer()
