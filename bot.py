import socketio
import requests
import re
import logging
import time
import pymongo
import random
import base64
'''
写的很乱
大概就是本地库中找不到图的话就会去api找

'''

color_pickey = ''  # 申请地址api.lolicon.app
size1200 = 'true'  # 是否使用 master_1200 缩略图，即长或宽最大为1200px的缩略图，以节省流量或提升加载速度（某些原图的大小可以达到十几MB）
webapi = "http://10.1.1.169:8888"  # Webapi接口 http://127.0.0.1:8888
robotqq = ""  # 机器人QQ号
path = 'Y:\\PICS' #本地图片路径
'''
下面是数据库部分
'''
try:
    myclient = pymongo.MongoClient("mongodb://10.1.1.142:27017/")
    print('连接成功~')
except:
    print('连接失败~')
mydb = myclient["setu"]
mycol = mydb["setu_1"]
# -----------------------------------------------------
api = webapi + '/v1/LuaApiCaller'
refreshapi = webapi + '/v1/RefreshKeys'
sio = socketio.Client()
# log文件处理
logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=0,
                    filename='new.log', filemode='a')
Luaapi = api + "/v1/LuaApiCaller"



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



def refreshkey():
    params = {'qq': robotqq}
    res = requests.get(refreshapi, params=params)
    print(res.text)


def base_64(filename):
    with open(path + '\\' + filename, 'rb') as f:
        coding = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        # code = str(coding, 'utf8')
        # print(coding)
        # print(code)
        return coding.decode()


def color_pic(r18, keyword=''):
    url = 'https://api.lolicon.app/setu/'
    params = {'r18': r18,
              'apikey': color_pickey,
              'keyword': keyword,
              'size1200': size1200,
              'proxy': 'i.pixiv.cat'}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36 Edg/81.0.416.53',
    }
    try:
        res = requests.get(url, headers=headers, params=params, timeout=8)
        data = res.json()  # 转换成字典
        picurl = data['data'][0]['url']  # 提取图片链接
        author = data['data'][0]['author']  # 提取作者名字
        title = data['data'][0]['title']  # 图片标题
        purl = 'www.pixiv.net/artworks/' + str(data['data'][0]['pid'])  # 拼凑p站链接
        uurl = 'www.pixiv.net/users/' + str(data['data'][0]['uid'])  # 画师的p站链接
        msg = title + '\r\n' + purl + '\r\n' + author + '\r\n' + uurl  # 组合消息
        return msg, picurl
    except IndexError:
        picurl = 'https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/error.jpg'
        return '你的xp好奇怪啊,爪巴', picurl
    except Exception as error:
        print(error)
        picurl = 'https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/error.jpg'
        return '服务器可能挂掉了' + '\r\n' + str(error), picurl  # 出错了就返回固定值.....


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
        return msg, '', base64code
    else:
        url = 'https://api.lolicon.app/setu/'
        params = {'r18': r18,
                  'apikey': color_pickey,
                  'keyword': keyword,
                  'size1200': size1200,
                  'proxy': 'i.pixiv.cat'}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36 Edg/81.0.416.53',
        }
        errpicurl = "https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/error.jpg"
        try:
            res = requests.get(url, headers=headers, params=params, timeout=8)
            data = res.json()  # 转换成字典
            if data["code"] == 404:
                return "你的xp好奇怪啊 爪巴", errpicurl, ''
            elif data["code"] == 429:
                return "今天的色图发完了 爪巴", errpicurl, ''
            picurl = data['data'][0]['url']  # 提取图片链接
            author = data['data'][0]['author']  # 提取作者名字
            title = data['data'][0]['title']  # 图片标题
            purl = 'www.pixiv.net/artworks/' + str(data['data'][0]['pid'])  # 拼凑p站链接
            uurl = 'www.pixiv.net/users/' + str(data['data'][0]['uid'])  # 画师的p站链接
            msg = title + '\r\n' + purl + '\r\n' + author + '\r\n' + uurl  # 组合消息
            return msg, picurl, ''
        except Exception:
            return '服务器可能挂掉了', errpicurl, ''  # 出错了就返回固定值.....


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
        code = data[2]
        send_text(a.FromQQG, 2, '', 0, a.FromQQ)
        send_pic(a.FromQQG, 2, msg, a.FromQQ, a.FromQQ, picurl, picbase64=code)
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
