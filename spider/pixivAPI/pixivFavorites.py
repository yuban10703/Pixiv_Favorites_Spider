# import httpx
import hashlib
from datetime import datetime

from retrying import retry


class PixivFavorites:
    def __init__(self, userid, access_token, session):
        self.userid = userid
        self.access_token = access_token
        self.session = session

    def headers(self) -> dict:
        hash_secret = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
        X_Client_Time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        X_Client_Hash = hashlib.md5(
            (X_Client_Time + hash_secret).encode("utf-8")
        ).hexdigest()
        return {
            'Authorization': 'Bearer ' + self.access_token,
            "User-Agent": "PixivAndroidApp/5.0.197 (Android 10; Redmi 4)",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept-Language": "zh_CN_#Hans",
            "App-OS": "android",
            "App-OS-Version": "10",
            "App-Version": "5.0.197",
            "X-Client-Time": X_Client_Time,
            "X-Client-Hash": X_Client_Hash,
            "Host": "app-api.pixiv.net"
        }

    @retry(stop_max_attempt_number=5, wait_random_max=2000)
    def favorites(self, max_bookmark_id=None) -> dict:
        params = {'user_id': self.userid,
                  'restrict': 'public'}  # 公开收藏夹
        if max_bookmark_id:
            params['max_bookmark_id'] = max_bookmark_id
        # print(params)
        res = self.session.get(
            url='https://app-api.pixiv.net/v1/user/bookmarks/illust',
            params=params,
            headers=self.headers()
        ).json()
        return res
