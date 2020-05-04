import os
import re
import requests
import hashlib
import pymongo
import time
import json
import random
from datetime import datetime


with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    print('获取配置成功')
myclient = pymongo.MongoClient(config['mongodb'])  # 数据库地址
mydb = myclient[config['database']]  # 数据库
mycol = mydb[config['collection']]  # 集合
username = config['username']  # 账号
password = config['password']  # 密码

hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'
client_id = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
client_secret = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'


class Parsing:  # 处理信息
    def __init__(self, data):
        self.title = data['title']  # 标题
        self.author = re.sub(r'[@,＠].*$', '', data['user']['name'])  # 作者名,去掉@后面的字符
        self.artist = data['user']['id']  # 作者ID
        self.artwork = data['id']  # 作品ID
        tags = []
        for i in data['tags']:
            tags.append(i['name'])
            if i['translated_name'] != None:  # None就没有必要存了
                tags.append(i['translated_name'])
        self.tags = tags
        if 'R-18' in tags:
            self.R18 = True
        else:
            self.R18 = False
        if data['page_count'] == 1:  # 单页画册
            self.large = [data['image_urls']['large']]
            self.medium = [data['image_urls']['medium']]
            self.square_medium = [data['image_urls']['square_medium']]
            self.original = [data['meta_single_page']['original_image_url']]
            self.filename = [os.path.basename(data['meta_single_page']['original_image_url'])]
            self.page_count = 1
        else:  # 多页画册
            self.page_count = data['page_count']
            large, medium, square_medium, original, filename = [], [], [], [], []
            for i in data['meta_pages']:
                large.append(i['image_urls']['large'])
                medium.append(i['image_urls']['medium'])
                square_medium.append(i['image_urls']['square_medium'])
                original.append(i['image_urls']['original'])
                filename.append(os.path.basename(i['image_urls']['original']))
            self.large = large
            self.medium = medium
            self.square_medium = square_medium
            self.original = original
            self.filename = filename


def p_hash():
    local_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    Hash = hashlib.md5((local_time + hash_secret).encode('utf-8')).hexdigest()
    return local_time, Hash


def token(username, password):  # 登录
    url = 'https://oauth.secure.pixiv.net/auth/token'
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'password',
            'username': str(username),
            'password': str(password),
            'device_token': 'ead69eaa4d738f71b94c482785b2d6ef',
            'get_secure_url': 'true',
            'include_policy': 'true'}
    hash = p_hash()
    headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
               'Accept-Language': 'zh_CN',
               'App-OS': 'android',
               'App-OS-Version': '6.0.1',
               'App-Version': '5.0.191',
               'X-Client-Time': hash[0],
               'X-Client-Hash': hash[1],
               'Content-Type': 'application/x-www-form-urlencoded',
               'Host': 'oauth.secure.pixiv.net',
               'Connection': 'Keep-Alive',
               'Accept-Encoding': 'gzip', }
    res = requests.post(url, data=data, headers=headers)
    return res


def refresh_token():  # 刷新token
    url = 'https://oauth.secure.pixiv.net/auth/token'
    data = {'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': token['response']['refresh_token'],
            'device_token': 'ead69eaa4d738f71b94c482785b2d6ef',
            'get_secure_url': 'true',
            'include_policy': 'true'}
    hash = p_hash()
    headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
               'Accept-Language': 'zh_CN',
               'App-OS': 'android',
               'App-OS-Version': '6.0.1',
               'App-Version': '5.0.191',
               'X-Client-Time': hash[0],
               'X-Client-Hash': hash[1],
               'Content-Type': 'application/x-www-form-urlencoded',
               'Host': 'oauth.secure.pixiv.net',
               'Connection': 'Keep-Alive',
               'Accept-Encoding': 'gzip', }
    res = requests.post(url, data=data, headers=headers)
    return res


def favorites(userid):  # 读取收藏夹
    url = 'https://app-api.pixiv.net/v1/user/bookmarks/illust'
    params = {'user_id': userid,
              'restrict': 'public'}
    hash = p_hash()
    headers = {'Authorization': 'Bearer ' + token['response']['access_token'],
               'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
               'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
               'Accept-Language': 'zh_CN',
               'App-OS': 'android',
               'App-OS-Version': '6.0.1',
               'App-Version': '5.0.191',
               'X-Client-Time': hash[0],
               'X-Client-Hash': hash[1],
               'Host': 'app-api.pixiv.net',
               'Accept-Encoding': 'gzip'}
    res = requests.get(url, params=params, headers=headers)
    return res


def next_url(url):  # 用来处理nexturl
    hash = p_hash()
    headers = {'Authorization': 'Bearer ' + token['response']['access_token'],
               'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
               'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
               'Accept-Language': 'zh_CN',
               'App-OS': 'android',
               'App-OS-Version': '6.0.1',
               'App-Version': '5.0.191',
               'X-Client-Time': hash[0],
               'X-Client-Hash': hash[1],
               'Host': 'app-api.pixiv.net',
               'Accept-Encoding': 'gzip'}
    res = requests.get(url, headers=headers, timeout=5)
    return res.json()


def database(setu):
    if mycol.count_documents({'artwork': setu.artwork}) == False:  # 通过ID去重
        lastdata = mycol.find().sort('_id', -1).limit(1)  # 数据库的最后一条数据
        try:  # 数据库里没有数据会出错
            num = list(lastdata)[0]['_id'] + 1  # +1(_)
        except:  # 出错了就说明数据库没数据,那就从0开始
            num = 0
        setudict = {'_id': num, 'title': setu.title, 'artwork': setu.artwork, 'author': setu.author,
                    'artist': setu.artist, 'R18': setu.R18, 'page': setu.page_count, 'tags': setu.tags,
                    'filename': setu.filename, 'original': setu.original, 'large': setu.large, 'medium': setu.medium,
                    'square_medium': setu.square_medium}  # 拼凑字典..
        info = mycol.insert_one(setudict)  # 向数据库插入数据
        print(info.inserted_id)  # 打印_id
        return info  # 没什么意义的return
    else:
        print('已存在')
        return


try:
    with open('token.json', 'r', encoding='utf-8') as f:
        token = json.loads(f.read())
        print('获取token成功')
    print('尝试刷新token')
    token = refresh_token().json()
except:
    print('重新获取token')
    token = token(username, password).json()
finally:
    with open('token.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(token))
        print('保存token')

a = favorites(token['response']['user']['id']).json()  # 第一次进入收藏夹

data_num = len(list(mycol.find({})))

for i in a['illusts']:  # 轮询收藏夹的画册
    x = database(Parsing(i))  # 将处理过的数据写入数据库
while True:
    if a['next_url'] == None:  # 到最后一页就停止
        print('>>done<<')
        break
    a = next_url(a['next_url'])  # 翻页
    time.sleep(random.randint(4, 7))  # 休眠一下,不然会boom....
    for i in a['illusts']:  # 继续轮询
        y = database(Parsing(i))  # 将处理过的数据写入数据库

nowdata_num = len(list(mycol.find({})))
print('本次新增', nowdata_num - data_num, '条')
