import base64
import time
import io
import os
import requests
import hashlib
import random
import string
from urllib.parse import urlencode
from PIL import Image
from retrying import retry
import pymongo

APPKEY = '' 
APPID =  #int类型
path = 'Y:\\PICS\\'
myclient = pymongo.MongoClient('mongodb://tianle:laosepi10703@10.1.1.142:27017/')  # 数据库地址
mydb = myclient['setu']  # 数据库
setu_all = mydb['setu_all']  # 集合
setu_normal = mydb['setu_normal']  # 正常
setu_sexy = mydb['setu_sexy']  # 性感
setu_porn = mydb['setu_porn']  # 色情

lastdata_id = setu_all.find().sort('_id', -1).limit(1)  # 数据库的最后一条数据
try:  # 数据库里没有数据会出错
    _id = list(lastdata_id)[0]['_id']  # +1(_)
except:  # 出错了就说明数据库没数据,那就从0开始
    _id = 0


class Parsing:  # 处理信息
    def __init__(self, data, num):
        self.title = data['title']
        self.artwork = data['artwork']
        self.author = data['author']
        self.artist = data['artist']
        self.page = 'p{page}'.format(page=num)
        self.tags = data['tags']
        self.filename = data['filename'][num]
        self.original = data['original'][num]
        self.large = data['large'][num]
        self.medium = data['medium'][num]
        self.square_medium = data['square_medium'][num]


class Identification:
    def __init__(self, filename):
        self.filename = filename

    def base_64(self, filename):
        pic_path = path + filename
        size = os.path.getsize(pic_path) / 1024
        if size > 900:
            with Image.open(pic_path) as img:
                w, h = img.size
                newWidth = 500
                newHeight = round(newWidth / w * h)
                img = img.resize((newWidth, newHeight), Image.ANTIALIAS)
                img_buffer = io.BytesIO()  # 生成buffer
                img.save(img_buffer, format='PNG', quality=70)
                byte_data = img_buffer.getvalue()
                base64_data = base64.b64encode(byte_data)
                code = base64_data.decode()
                return code
        with open(pic_path, 'rb') as f:
            coding = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
            return coding.decode()

    def sign(self, body):  # sign计算
        b = urlencode(sorted(body.items(), key=lambda value: value[0]))
        b += '&app_key=' + APPKEY
        return str(hashlib.md5(b.encode()).hexdigest()).upper()

    def distinguish(self):
        url = 'https://api.ai.qq.com/fcgi-bin/vision/vision_porn'
        body = {'app_id': APPID,
                'time_stamp': int(time.time()),
                'nonce_str': ''.join(random.sample(string.ascii_letters + string.digits, 32)),
                'image': self.base_64(self.filename)}
        body['sign'] = self.sign(body)
        res = requests.post(url, data=body)
        # print(res.status_code)
        return res.json()

    @retry(stop_max_attempt_number=3, wait_random_max=2000)
    def result(self):
        data = self.distinguish()
        print(data)
        if data['msg'] == 'ok':
            emm = sorted(data['data']['tag_list'][:3], key=lambda x: x["tag_confidence_f"], reverse=True)
            return emm[0]['tag_name']
        else:
            raise


repeat = []


def database(setu, col):
    if col.count_documents({'filename': setu.filename}) == False:  # 通过文件名去重
        lastdata = col.find().sort('_id', -1).limit(1)  # 数据库的最后一条数据
        try:  # 数据库里没有数据会出错
            num = list(lastdata)[0]['_id'] + 1  # +1(_)
        except:  # 出错了就说明数据库没数据,那就从0开始
            num = 0
        setudict = {'_id': num, 'title': setu.title, 'artwork': setu.artwork, 'author': setu.author,
                    'artist': setu.artist,
                    'page': setu.page, 'tags': setu.tags, 'filename': setu.filename, 'original': setu.original,
                    'large': setu.large, 'medium': setu.medium, 'square_medium': setu.square_medium}  # 拼凑字典..
        info = col.insert_one(setudict)  # 向数据库插入数据
        print('id:', info.inserted_id)  # 打印_id
        return
    else:
        repeat.append(setu.filename)


def normal(data):
    print('就这?')
    database(data, setu_normal)


def sexy(data):
    print('还行')
    database(data, setu_sexy)


def porn(data):
    print('社保')
    database(data, setu_porn)


ways = {'normal': normal, 'hot': sexy, 'porn': porn}
allsetus = setu_all.find().sort('_id', -1)  # 读取数据库所有信息
print('从{0}开始'.format(_id))

for i in allsetus:
    if len(repeat) > 5:
        break
    print(i['_id'])
    for ii in range(i['page']):
        filename = i['filename'][ii]
        # print(filename)
        tag = Identification(filename)
        data = Parsing(i, ii)
        ways[tag.result()](data)
        time.sleep(0.8)
