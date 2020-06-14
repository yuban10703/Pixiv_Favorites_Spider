## 色图库用到的所有东西

用mongodb储存从pixiv上爬下来的数据

spider文件夹里是爬虫,从P站的公开收藏夹爬图到数据库里

select里是筛图的脚本和一个下载脚本,用腾讯ai的鉴黄api给数据库里的数据打标签

gui里是一个手动筛图的gui..

api里是给qqbot调用的api



### config

| config     |                |
| ---------- | -------------- |
| mongodb    | 数据库地址     |
| database   | 数据库         |
| collection | 数据表         |
| path       | 下载的色图路径 |
| APPKEY     | 腾讯ai的appkey |
| APPID      | 腾讯ai的appid  |
| username   | pixiv的用户名  |
| password   | pixiv的密码    |

爬下来的数据:
![image-20200614113034532](https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/20200614113034.png)

简陋的gui:

![image-20200614113234090](https://cdn.jsdelivr.net/gh/yuban10703/BlogImgdata/img/20200614113234.png)

有问题可以提iss..