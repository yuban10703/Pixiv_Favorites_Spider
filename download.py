from PIL import Image
import aiohttp
import asyncio
import io
import os
import pymongo
import json

with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    config = json.loads(f.read())
    print('获取配置成功')
myclient = pymongo.MongoClient(config['mongodb'])  # 数据库地址
mydb = myclient[config['database']]  # 数据库
mycol = mydb[config['collection']]  # 集合
path = config['download_path']  # 下载路径

headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
           'Accept-Language': 'zh_CN',
           'App-OS': 'android',
           'App-OS-Version': '6.0.1',
           'App-Version': '5.0.191',
           'Referer': 'https://www.pixiv.net'}

list = os.listdir(path)  # 获取下载路径的所有文件
print(list)  # 打印文件列表


async def download(filename, url):  # 下载
    if filename not in list:  # 如果文件不在列表中就下载
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status)  # 打印状态码
                date = await resp.content.read()
                Image.open(io.BytesIO(date)).save(path + filename)  # 以二进制读取文件,并转码为对应格式保存
    else:
        print('已下载过')


aa = mycol.find({})  # 读取数据库所有信息
tasks = []  # 任务列表


async def main():
    for i in aa:  # 遍历数据库里所有信息
        for ii in range(i['page']):  # 获取画册页数
            print(i['large'][ii])  # 打印链接
            filename = i['filename'][ii]  # 获取文件名
            tasks.append(asyncio.create_task(download(filename, str(i['large'][ii]))))  # 加入任务
    await asyncio.gather(*tasks)  # 并发执行


asyncio.run(main())  # gogogo
