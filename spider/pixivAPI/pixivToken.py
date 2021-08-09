import hashlib
import json
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from retrying import retry

from ._proxies import proxies, transport

scheduler = BackgroundScheduler()


class PixivToken:
    def __init__(self):
        self.tokenPath = Path(__file__).absolute().parent.parent / "config" / ".PixivToken.json"
        self.tokendata = {}
        self.Client = httpx.Client(proxies=proxies, transport=transport)

    def headers(self):
        hash_secret = "28c1fdd170a5204386cb1313c7077b34f83e4aaf4aa829ce78c231e05b0bae2c"
        X_Client_Time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S+08:00")
        X_Client_Hash = hashlib.md5(
            (X_Client_Time + hash_secret).encode("utf-8")
        ).hexdigest()
        headers = {
            "User-Agent": "PixivAndroidApp/5.0.197 (Android 10; Redmi 4)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Language": "zh_CN_#Hans",
            "App-OS": "android",
            "App-OS-Version": "10",
            "App-Version": "5.0.197",
            "X-Client-Time": X_Client_Time,
            "X-Client-Hash": X_Client_Hash,
            "Host": "oauth.secure.pixiv.net",
            "Accept-Encoding": "gzip",
        }
        return headers

    @retry(stop_max_attempt_number=3, wait_random_max=5000)
    def refresh_token(self):
        url = "https://oauth.secure.pixiv.net/auth/token"
        print("尝试刷新Pixiv_token")
        data = {
            "client_id": "MOBrBDS8blbauoSck0ZfDbtuzpyT",
            "client_secret": "lsACyCD94FhDUtGTXi3QzcFE2uU1hqtDaKeqrdwj",
            "grant_type": "refresh_token",
            "refresh_token": self.tokendata["refresh_token"],
            "device_token": self.tokendata["device_token"]
            if "device_token" in self.tokendata.keys()
            else uuid.uuid4().hex,
            "get_secure_url": "true",
            "include_policy": "true",
        }
        self.tokendata = self.Client.post(url, data=data, headers=self.headers()).json()
        self.tokendata["time"] = time.time()
        print("刷新token成功~")
        self.saveToken()

    def continue_refresh_token(self):
        try:
            self.refresh_token()
        except:
            print("刷新失败")
            nextTime = 300
        else:
            nextTime = int(
                self.tokendata["expires_in"] - (time.time() - self.tokendata["time"])
            )
        self.addJob(nextTime)
        return

    def saveToken(self):
        with open(self.tokenPath, "w", encoding="utf-8") as f:
            json.dump(self.tokendata, f, indent=4, ensure_ascii=False)
        print("PixivToken已保存到.PixivToken.json")
        return

    def addJob(self, next_time: int):
        print("离下次刷新还有:{}s".format(next_time))
        scheduler.add_job(
            self.continue_refresh_token,
            next_run_time=datetime.now() + timedelta(seconds=next_time - 1),
            misfire_grace_time=30,
        )

    def main(self):
        try:
            with open(self.tokenPath, "r", encoding="utf-8") as f:
                self.tokendata = json.load(f)
                print("读取.PixivToken.json成功~")
        except Exception as e:
            print(".PixivToken.json载入失败,请检查内容并重新启动~\r\n{}".format(e))
            sys.exit(0)
        if self.tokendata["refresh_token"] == "":
            print("PixivToken不存在")
            sys.exit(0)
        if "time" not in self.tokendata.keys():  # 没time字段就是第一次启动
            self.continue_refresh_token()
            return
        if time.time() - self.tokendata["time"] >= int(
                self.tokendata["expires_in"]
        ):  # 停止程序后再次启动时间后的间隔时间超过刷新间隔
            self.continue_refresh_token()
            return
        self.addJob(
            int(self.tokendata["expires_in"] - (time.time() - self.tokendata["time"]))
        )
