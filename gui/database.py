import pymongo
from bson import ObjectId


class DataBase:
    myclient = pymongo.MongoClient('mongodb+srv://username:password@cludn.mongodb.net/setu?retryWrites=true&w=majority')  # 数据库地址
    mydb = myclient['setu']  # 数据库
    setu = mydb['setu_v5']  # 集合
    setu_del = mydb['setu_del_v5']  # 集合

    @classmethod
    def init_gui(cls):
        return list(cls.setu.find().sort('_id', 1).limit(1))[0]

    @classmethod
    def previous(cls, _id: str):
        return list(cls.setu.find({'_id': {'$lt': ObjectId(_id)}}).sort('_id', -1).limit(1))[0]

    @classmethod
    def next(cls, _id: str):
        return list(cls.setu.find({'_id': {'$gt': ObjectId(_id)}}).sort('_id', 1).limit(1))[0]

    @classmethod
    def next_r18(cls, _id: str):
        return list(cls.setu.find({'r18': True, '_id': {'$gt': ObjectId(_id)}}).sort('_id', 1).limit(1))[0]

    @classmethod
    def next_not_r18(cls, _id: str):
        return list(cls.setu.find({'r18': False, '_id': {'$gt': ObjectId(_id)}}).sort('_id', 1).limit(1))[0]

    @classmethod
    def getdata(cls, _id: str):
        if data := cls.setu.find_one({'_id': ObjectId(_id.replace("\n", ""))}):
            return data
        else:
            return cls.next(_id)

    @classmethod
    def find(cls, pid, page=None):
        if page:
            return cls.setu.find_one({'artwork.id': pid, 'page': page})
        return cls.setu.find_one({'artwork.id': pid})

    @classmethod
    def updateType(cls, _id: str, r18: bool):  # 更新type
        return cls.setu.update_one({'_id': ObjectId(_id)}, {'$set': {'r18': r18}}).matched_count

    @classmethod
    def updateTags(cls, _id: str, tags: list):  # 更新type
        return cls.setu.update_one({'_id': ObjectId(_id)}, {'$set': {'tags': tags}}).matched_count

    @classmethod
    def delsetu(cls, _id, pid, page):
        print('删除: {}'.format(cls.setu_del.insert_one({'pid': pid, 'page': page}).inserted_id))
        return cls.setu.delete_one({'_id': ObjectId(_id)}).deleted_count

    @classmethod
    def unmodified_count(cls) -> int:
        return cls.setu.count_documents({'r18': None})

    @classmethod
    def modified_count(cls) -> int:
        return cls.setu.count_documents({'r18': {"$ne": None}})

    @classmethod
    def noFiltrate(cls):
        return list(cls.setu.find({'r18': None}).sort('r18', 1).limit(1))[0]
