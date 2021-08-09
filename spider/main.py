import random
import time
import urllib.parse as urlparse

import httpx

from database import process_data, Database
from pixivAPI import PixivToken, PixivFavorites

if __name__ == '__main__':
    pixivToken = PixivToken()
    pixivToken.main()
    with httpx.Client() as session:
        data = PixivFavorites(pixivToken.tokendata['response']['user']['id'],
                              pixivToken.tokendata['access_token'],
                              session).favorites()  # 第一次进入收藏夹
        print(data)
        Database(data=process_data(data['illusts'])).main()
        while True:
            if data['next_url'] == None:  # 到最后一页就停止
                print('>>done<<')
                break
            time.sleep(random.randint(2, 4))
            data = PixivFavorites(pixivToken.tokendata['response']['user']['id'],
                                  pixivToken.tokendata['access_token'],
                                  session).favorites(max_bookmark_id=int(
                urlparse.parse_qs(urlparse.urlparse(data['next_url']).query)['max_bookmark_id'][0]))  # 第一次进入收藏夹
            print(data)
            Database(data=process_data(data['illusts'])).main()
    # print(data['max_bookmark_id'])
