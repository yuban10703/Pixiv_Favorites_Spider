import base64
import time
import json
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

with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    config = json.loads(f.read())
    print('获取配置成功')
APPKEY = config['APPKEY']
APPID = int(config['APPID'])
path = config['path']
myclient = pymongo.MongoClient(config['mongodb'])  # 数据库地址
mydb = myclient[config['database']]  # 数据库
setu_all = mydb[config['collection']]  # 集合

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

    def base_64(self):
        pic_path = path + self.filename
        size = os.path.getsize(pic_path) / 1024
        if size > 900:
            print('>>>>压缩<<<<')
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
                'image': self.base_64()}
        body['sign'] = self.sign(body)
        res = requests.post(url, data=body)
        # print(res.status_code)
        return res.json()

    @retry(stop_max_attempt_number=3, wait_random_max=1000)
    def result(self):
        data = self.distinguish()
        # print(data)
        if data['msg'] == 'ok':
            emm = sorted(data['data']['tag_list'][:3], key=lambda x: x["tag_confidence_f"], reverse=True)
            return emm[0]['tag_name']
        else:
            raise


repeat = 0

ways = {'normal': 'normal', 'hot': 'sexy', 'porn': 'porn'}
if __name__ == '__main__':
    allsetus = setu_all.find().sort('_id', -1)  # 读取数据库所有信息
    # allsetus = setu_all.find({'_id':3368}).sort('_id',-1)
    print('从{}开始'.format(_id))
    for setu in allsetus:
        if repeat > 5:
            break
        print('id:{}:{}'.format(setu['_id'],setu['title'])  ,end='')
        filename = setu['filename']
        tag_for_tx = Identification(filename)
        tag = ways[tag_for_tx.result()]
        print(', {}'.format(tag))
        tag_before = setu['type']
        # print(tag_before)
        if tag_before == None:
            result = setu_all.update_one({'filename': filename},
                                         {'$set': {'type': tag}})  # 更新数据
            print('更新数量:{}'.format(result.matched_count))
            continue
        repeat += 1
        time.sleep(0.5)
