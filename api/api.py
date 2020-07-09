import re
import motor.motor_asyncio
from fastapi import FastAPI, Query
from fastapi.responses import ORJSONResponse

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient

myclient = client("mongodb://10.1.1.142:27017/setu")

mydb = myclient["setu"]
collection = 'setu_all_v3'


async def find(condition, num):  # collection为str参数
    result = await mydb.command(
        'aggregate', collection,
        pipeline=[{'$match': condition},
                  {'$sample': {'size': num}}],
        explain=False)
    return result['cursor']['firstBatch']


# ------------------------------------------------------------------------------------------------------------

@app.get("/setu", response_class=ORJSONResponse)
async def setu_v1(tag: str = Query('', max_length=35), r18: bool = False):
    print('{0}SETU_V1: tag:[{1}] r18:[{2}]{3}'.format('>' * 20, tag, r18, '<' * 20))
    condition = {}
    try:
        if (len(tag) != 0) and (not tag.isspace()):  # 如果tag不为空(字符串字数不为零且不为空)
            condition['tags'] = re.compile(tag.strip(), re.I)  # 正则并去掉字符两边空格
        if r18:
            condition['type'] = 'porn'
            setu = await find(condition, 1)
        else:
            condition['type'] = 'sexy'
            setu = await find(condition, 1)
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = setu[0]
            setu_full['code'] = 200
            return setu_full
        else:
            return ORJSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return ORJSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})


# ------------------------------------------------------------------------------------------------------------


@app.get("/setu_v2", response_class=ORJSONResponse)
async def setu_v2(tag: str = Query('', max_length=45), num: int = Query(1, ge=1, le=10), r18: bool = False):
    print('{0}SETU_V2: tag:[{1}] r18:[{2}] num:[{3}]{4}'.format('>' * 20, tag, r18, num, '<' * 20))
    condition = {}
    try:
        if (len(tag) != 0) and (not tag.isspace()):  # 如果tag不为空(字符串字数不为零且不为空)
            condition['tags'] = re.compile(tag.strip(), re.I)
        if r18:
            condition['type'] = 'porn'
            setu = await find(condition, num)
        else:
            condition['type'] = 'sexy'
            setu = await find(condition, num)
        setus_num = len(setu)
        if setus_num != 0:
            for i in range(setus_num):  # 兼容v2
                setu[i]['page'] = 'p{}'.format(setu[i]['page'])
            setu_full = {'code': 200}
            setu_full['data'] = setu
            return setu_full
        else:
            return ORJSONResponse(status_code=404, content={'code': 404, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return ORJSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})


# ------------------------------------------------------------------------------------------------------------

ways_v3 = {
    0: {'type': 'normal'},
    1: {'type': 'sexy'},
    2: {'type': 'porn'},
    3: {'$or': [{'type': 'normal'}, {'type': 'sexy'}, {'type': 'porn'}]}
}


@app.get("/setu_v3", response_class=ORJSONResponse)
async def setu_v3(tag: str = Query('', max_length=45), num: int = Query(1, ge=1, le=10),
                  type: int = Query(0, ge=0, le=3)):
    print('{0}SETU_V3: tag:[{1}] type:[{2}] num:[{3}]{4}'.format('>' * 20, tag, type, num, '<' * 20))
    try:
        condition = ways_v3[type].copy()
        if (len(tag) != 0) and (not tag.isspace()):  # 如果tag不为空(字符串字数不为零且不为空)
            condition['tags'] = re.compile(tag.strip(), re.I)
        setu = await find(condition, num)
        setus_num = len(setu)
        if setus_num != 0:
            setu_full = {'code': 200, 'count': setus_num}
            setu_full['data'] = setu
            return setu_full
        else:
            return ORJSONResponse(status_code=404, content={'code': 404, 'count': 0, 'msg': '色图库中没找到色图~'})
    except Exception as error:
        return ORJSONResponse(status_code=500,
                              content={'code': 500, 'count': 0, 'msg': '爆炸啦~', 'error': str(error)})
