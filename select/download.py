from PIL import Image
import aiohttp
import aiofiles
import asyncio
import io
import os
import json
import pymongo

with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    config = json.loads(f.read())
    print('获取配置成功')
# myclient = pymongo.MongoClient(sys.argv[1])  # 数据库地址
myclient = pymongo.MongoClient(config['mongodb'])  # 数据库地址
mydb = myclient[config['database']]  # 数据库
mycol = mydb[config['collection']]  # 集合
# path = './pics/'  # 下载路径
# path_original = './pics_original/'  # 下载路径
path = config['path']  # 下载路径
path_original = config['path_original']  # 下载路径

headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
           'Accept-Language': 'zh_CN',
           'App-OS': 'android',
           'App-OS-Version': '6.0.1',
           'App-Version': '5.0.191',
           'Referer': 'https://www.pixiv.net'}

list = os.listdir(path)  # 获取下载路径的所有文件
list_original = os.listdir(path_original)


async def download(session,filename, url, path):  # 下载
    try:
        async with session.get(url, headers=headers) as resp:
            print(resp.status)  # 打印状态码
            date = await resp.content.read()
            Image.open(io.BytesIO(date)).save(path + filename)  # 以二进制读取文件,并转码为对应格式保存
            return
    except:
        print('>>>', filename, '<<')
        return

async def download_original(session,filename, url, path):  # 下载
    try:
        async with session.get(url, headers=headers) as resp:
            print(resp.status)  # 打印状态码
            date = await resp.content.read()
            async with aiofiles.open(path + filename, 'wb') as f:
                await f.write(date)
            return
    except:
        print('>>>', filename, '<<')
        faild_list.append(filename)
        return



alldata = mycol.find({})  # 读取数据库所有信息
tasks = []  # 任务列表
faild_list = []
async def main():
    # num = 0
    async with aiohttp.ClientSession() as session:
        for data in alldata:  # 遍历数据库里所有信息
            # if num >=100:
            #     break
            url = data['large']
            url_original = data['original']
            filename = data['filename']  # 获取文件名
            if filename not in list:
                tasks.append(asyncio.create_task(download(session,filename, url, path)))  # 加入任务
            if filename not in list_original:
                tasks.append(asyncio.create_task(download_original(session,filename, url_original, path_original)))  # 加入任务(原图)
                # num +=1
        await asyncio.gather(*tasks)  # 并发执行


asyncio.run(main())  # gogogo
print(faild_list)
print('下载失败数量:"{}'.format(len(faild_list)))