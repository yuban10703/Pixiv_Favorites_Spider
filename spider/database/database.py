import json
import sys
from pathlib import Path
from typing import List

import pymongo

from spider.model import Setu

try:
    with open(Path(__file__).absolute().parent.parent / "config" / "database.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        print("读取database.json成功~")
except Exception as e:
    print("database.json载入失败,请检查内容并重新启动~\r\n{}".format(e))
    sys.exit(0)

myclient = pymongo.MongoClient(config['mongodb'])
mydb = myclient[config['database']]
mycol = mydb[config['collection']]
mycol_del = mydb[config['collection_del']]


class Database:

    def __init__(self, data: List[Setu]):
        self.collection = mycol
        self.collection_del = mycol_del
        self.setus = data

    def filter_del(self):
        """
        过滤掉删除过的
        :return:
        """
        setus_copy = self.setus.copy()
        for setu in setus_copy:
            if self.collection_del.find_one({'pid': setu.artwork.id, 'page': setu.page}):
                self.setus.remove(setu)

    def filter_changing_and_repeating(self):
        """
        过滤重复的和有改变的
        :return:
        """
        setus_copy = self.setus.copy()
        for setu in setus_copy:
            if data := self.collection.find_one({'artwork.id': setu.artwork.id, 'page': setu.page}):  # 是否存在
                if data['urls']['original'] == str(setu.urls.original):
                    self.setus.remove(setu)
                    print('数据一致')
                else:
                    print('数据不一致')
                    print(setu.create_date, '---', data['create_date'])
                    result = self.collection.delete_many({'artwork.id': setu.artwork.id})  # 删除这个id的所有数据
                    print("已删除{}条关于id:{}的数据".format(result.deleted_count, setu.artwork.id))

    def insertData(self):
        data_insert = [data.dict() for data in self.setus]
        if data_insert == []:
            return
        result = self.collection.insert_many(data_insert)
        for setu in self.setus:
            print('{}  P:{}'.format(setu.artwork.id, setu.page))
        print('增加:{}'.format(len(result.inserted_ids)))

    def main(self):
        self.filter_del()
        self.filter_changing_and_repeating()
        self.insertData()
        print('-' * 20)
