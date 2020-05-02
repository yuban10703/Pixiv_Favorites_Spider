from fastapi import FastAPI, Query
import re
import random
import pymongo

app = FastAPI()


myclient = pymongo.MongoClient("mongodb://10.1.1.142:27017/")


mydb = myclient["setu"]
mycol = mydb["setu_1"]


@app.get("/setu")
async def setu(tag: str = Query('', max_length=15), r18: bool = False):
    data_re = re.compile(tag)
    tmp = mycol.find({"$and": [{'tags': data_re}, {'R18': r18}]})
    setus = list(tmp)
    setus_num = len(setus)
    try:
        if setus_num != 0:
            num = random.randint(0, (setus_num - 1))
            setu = (setus[num])
            setu['code'] = 200
            return setu
        else:
            return {'code': '404', }
    except:
        return {'code': '500'}
