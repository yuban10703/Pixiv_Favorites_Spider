from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import re
import pymongo

app = FastAPI()

try:
    myclient = pymongo.MongoClient("mongodb://10.1.1.142:27017/")
    print('连接成功~')
except:
    print('连接失败~')

mydb = myclient["setu"]
setu_all = mydb["setu_all"]
setu_sexy = mydb['setu_sexy']  # 性感
setu_porn = mydb['setu_porn']  # 色情


def find_setu(condition, num, database):
    result = database.aggregate([{'$match': condition}, {'$sample': {'size': num}}])
    return result


@app.get("/setu_v2")
async def setu(tag: str = Query('', max_length=35), num: int = Query(1, le=10), r18: bool = False):
    print('SETU_V2: tag:{0}, num:{1}, r18:{2}'.format(tag, num, r18))
    try:
        data_re = re.compile(tag)
        condition = {'tags': data_re}
        if r18:
            setu = list(find_setu(condition, num, setu_porn))
        else:
            setu = list(find_setu(condition, num, setu_sexy))
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = {'code': 200}
            setu_full['data'] = setu
            return setu_full
        else:
            return JSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~'})


@app.get("/setu")
async def setu(tag: str = Query('', max_length=35), r18: bool = False):
    print('SETU_V1: tag:{0}, r18:{1}'.format(tag, r18))
    try:
        data_re = re.compile(tag)
        condition = {'tags': data_re, 'R18': r18}
        setu = list(find_setu(condition, 1, setu_all))
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = setu[0]
            setu_full['code'] = 200
            return setu_full
        else:
            return JSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~'})
