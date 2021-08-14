import copy
import json
import time
from functools import lru_cache
from io import BytesIO
from threading import Thread

import httpx
from PIL import Image
from PySide2 import QtGui
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMessageBox

from database import DataBase


# 屎山

class Stats():

    def __init__(self):
        self.session = httpx.Client()
        self.ui = QUiLoader().load('ui2.ui')

        # self.ui.label.setScaledContents(True)  # 图片大小自适应
        # 按钮对应事件
        self.ui.sexy.clicked.connect(lambda: self.change_r18_level(False))
        self.ui.porn.clicked.connect(lambda: self.change_r18_level(True))
        self.ui.addtag.clicked.connect(self.addtag)
        self.ui.deltag.clicked.connect(self.deltag)
        self.ui.previous.clicked.connect(self.previous)
        self.ui.next.clicked.connect(self.next)
        self.ui.R18.clicked.connect(self.next_R18)
        self.ui.NOTR18.clicked.connect(self.next_not_R18)
        self.ui.reset.clicked.connect(self.reset)
        self.ui.savetag.clicked.connect(self.savetag)
        self.ui.delet.clicked.connect(self.delet)
        self.ui.noFiltrate.clicked.connect(self.jump_to_noFiltrate)
        # 回车事件
        self.ui.idedit.returnPressed.connect(self.jumpID)
        self.ui.pidedit.returnPressed.connect(self.jumpPid)
        self.ui.pageedit.returnPressed.connect(self.jumpPid)
        self.ui.taginput.returnPressed.connect(self.addtag)

        # 数据
        self.data = {'_id': '610fd717abf9ac91bca84727'}
        # self.data_raw = {'_id': '610fd717abf9ac91bca84727'}  # 禁止修改
        self.data_raw = DataBase.init_gui()  # 禁止修改
        self.reset()
        # test
        # 初始化界面
        self.init()

    def showSetuinfo(func):
        # @wraps(func)
        def wrapper(self, *args, **kwargs):
            print('刷新界面')
            func(self, *args, **kwargs)
            self.ui.picinfo.clear()
            print(self.data)
            self.data["_id"] = str(self.data["_id"])
            self.data['create_date'] = str(self.data['create_date'])
            self.ui.picinfo.append(str(json.dumps(self.data, indent=2, ensure_ascii=False)))
            self.ui.taglist.clear()
            self.ui.taglist.addItems(self.data['tags'])
            self.ui.modified_count.setNum(DataBase.modified_count())
            self.ui.unmodified_count.setNum(DataBase.unmodified_count())
            self.ui.r18.setText('R18:{}'.format(self.data['r18']))
            self.ui.sanity_level.setText('sanity_level:{}'.format(self.data['sanity_level']))

        return wrapper

    def init(self):
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()

    def copy(self):
        self.data = copy.deepcopy(self.data_raw)

    @showSetuinfo
    def reset(self):
        self.copy()
        # self.showSetuinfo()

    def savetag(self):
        print('增加TAG:{}'.format(list(set(self.data['tags']).difference(set(self.data_raw['tags'])))))
        print('移除TAG:{}'.format(list(set(self.data_raw['tags']).difference(set(self.data['tags'])))))
        DataBase.updateTags(self.data_raw['_id'], self.data['tags'])

    def delet(self):
        reply = QMessageBox.question(self.ui, 'Message', '是否删除?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            print('删除数量{}'.format(
                DataBase.delsetu(self.data_raw['_id'], self.data_raw['artwork']['id'], self.data_raw['page'])))
        elif reply == QMessageBox.No:
            pass

    @showSetuinfo
    def change_r18_level(self, level: bool):
        print('r18:{}'.format(level))
        res = DataBase.updateType(self.data_raw['_id'], level)
        print('更新数量:{}'.format(res))
        self.data['r18'] = level
        # self.showSetuinfo()

    @showSetuinfo
    def addtag(self):
        if tag := self.ui.taginput.text():
            self.data['tags'].append(tag)
            self.ui.taginput.clear()
            # self.showSetuinfo()

    @showSetuinfo
    def deltag(self):
        if tag := self.ui.taglist.currentItem().text():  # 当前选中的tag
            self.data['tags'].remove(tag)  # 移除
            # self.showSetuinfo()

    @showSetuinfo
    def previous(self):
        self.data_raw = DataBase.previous(self.data_raw['_id'])
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()

    @showSetuinfo
    def next(self):
        self.data_raw = DataBase.next(self.data_raw['_id'])
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()

    @showSetuinfo
    def next_R18(self):
        self.data_raw = DataBase.next_r18(self.data_raw['_id'])
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()

    @showSetuinfo
    def next_not_R18(self):
        self.data_raw = DataBase.next_not_r18(self.data_raw['_id'])
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()

    @lru_cache(maxsize=10)  # 缓存5张图片?
    def downloadPic(self, url):
        print('我真的在下载')
        res = self.session.get(url, headers={'Referer': 'https://www.pixiv.net'})
        if res.status_code == 200:
            return res.content
        else:
            print(res.status_code)

    def changePic(self, url):
        pixmap = QtGui.QPixmap()
        start = time.time()
        pixmap.loadFromData(self.resize(self.ui.label.width(), self.ui.label.height(), self.downloadPic(url)))
        print('下载耗时{}s'.format(time.time() - start))
        self.ui.label.setPixmap(pixmap)
        Thread(target=self.downloadPic, args=(DataBase.next(self.data_raw['_id'])['urls']['large'],)).start()

    def resize(self, w_box, h_box, pic_bf):
        '''
        resize a pil_image object so it will fit into
        a box of size w_box times h_box, but retain aspect ratio
        对一个pil_image对象进行缩放，让它在一个矩形框内，还能保持比例
        '''
        with Image.open(BytesIO(pic_bf)) as pic:
            w, h = pic.size
            print(w, h)
            f1 = 1.0 * w_box / w  # 1.0 forces float division in Python2
            f2 = 1.0 * h_box / h
            factor = min([f1, f2])
            # print(f1, f2, factor) # test
            # use best down-sizing filter
            width = int(w * factor)
            height = int(h * factor)
            pic.resize((width, height), Image.ANTIALIAS)
            # pic.scaled((width, height))
            with BytesIO() as bf:
                pic.save(bf, format="PNG")
                return bf.getvalue()

    @showSetuinfo
    def jumpID(self):
        # if self.checktype(self.ui.idedit.text()):
        self.data_raw = DataBase.getdata(self.ui.idedit.text())
        self.ui.idedit.clear()
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()
        # else:
        #     QMessageBox().warning(self.ui, '!', '检查输入')
        #     return

    def checktype(self, data: str):
        try:
            int(data)
            return True
        except:
            return False

    @showSetuinfo
    def jumpPid(self):
        if (len(self.ui.pidedit.text()) == 0) or (self.ui.pidedit.text().isspace()):
            QMessageBox().information(self.ui, '?', '请输入pid')
            return
        if (len(self.ui.pageedit.text()) == 0) or (self.ui.pageedit.text().isspace()):
            if self.checktype(self.ui.pidedit.text()):
                data = DataBase.find(int(self.ui.pidedit.text()))
            else:
                QMessageBox().warning(self.ui, '!', '检查输入')
                return
        else:
            if self.checktype(self.ui.pidedit.text()) and self.checktype(self.ui.pageedit.text()):
                pid = int(self.ui.pidedit.text())
                page = int(self.ui.pageedit.text())
                data = DataBase.find(pid, page)
            else:
                QMessageBox().warning(self.ui, '!', '检查输入')
                return
        self.ui.pidedit.clear()
        self.ui.pageedit.clear()
        if data is None:
            QMessageBox().information(self.ui, '?', '无数据')
            return
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()
        # self.showSetuinfo()

    @showSetuinfo
    def jump_to_noFiltrate(self):
        self.data_raw = DataBase.noFiltrate()
        Thread(target=self.changePic, args=(self.data_raw['urls']['large'],)).start()
        self.copy()

    def test(self):
        print(self.ui.idedit.text())
        print(self.ui.label.height())
        print(self.ui.label.width())
        self.ui.idedit.clear()


app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()
