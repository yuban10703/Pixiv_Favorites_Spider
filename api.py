from xmlrpc.client import boolean

from fastapi import FastAPI
import re
import random
import pymongo
from pydantic import BaseModel

app = FastAPI()

try:
    myclient = pymongo.MongoClient("mongodb://10.1.1.116:27017/")
    print('连接成功~')
except:
    print('连接失败~')

mydb = myclient["setu_test"]
mycol = mydb["test2"]


# @app.post("/setu")
# async def setu(tag: '',r18 : boolean = False):
#     if tag ==None:
#         tmp = mycol.aggregate([{'$sample': {'size': 1}}])
#         setu = list(tmp)[0]
#         print(setu['_id'])
#         return setu

# @app.post("/tags/{tags}")
# async def tags(tags):
#     data_re = re.compile(tags)
#     tmp = mycol.find({'tags':data_re})
#     setus = list(tmp)
#     num = random.randint(0, (len(setus)-1))
#     setu = setus[num]
#     return setu

# @app.post("/setu")
# async def setu(tag:str = None ,r18 : int = 2):
#     if tag ==None and r18==2 :
#         tmp = mycol.aggregate([{'$sample': {'size': 1}}])
#         setu = list(tmp)[0]
#         print(setu['_id'])
#         return setu
#     else:
#         print(tag)
#         data_re = re.compile(tag)
#         tmp = mycol.find({"$and":[{'tags':data_re},{'R18':True}]})
#         setus = list(tmp)
#         num = random.randint(0, (len(setus) - 1))
#         setu = setus[num]
#         return setu

@app.get("/setu")
async def setu(tag: str = '', r18: boolean = False):
    # a = {'a':tag , 'b':r18}
    # return a
    print(tag)
    data_re = re.compile(tag)
    tmp = mycol.find({"$and": [{'tags': data_re}, {'R18': r18}]})
    setus = list(tmp)
    setus_num = len(setus)
    if setus != 0:
        num = random.randint(0, (setus_num - 1))
        setu = setus[num]
        return setu
    else:
        return
#
# fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]
#
# @app.get("/items/")
# async def read_item(skip: int = 0, limit: int = 10):
#     return fake_items_db[skip : skip + limit]
