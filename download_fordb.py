import aiohttp
import asyncio
import aiofiles
import os
import pymongo

path = 'Y:\\setu\\'  # 下载路径

myclient = pymongo.MongoClient("mongodb://10.1.1.142:27017/")  # 数据库地址
mydb = myclient["setu"]  # 数据库
mycol = mydb["setu_1"]  # 集合

headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
           'Accept-Language': 'zh_CN',
           'App-OS': 'android',
           'App-OS-Version': '6.0.1',
           'App-Version': '5.0.191',
           'Referer': 'https://www.pixiv.net'}
# path = os.getcwd()

list = os.listdir(path)  # 获取下载路径的所有文件
print(list)  # 打印文件列表


async def download(filename, url):  # 下载
    # filename = os.path.basename(url)
    if filename not in list:  # 如果文件不在列表中就下载
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status)  # 打印状态码
                test = await resp.content.read()
                async with aiofiles.open(path + filename, 'wb') as f:
                    await f.write(test)
                    print(path + filename)  # 打印路径+文件名
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


asyncio.run(main())
