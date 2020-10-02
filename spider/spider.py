import os
import re
import requests
import hashlib
import pymongo
import time
import json
import uuid
import random
from retrying import retry
from datetime import datetime

'''获取配置'''
with open('/root/download_setu/config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    print('获取配置成功')
myclient = pymongo.MongoClient(config['mongodb'])
mydb = myclient[config['database']]
mycol = mydb[config['collection']]
mycol_del = mydb[config['collection_del']]
mycol_update = mydb[config['collection_update']]
username = config['username']
password = config['password']
path = config['path']  # 下载路径
path_original = config['path_original']  # 下载路径

'''一些不知道什么东西'''
# hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'
# client_id = 'MOBrBDS8blbauoSck0ZfDbtuzpyT'
# client_secret = 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj'
# device_token = 'ead69eaa4d738f71b94c482785b2d6ef'


class Processed_data:
    def __init__(self, data):
        self.data_list = []  # 待插入的所有处理完的数据
        for illust in data['illusts']:  # 轮询所有插画
            if not illust['visible']:  # 如果作品不可见
                continue
            self.title = illust['title']  # 标题
            self.author = re.sub(r'[@,＠].*$', '', illust['user']['name'])  # 作者名,去掉@后面的字符
            self.artwork = illust['id']  # 作品ID
            self.artist = illust['user']['id']  # 作者ID
            # self.width = illust['width']  # 宽度
            # self.height = illust['height']  # 高度
            self.tags = []
            for tag in illust['tags']:  # 轮询tags
                self.tags.append(tag['name'])
                if tag['translated_name'] != None:  # None就没有必要存了
                    self.tags.append(tag['translated_name'])
            self.page = 0  # 第0P
            if illust['page_count'] == 1:  # 单页画册
                '''各种画质的链接'''
                self.large = illust['image_urls']['large']
                self.medium = illust['image_urls']['medium']
                self.square_medium = illust['image_urls']['square_medium']
                self.original = illust['meta_single_page']['original_image_url']
                self.filename = os.path.basename(illust['meta_single_page']['original_image_url'])
                self.append_data()
            else:  # 多页画册
                for urls in illust['meta_pages']:  # 轮询所有链接
                    self.large = urls['image_urls']['large']
                    self.medium = urls['image_urls']['medium']
                    self.square_medium = urls['image_urls']['square_medium']
                    self.original = urls['image_urls']['original']
                    self.filename = os.path.basename(urls['image_urls']['original'])
                    self.append_data()
                    self.page += 1

    def append_data(self):
        data_dict = {'title': self.title, 'artwork': self.artwork, 'author': self.author,
                     'artist': self.artist, 'page': self.page, 'tags': self.tags, 'type': None,  # 占位
                     'filename': self.filename, 'original': self.original, 'large': self.large, 'medium': self.medium,
                     'square_medium': self.square_medium}  # 拼凑字典..
        self.data_list.append(data_dict)


class PixivToken:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.device_token = uuid.uuid4().hex
        self.api = 'https://oauth.secure.pixiv.net/auth/token'

    def headers(self):
        hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'
        X_Client_Time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        X_Client_Hash = hashlib.md5((X_Client_Time + hash_secret).encode('utf-8')).hexdigest()
        headers = {'User-Agent': 'PixivAndroidApp/5.0.197 (Android 10; Redmi 8)',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Accept-Language': 'zh_CN_#Hans',
                   'App-OS': 'android',
                   'App-OS-Version': '10',
                   'App-Version': '5.0.197',
                   'X-Client-Time': X_Client_Time,
                   'X-Client-Hash': X_Client_Hash,
                   'Host': 'oauth.secure.pixiv.net',
                   'Accept-Encoding': 'gzip'}
        return headers

    def get_token(self):
        print('获取Pixiv_token~')
        data = {'client_id': 'MOBrBDS8blbauoSck0ZfDbtuzpyT',
                'client_secret': 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj',
                'grant_type': 'password',
                'username': self.username,
                'password': self.password,
                'device_token': self.device_token,
                'get_secure_url': 'true',
                'include_policy': 'true'}
        res = requests.post(url=self.api, data=data, headers=self.headers()).json()
        res['time'] = time.time()  # 记录时间
        return res

    def refresh_token(self, token):
        print('刷新Pixiv_token~')
        data = {'client_id': 'MOBrBDS8blbauoSck0ZfDbtuzpyT',
                'client_secret': 'lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj',
                'grant_type': 'refresh_token',
                'refresh_token': token,
                'device_token': self.device_token,
                'get_secure_url': 'true',
                'include_policy': 'true'}
        res = requests.post(url=self.api, data=data, headers=self.headers()).json()
        res['time'] = time.time()
        return res

    def if_refresh_token(self):
        global pixivid
        if time.time() - pixivid['time'] >= int(pixivid['expires_in']):  # 刷新
            pixivid = self.refresh_token(pixivid['refresh_token'])
            self.saveToken(pixivid)
        return

    def saveToken(self, data):
        with open('.Pixiv_Token.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
        print('PixivToken已保存到.Pixiv_Token.json')
        return


class Favorites:
    def __init__(self, token_data):
        self.userid = token_data['response']['user']['id']
        self.access_token = token_data['access_token']
        self.url = 'https://app-api.pixiv.net/v1/user/bookmarks/illust'
        self.params = {'user_id': self.userid,
                       'restrict': 'public'}

        self.headers = {'Authorization': 'Bearer ' + self.access_token,
                        'User-Agent': 'PixivAndroidApp/5.0.197 (Android 10; Redmi 8)',
                        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                        'Accept-Language': 'zh_CN_#Hans',
                        'App-OS': 'android',
                        'App-OS-Version': '10',
                        'App-Version': '5.0.197',
                        'X-Client-Time': None,  # 占位
                        'X-Client-Hash': None,  # 占位
                        'Host': 'app-api.pixiv.net',
                        'Accept-Encoding': 'gzip'}

    @retry(stop_max_attempt_number=5, wait_random_max=2000)
    def favorites(self):
        print("-" * 30)
        hash_secret = '28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c'
        local_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+08:00')
        Hash = hashlib.md5((local_time + hash_secret).encode('utf-8')).hexdigest()
        self.headers['X-Client-Time'] = local_time  # 更新
        self.headers['X-Client-Hash'] = Hash
        res = requests.get(url=self.url, params=self.params, headers=self.headers)
        return res.json()


class Favorites_next_url(Favorites):
    def __init__(self, token_data, next_url):
        super(Favorites_next_url, self).__init__(token_data)
        self.url = next_url
        self.params = {}


def remove_file(path, filename):
    if os.path.exists(path + filename):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(path + filename)
        print('删除{}'.format(filename))
    else:
        print('无文件:{}'.format(filename))  # 则返回文件不存在
    return


def database(collection, collection_del, data_list):
    data_for_del = []  # 待删除的数据
    for data in data_list:  # 去重与更新
        filename = data['filename']
        data_if_del = collection_del.find_one({'filename': filename})
        #       print(data_if_del)
        if data_if_del != None:  # 如果数据被删除过
            print('数据被删除过')
            data_for_del.append(data)  # 添加到待删除列表
            continue
        data_tmp = collection.find_one({'filename': filename})  # 查找是否有这条数据 (测试)
        if data_tmp != None:  # 表中有相同数据
            if data_tmp['original'] == data['original']:  # 如果数据表中数据和爬下来的一致
                print('数据一致')
                data_for_del.append(data)  # 添加到待删除列表
            else:
                print('不一致,删除')
                # result = collection.update_one({'filename': filename},
                #                                {'$set': data})  # 更新数据(filename是唯一的,直接覆盖掉除_id外的数据)  # 作者如果删P了的话没法删掉之前多出来的P
                #remove_file(path, filename)
                #remove_file(path_original, filename)
                result = collection.delete_many({'artwork': data['artwork']})  # 删除这个id的所有数据
                print("已删除{}条数据".format(result.deleted_count))
    for data_del in data_for_del:
        data_list.remove(data_del)  # 从待插入数据中删除
    if len(data_list) > 0:  # 如果待插入列表还有数据
        lastdata = collection.find().sort('_id', -1).limit(1)  # 数据库的最后一条数据
        try:  # 数据库里没有数据会出错
            num = list(lastdata)[0]['_id'] + 1  # 表中最后一条数据的_id加1
        except:  # 出错了就说明数据库没数据,那就从0开始
            num = 0
        for data_one in data_list:
            data_one['_id'] = num  # 给待插入的数据增加_id
            num += 1
        result = collection.insert_many(data_list)
        print('ID:{}'.format(result.inserted_ids))
    return


if __name__ == '__main__':
    data_num = len(list(mycol.find({})))  # 获取数据库当前有多少条数据
    '''token相关的'''
    pixiv = PixivToken(config['username'], config['password'])
    if os.path.isfile('.Pixiv_Token.json'):  # 有文件
        print('有Pixiv_Token文件 尝试载入~')
        try:
            with open('.Pixiv_Token.json', 'r', encoding='utf-8') as f:
                pixivid = json.loads(f.read())
        except:
            print('载入失败,请删除.Pixiv_Token.json重新登录~')
            sys.exit()
        pixiv.if_refresh_token()  # 判断刷新token
    else:
        print('无Pixiv_Token文件')
        pixivid = pixiv.get_token()
        if pixivid.get('has_error'):
            print('获取失败~\n' + pixivid['errors']['system']['message'])
            sys.exit()
        pixiv.saveToken(pixivid)
    '''开始'''
    data = Favorites(pixivid).favorites()  # 第一次进入收藏夹
    data_list = Processed_data(data).data_list  # 处理数据
    database(mycol, mycol_del, data_list)  # 插入数据库
    while True:
        if data['next_url'] == None:  # 到最后一页就停止
            print('>>done<<')
            break
        nexturl = data['next_url']
        time.sleep(random.randint(4, 6))
        data = Favorites_next_url(pixivid, nexturl).favorites()
        data_list = Processed_data(data).data_list
        database(mycol, mycol_del, data_list)
    '''结束'''
    nowdata_num = len(list(mycol.find({})))
    print('本次新增', nowdata_num - data_num, '条')
