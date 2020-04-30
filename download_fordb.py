import aiohttp
import asyncio
import aiofiles
import os
import pymongo
path = 'F:\\pixiv\\test' #下载路径

myclient = pymongo.MongoClient("mongodb://10.1.1.116:27017/")
mydb = myclient["setu_test"]
mycol = mydb["test2"]

headers = {'User-Agent': 'PixivAndroidApp/5.0.191 (Android 6.0.1; HUAWEI ALE-CL00)',
           'Accept-Language': 'zh_CN',
           'App-OS': 'android',
           'App-OS-Version': '6.0.1',
           'App-Version': '5.0.191',
           'Referer': 'https://www.pixiv.net'}
# path = os.getcwd()

list = os.listdir(path)
print (list)

async def download(filename,url):
    # filename = os.path.basename(url)
    if filename not in list:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                print(resp.status)
                test = await resp.content.read()
                async with aiofiles.open(path+filename, 'wb') as f:
                    await f.write(test)
                    print('>>OK<<')
    else:
        print('已下载过')

aa = mycol.find({})
tasks = []


async def main():
    for i in aa:
        for ii in range(i['page']):
            print(i['large'][ii])
            filename = i['filename'][ii]
            tasks.append(asyncio.create_task(download(filename,str(i['large'][ii]))))
    await asyncio.gather(*tasks)


asyncio.run(main())
