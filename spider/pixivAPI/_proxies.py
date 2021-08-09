import json
import sys
from pathlib import Path

from httpx_socks import SyncProxyTransport

try:
    with open(Path(__file__).absolute().parent.parent / "config" / "proxies.json", "r", encoding="utf-8") as f:
        proxiesConfig = json.load(f)
        print("读取proxies.json成功~")
except Exception as e:
    print("proxies.json载入失败,请检查内容并重新启动~\r\n{}".format(e))
    sys.exit(0)

if proxies_socks := proxiesConfig.get("proxies_socks"):
    transport = SyncProxyTransport.from_url(proxies_socks)
    proxies = None
else:
    transport = None
    proxies = proxiesConfig.get("proxies_http")
