# coding=utf-8
import socketio
# import json
import requests
import re
import logging
import time
import pymongo
import random
import base64
# from api import *

# import socket
'''
Python插件SDK Ver 0.0.2
维护者:enjoy(2435932516)
有问题联系我。
'''


webapi = "http://10.1.1.169:8888"  # Webapi接口 http://127.0.0.1:8888
robotqq = ""  # 机器人QQ号


# -----------------------------------------------------
api = webapi + '/v1/LuaApiCaller'
refreshapi = webapi + '/v1/RefreshKeys'
sio = socketio.Client()
# log文件处理
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=0,
                    filename='new.log', filemode='a')
Luaapi = api + "/v1/LuaApiCaller"
try:
    myclient = pymongo.MongoClient("mongodb://10.1.1.116:27017/")
    print('连接成功~')
except:
    print('连接失败~')
mydb = myclient["setu_test"]
mycol = mydb["test2"]
class GMess:
    # QQ群消息类型
    def __init__(self, message1):
        # print(message1)
        self.FromQQG = message1['FromGroupId']  # 来源QQ群
        self.QQGName = message1['FromGroupName']  # 来源QQ群昵称
        self.FromQQ = message1['FromUserId']  # 来源QQ
        self.FromQQName = message1['FromNickName']  # 来源QQ名称
        self.Content = message1['Content']  # 消息内容


class Mess:
    def __init__(self, message1):
        self.FromQQ = message1['ToUin']
        self.ToQQ = message1['FromUin']
        self.Content = message1['Content']
        try:
            self.FromQQG = message1['TempUin']
        except:
            self.FromQQG = 0


# standard Python

# SocketIO Client
# sio = socketio.AsyncClient(logger=True, engineio_logger=True)

# -----------------------------------------------------
# Socketio
# -----------------------------------------------------
def refreshkey():
    params = {'qq': robotqq}
    res = requests.get(refreshapi, params=params)
    print(res.text)


def base_64(filename):
    with open('F:\\pixiv\\test'+'\\'+filename, 'rb') as f:
        coding = str(base64.b64encode(f.read()), 'utf8')  # 读取文件内容，转换为base64编码
        return coding

def setu(r18, keyword=""):
    print(keyword)
    data_re = re.compile(keyword)
    tmp = mycol.find({"$and": [{'tags': data_re}, {'R18': r18}]})
    setus = list(tmp)
    setus_num = len(setus)
    print(setus_num)
    if setus_num != 0:
        num = random.randint(0, (setus_num - 1))
        setu = setus[num]
        title = setu['title']
        author = setu['author']
        artworkid = setu['artwork']
        artistid = setu['artist']
        purl = "www.pixiv.net/artworks/" + str(artworkid)  # 拼凑p站链接
        uurl = "www.pixiv.net/users/" + str(artistid)  # 画师的p站链接
        msg = title + "\r\n" + purl + "\r\n" + author + "\r\n" + uurl
        print(msg)
        base64code = base_64(setu['filename'][0])
        return msg, base64code
    else:
        return

def send_text(toid, type, msg, groupid, atuser):
    params = {'qq': robotqq,
              'funcname': 'SendMsg'}
    data = {"toUser": toid,
            "sendToType": type,
            "sendMsgType": "TextMsg",
            "content": msg,
            "groupid": groupid,
            "atUser": atuser}
    requests.post(api, params=params, json=data)


def send_pic(toid, type, msg, groupid, atuser, picurl='', picbase64='', picmd5=''):
    params = {'qq': robotqq,
              'funcname': 'SendMsg'}
    data = {"toUser": toid,
            "sendToType": type,
            "sendMsgType": "PicMsg",
            "content": msg,
            "groupid": groupid,
            "atUser": atuser,
            "picUrl": picurl,
            "picBase64Buf": picbase64,
            "fileMd5": picmd5}
    requests.post(api, params=params, json=data, timeout=30)
    print(data)


def beat():
    while (1):
        sio.emit('GetWebConn', robotqq)
        time.sleep(60)



@sio.event
def connect():
    print('connected to server')
    sio.emit('GetWebConn', robotqq)  # 取得当前已经登录的QQ链接
    beat()  # 心跳包，保持对服务器的连接


@sio.on('OnGroupMsgs')
def OnGroupMsgs(message):
    ''' 监听群组消息'''
    tmp = message['CurrentPacket']['Data']
    # print(tmp)
    a = GMess(tmp)
    # cm = a.Content.split(' ',3) #分割命令
    '''
    a.FrQQ 消息来源
    a.QQGName 来源QQ群昵称
    a.FromQQG 来源QQ群
    a.FromNickName 来源QQ昵称
    a.Content 消息内容
    '''
    print('群聊:', a.Content)
    keyword = re.match(r'来[点丶张](.*?)的{0,1}色图', a.Content)  # 瞎写的正则
    if keyword:
        keyword = keyword.group(1)
        data = setu(False, keyword)
        msg = data[0]
        picurl = data[1]
        send_text(a.FromQQG, 2, '', 0, a.FromQQ)
        send_pic(a.FromQQG, 2, msg, a.FromQQ, a.FromQQ, picbase64=picurl)
        print('已发送~')
        return

    # te = re.search(r'\#(.*)', str(a.Content))
    # if te == None:
    #     # print('???')
    #     return


@sio.on('OnFriendMsgs')
def OnFriendMsgs(message):
    ''' 监听好友消息 '''
    tmp = message['CurrentPacket']['Data']
    a = Mess(tmp)
    # print(tmp)
    # cm = a.Content.split(' ')
    print('好友:', a.Content)
    keyword = re.match(r'来[点丶张](.*?)的{0,1}色图', a.Content)  # 瞎写的正则
    if keyword:
        keyword = keyword.group(1)
        data = setu(True, keyword)
        msg = data[0]
        picurl = data[1]
        send_text(a.FromQQG, 2, '', 0, a.FromQQ)
        send_pic(a.ToQQ, 3, msg, a.FromQQG, 0, picbase64=picurl)
        print('已发送~')
        return


@sio.on('OnEvents')
def OnEvents(message):
    ''' 监听相关事件'''
    print(message)


# -----------------------------------------------------

def main():
    try:
        sio.connect(webapi, transports=['websocket'])
        # pdb.set_trace() 这是断点
        sio.wait()
    except BaseException as e:
        logging.info(e)
        print(e)


if __name__ == '__main__':
    # refreshkey()
    main()
