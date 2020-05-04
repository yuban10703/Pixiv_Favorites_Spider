from PIL import Image
import os
import json

'''
webp转换成base64发出去后电脑端QQ不显示
所以转换一下再发....
文件夹中除了图片别的不能有哦~
'''
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.loads(f.read())
    print('获取配置成功')
path = config['download_path']  # 需要转换的路径,就是下载路径
to_path = config['conversion_path']  # 转换后的存储路径

list = os.listdir(path)
to_list = os.listdir(to_path)
for file_names in list:  # 找出所有的后缀为bmp的格式的图片
    if file_names not in to_list:
        file_path = path + file_names  # 拼接出图片的完整url
        out_path = to_path + file_names
        print(out_path)
        Image.open(file_path).save(out_path)
    else:
        print('已转换过~')
print('转换成功')
