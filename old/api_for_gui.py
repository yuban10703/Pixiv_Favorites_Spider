from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import re
import motor.motor_asyncio

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient

myclient = client("mongodb://10.1.1.142:27017/setu")

mydb = myclient["setu"]
setu_test = mydb['setu_test']
setu_normal = mydb['setu_normal_0']  # 正常
setu_sexy = mydb['setu_sexy_0']  # 性感
setu_porn = mydb['setu_porn_0']  # 色情


class Item(BaseModel):
    data: dict  # 待更新的数据
    collection: str


class Item_get(Item):
    data: int  # 数据库的_id


class Item_move(Item):
    to_collection: str  # 移动到哪个表


async def replace(data, collection):
    data_for_only = await collection.find_one({'artwork': data['artwork']})  # 查找是否有这条数据
    if data_for_only != None:  # 数据库中有信息就更新
        result = await collection.replace_one({'_id': data['_id']}, data)  # 更新数据
        num = result.modified_count  # 如果数据没变化就是0,变化了就是1
        print('更新数量:{}'.format(num))
        return num
    else:
        print('???')
        raise


async def get_database_id(collection):  # 获取数据库中的_id 实现自增长
    data = collection.find()
    lastdata = data.sort('_id', -1).limit(1)  # 数据库的最后一条数据
    try:  # 数据库里没有数据会出错
        async for i in lastdata:
            num = i['_id'] + 1
    except:  # 出错了就说明数据库没数据,那就从0开始
        num = 0
    # print(num)
    return num


async def get_setu(id, collection):
    data = await collection.find_one({'_id': id})  # 查找数据
    return data


async def move_setu(data, collection, to_collection):
    # print('id:{}'.format(id))
    await collection.delete_many({'_id': data['_id']})  # 删除原表数据
    if to_collection != '':  # 如果to_collection不为空就插入数据
        id = await get_database_id(to_collection)
        data['_id'] = id  # 更新_id
        # print(data)
        res_insert = await to_collection.insert_one(data)  # 插入到新表
        return res_insert.inserted_id
    return 'OK'


ways = {'normal': setu_normal, 'sexy': setu_sexy, 'porn': setu_porn, '': ''}


@app.post("/replace")  # 更新数据
async def replace_setu(body: Item):
    try:
        data_back = {'code': 200}
        res = await replace(body.data, ways[body.collection])
        if res:
            data_back['msg'] = '更新成功'
        else:
            data_back = {'code': 400}
            data_back['msg'] = '未更新'
            return JSONResponse(status_code=400, content=data_back)
        return data_back
    except Exception as error:
        return JSONResponse(status_code=500, content={'code': 500, 'msg': '爆炸啦~', 'error': str(error)})


@app.post("/get")  # 通过'_id'获取数据
async def getsetu(body: Item_get):
    try:
        res = await get_setu(body.data, ways[body.collection])
        return res
    except Exception as error:
        return JSONResponse(status_code=500, content={'msg': '爆炸啦~', 'error': str(error)})


@app.post("/move")  # 移动数据到新的表
async def movesetu(body: Item_move):
    try:
        if body.collection == body.to_collection:  # ??????
            raise
        res = await move_setu(body.data, ways[body.collection], ways[body.to_collection])
        return res
    except Exception as error:
        return JSONResponse(status_code=500, content={'msg': '爆炸啦~', 'error': str(error)})
