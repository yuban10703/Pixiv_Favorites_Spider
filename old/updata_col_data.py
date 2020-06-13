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

myclient = pymongo.MongoClient('mongodb://10.1.1.142:27017/setu')  # 数据库地址
mydb = myclient['setu']  # 数据库
mycol = mydb['setu_all']  # 集合
setu_normal = mydb['setu_normal']  # 正常
setu_sexy = mydb['setu_sexy']  # 性感
setu_porn = mydb['setu_porn']  # 色情


class Parsing_all:  # 处理信息
    def __init__(self, data, num):
        self.title = data['title']
        self.artwork = data['artwork']
        self.author = data['author']
        self.artist = data['artist']
        # self.page = 'p{page}'.format(page=num)
        self.tags = data['tags']
        self.filename = data['filename'][num]
        self.original = data['original'][num]
        self.large = data['large'][num]
        self.medium = data['medium'][num]
        self.square_medium = data['square_medium'][num]
        '''拼凑字典'''
        self.alldata = {'title': self.title, 'artwork': self.artwork, 'author': self.author,
                        'artist': self.artist,
                        'tags': self.tags, 'filename': self.filename, 'original': self.original,
                        'large': self.large, 'medium': self.medium, 'square_medium': self.square_medium}  # 拼凑字典..


def compared(data, col, col_all):
    filename = data['filename']  # filename对于col是唯一的
    artwork_id = data['artwork']  # artworkid对于col_all是唯一的
    pnum = int(data['page'][1:])  # 读取数据是第几页
    # print(pnum)
    data_for_db_all = col_all.find_one({'artwork': artwork_id})  # 从总数据库读取数据
    # print(data_for_db_all)
    if data_for_db_all != None:
        try:
            data_for_update = Parsing_all(data_for_db_all, pnum)  # 处理总数据库的数据
        except:
            print('data_for_update_炸啦~~~,应该是作者删P了{}'.format(artwork_id))
            return
        if data_for_update.original != data['original']:  # 如果数据不一样就替换
            print('不一致')
            result = col.update_one({'filename': filename},
                                    {'$set': data_for_update.alldata})  # 更新数据(filename是唯一的,直接覆盖掉除_id外的数据)
            if result.modified_count:
                print('更新成功')
                return
            else:
                print('{}更新失败?????????'.format(artwork_id))
                return
        else:
            # print('一致')
            return
    else:
        print('总数据库无此数据,{}'.format(artwork_id))


collist = [setu_normal, setu_sexy, setu_porn]
for col in collist:
    for coldata in col.find():
        compared(coldata, col, mycol)
    #     break
    # break
