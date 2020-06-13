from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import requests


class App:
    def __init__(self, master):
        self.window = master
        '''定义窗口'''
        self.window.title("手动筛色图 Ver1.0")
        # self.window.geometry("800x550")
        width = 800
        height = 550
        '''初始化变量'''
        self.pic = '1.jpg'
        self.num = 10
        self.collection = 'normal'
        self.data = None
        '''获取屏幕尺寸以计算布局参数，使窗口居屏幕中央'''
        screenwidth = self.window.winfo_screenwidth()
        screenheight = self.window.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.window.geometry(alignstr)
        self.window.resizable(width=True, height=True)
        '''检测窗口大小并缩放图片'''
        self.window.bind('<Configure>', self._resize)
        '''定义容器'''
        butt1frame = Frame(self.window)
        buttframe = Frame(self.window)
        picframe = Frame(self.window)
        infoframe = Frame(self.window)
        inputframe = Frame(self.window)
        taglist = Frame(self.window)
        picframe.pack()
        infoframe.pack(side=LEFT)
        inputframe.pack(side=TOP)
        taglist.pack(side=TOP)
        buttframe.pack(side=BOTTOM, pady=15)
        butt1frame.pack(side=BOTTOM)

        '''图片'''
        # self.photo = PhotoImage(file="2.gif")
        self.window.pic_label = Label(infoframe)  # 图片显示框
        # self.pic_label.photo = photo
        self.window.pic_label.pack()
        '''文本框'''
        self.window.text_info = Text(infoframe)
        self.window.text_info.pack(side=TOP)
        '''输入框'''
        self.window.inputlable = Label(inputframe, text="增加标签")
        self.window.inputlable.pack(side=LEFT)
        self.window.inputentry = Entry(inputframe)
        self.window.inputentry.pack(side=LEFT)
        # self.window.inputlable.pack()
        '''tag列表'''
        self.window.del_tag = Button(taglist, text="删除tag",fg='red',
                                         command=lambda: self.del_tag())
        self.window.del_tag.pack(side=BOTTOM, fill=BOTH)
        self.window.save_tag = Button(taglist, text="保存",fg='red',
                                         command=lambda: self.replace())
        self.window.save_tag.pack(side=BOTTOM, fill=BOTH)
        self.window.inputlable = Label(taglist, text="TAGS:")
        self.window.inputlable.pack(side=LEFT)
        self.window.tagbar = Scrollbar(taglist)  # 垂直滚动条组件
        self.window.tagbar.pack(side=RIGHT, fill=Y)  # 设置垂直滚动条显示的位置
        self.window.taglist = Listbox(taglist, yscrollcommand=self.window.tagbar.set)  # Listbox组件添加Scrollbar组件的set()方法
        self.window.taglist.pack(side=TOP, fill=BOTH)
        self.window.tagbar.config(command=self.window.taglist.yview)  # 设置Scrollbar组件的command选项为该组件的yview()方法
        '''按钮之类的'''
        self.window.previous = Button(butt1frame, text="上一张", command=self.previous)
        self.window.previous.pack(side=LEFT, padx=6)
        self.window.next = Button(butt1frame, text="下一张", command=self.next)
        self.window.next.pack(side=LEFT, padx=6)
        self.window.delet = Button(butt1frame, text="删除", fg='red',
                                   command=lambda: self.move_api(col=self.collection, to_col=''))
        self.window.delet.pack(side=LEFT, padx=6)
        self.window.normal_button = Button(buttframe, text="normal",
                                           command=lambda: self.move_api(self.collection, 'normal'))
        self.window.normal_button.pack(side=LEFT, padx=6)
        self.window.sexy_button = Button(buttframe, text="sexy",
                                         command=lambda: self.move_api(col=self.collection, to_col='sexy'))
        self.window.sexy_button.pack(side=LEFT, padx=6)
        self.window.porn_button = Button(buttframe, text="porn",
                                         command=lambda: self.move_api(col=self.collection, to_col='porn'))
        self.window.porn_button.pack(side=LEFT, padx=6)
        self.window.protocol('WM_DELETE_WINDOW', self.warning)  # 退出提示
        '''获取窗口大小'''
        self.window.update()  # 刷新窗口，这一点很重要，如果设置完宽高不进行刷新，获取的数据是不准确的
        self.Width = self.window.winfo_width()  # 返回tk窗口对象的宽度
        self.Height = self.window.winfo_height()  # 返回tk窗口对象的高度
        '''按键绑定'''
        self.window.bind("<Right>", self.handlerAdaptor(self.next))  # 方向右键
        self.window.bind("<Left>", self.handlerAdaptor(self.previous))  # 方向左键
        self.window.bind("<Delete>", self.handlerAdaptor(self.move_api, col=self.collection, to_col=''))  # del
        self.window.inputentry.bind("<Return>", self.handlerAdaptor(self.add_tag))  #在输入框里按下回车增加tag
        self.window.taglist.bind("<Double-Button-1>", self.handlerAdaptor(self.del_tag))  #在输入框里按下del删除tag
        # self.window.bind("<Key>", self.handlerAdaptor)
        # self.window.bind("<Key>", self.handlerAdaptor)

    def handlerAdaptor(self, fun, **kwds):
        '''事件处理函数的适配器，相当于中介，那个event是从那里来的呢，我也纳闷，这也许就是python的伟大之处吧'''
        return lambda event, fun=fun, kwds=kwds: fun(event, **kwds)

    def warning(self):  # 退出时提示
        if tkinter.messagebox.askokcancel('┬＿┬', '真的要退出吗? (╥╯^╰╥)'):
            root.destroy()

    def add_tag(self, event=None):
        tag = self.window.inputentry.get()
        self.window.inputentry.delete(0, 'end') #清空输入
        if len(tag) == 0 or tag.isspace():
            tkinter.messagebox.showwarning('???', '输入空标签是什么意思?')  # 弹窗警告
            return
        self.data['tags'].append(tag.strip())  # 往列表增加内容,并去掉两端空格
        print(self.data)
        self.updata_taglist()  # 刷新列表

    def del_tag(self,event=None):
        if tkinter.messagebox.askokcancel('tag', '红豆泥?'):
            items = self.window.taglist.curselection()[0]
            # print(items)
            del self.data['tags'][items]
            self.updata_taglist()
            # a = self.window.taglist.get(self.window.taglist.curselection())
            # print(a)
    def previous(self, event=None):  # 键盘绑定后会传入一个参数,但是又用不到这个参数......,而且必须有这个参数....
        self.num -= 1
        while True:
            try:
                if self.num <= 0:  # 如果_id小于等于0就停止
                    tkinter.messagebox.showinfo('别翻了', '一滴都没有了~')
                    break
                self.getapi()
                break
            except:
                self.num -= 1
        self.update_pic()

    def next(self, event=None):
        self.num += 1
        num = 0
        while True:
            try:
                if num >= 8:  # 错误
                    tkinter.messagebox.showinfo('别翻了', '一滴都没有了~')
                    break
                self.getapi()
                break
            except:
                num += 1
                self.num += 1
        self.update_pic()

    def updata_taglist(self):
        self.window.taglist.delete(0, END)
        for i in self.data['tags']:
            self.window.taglist.insert(END, i)
        # print(self.data['tags'])

    def _resize(self, event):  # 图片和窗口等比例缩放
        self.Width = self.window.winfo_width()  # 返回tk窗口对象的宽度
        self.Height = self.window.winfo_height()  # 返回tk窗口对象的高度
        self.update_pic()

    def update_pic(self):
        image = Image.open(self.pic)  # 打开图片
        '''处理图片'''
        newWidth = round(self.Width * 0.3)
        w, h = image.size
        newHeight = round(newWidth / w * h)

        image = image.resize((newWidth, newHeight), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.window.pic_label.configure(image=photo)
        self.window.pic_label.photo = photo  # 防止被回收??
        self.window.pic_label.pack()
        self.window.update_idletasks()
    def replace(self):
        url = 'http://127.0.0.1:8000/replace'
        data = {"data": self.data,
                "collection": self.collection}
        res = requests.post(url, json=data)
        print(res)
    def getapi(self):
        url = 'http://127.0.0.1:8000/get'
        data = {"data": self.num,
                "collection": self.collection}
        res = requests.post(url, json=data)
        setu_data = res.json()
        print(setu_data)
        if setu_data != None:
            self.pic = 'Y:\\PICS\\' + setu_data['filename']
            self.data = setu_data
            self.setu_info()
            self.updata_taglist()
        else:
            raise

    def move_api(self, event=None, col='', to_col=''):
        # print(self.data)
        if tkinter.messagebox.askokcancel(to_col, '红豆泥?'):
            url = 'http://127.0.0.1:8000/move'
            data = {"data": self.data,
                    "collection": col,
                    "to_collection": to_col}
            print(data)
            res = requests.post(url, json=data)
            setu_data = res.json()
            print(setu_data)

    def setu_info(self):
        self.window.text_info.configure(state='normal')  # 设置text可写
        self.window.text_info.delete('1.0', 'end')  # 清除内容
        self.window.text_info.insert('end', self.data)  # 插入数据
        self.window.text_info.configure(state='disabled')  # 设置只读


root = Tk()

app = App(root)
root.mainloop()