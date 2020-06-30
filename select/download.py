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


async def download(session, filename, url, path):  # 下载
    try:
        async with session.get(url, headers=headers) as res:
            assert res.status == 200
            date = await res.content.read()
            Image.open(io.BytesIO(date)).save(path + filename)  # 以二进制读取文件,并转码为对应格式保存
            print('{}下载成功 :{}'.format(filename, res.status))
            return
    except:  # 不知道为什么会出错.....
        print('下载失败: >>>{}<<<'.format(filename))
        faild_list.append(url)
        return


async def download_original(session, filename, url, path):  # 下载
    try:
        async with session.get(url, headers=headers) as res:
            assert res.status == 200
            date = await res.content.read()
            async with aiofiles.open(path + filename, 'wb') as f:
                await f.write(date)
            print('{}下载成功  '.format(filename, res.status))
            return
    except:  # 不知道为什么会出错.....
        print('下载失败: >>>{}<<<'.format(filename))
        faild_list.append(url)
        return

alldata = mycol.find({})  # 读取数据库所有信息
faild_list = []
task_data = []

for data in alldata:  # 遍历数据库里所有信息
    task_data.append({'url': data['large'], 'url_original': data['original'], 'filename': data['filename']})
print('获取数据库成功~')
async def main():
    conn = aiohttp.TCPConnector(limit=50)  # 限制连接池
    async with aiohttp.ClientSession(connector=conn) as session:
        for _ in range(3):
            tasks = []  # 任务列表
            faild_list.clear()
            list = os.listdir(path)  # 获取下载路径的所有文件
            list_original = os.listdir(path_original)
            for data in task_data:
                url = data['url']
                url_original = data['url_original']
                filename = data['filename']  # 获取文件名
                if filename not in list:
                    tasks.append(asyncio.create_task(download(session, filename, url, path)))  # 加入任务
                if filename not in list_original:
                    tasks.append(
                        asyncio.create_task(download_original(session, filename, url_original, path_original)))  # 加入任务(原图)
            await asyncio.gather(*tasks)  # 并发执行
            if not len(faild_list): #如果没有下载失败的就结束
                break

if __name__ == '__main__':
    print('开始下载~')
    asyncio.run(main())  # gogogo
    print(faild_list)
    print('下载失败数量:{}'.format(len(faild_list)))