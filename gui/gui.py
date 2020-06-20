from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import json
import pymongo

with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    config = json.loads(f.read())
    print('获取配置成功')
path = config['path']
myclient = pymongo.MongoClient(config['mongodb'])  # 数据库地址
mydb = myclient[config['database']]  # 数据库
setu_all = mydb[config['collection']]  # 集合
setu_del = mydb[config['collection_del']]  # 集合


class App:
    def __init__(self, master):
        self.window = master
        '''定义窗口'''
        self.window.title("手动筛色图 Ver2.1")
        # self.window.geometry("800x550")
        width = 800
        height = 550
        '''初始化变量'''
        self.pic = '1.jpg'
        self.num = 5
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
        jumpframe = Frame(self.window)
        jumpframe_filename = Frame(self.window)
        display_filename = Frame(self.window)
        picframe.pack()
        infoframe.pack(side=LEFT)
        inputframe.pack(side=TOP)
        taglist.pack(side=TOP)
        jumpframe.pack(side=TOP)
        jumpframe_filename.pack(side=TOP)
        display_filename.pack(side=TOP)
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
        '''tag输入框'''
        self.window.inputlable = Label(inputframe, text="增加标签:")
        self.window.inputlable.pack(side=LEFT)
        self.window.inputentry = Entry(inputframe)
        self.window.inputentry.pack(side=LEFT)
        '''跳转'''
        self.window.jumpinput = Label(jumpframe_filename, text="filename跳转:")
        self.window.jumpinput_id = Label(jumpframe, text="_id跳转:")
        self.window.jumpinput.pack(side=LEFT)
        self.window.jumpinput_id.pack(side=LEFT)
        self.window.jump_inputentry = Entry(jumpframe_filename)
        self.window.jump_inputentry_id = Entry(jumpframe)
        self.window.jump_inputentry.pack(side=LEFT)
        self.window.jump_inputentry_id.pack(side=LEFT)
        # self.window.inputlable.pack()
        '''类型显示'''
        self.type_text = StringVar()
        self.window.pic_type = Label(display_filename, textvariable=self.type_text, font=(None, 25))
        self.window.pic_type.pack()
        '''tag列表'''
        self.window.del_tag = Button(taglist, text="删除tag", fg='red',
                                     command=lambda: self.del_tag())
        self.window.del_tag.pack(side=BOTTOM, fill=BOTH)
        self.window.save_tag = Button(taglist, text="保存", fg='red',
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
                                   command=lambda: self.del_data())
        self.window.delet.pack(side=LEFT, padx=6)
        self.window.normal_button = Button(buttframe, text="normal",
                                           command=lambda: self.change_tag(want_type='normal'))
        self.window.normal_button.pack(side=LEFT, padx=6)
        self.window.sexy_button = Button(buttframe, text="sexy",
                                         command=lambda: self.change_tag(want_type='sexy'))
        self.window.sexy_button.pack(side=LEFT, padx=6)
        self.window.porn_button = Button(buttframe, text="porn",
                                         command=lambda: self.change_tag(want_type='porn'))
        self.window.porn_button.pack(side=LEFT, padx=6)
        self.window.protocol('WM_DELETE_WINDOW', self.warning)  # 退出提示
        '''获取窗口大小'''
        self.window.update()  # 刷新窗口，这一点很重要，如果设置完宽高不进行刷新，获取的数据是不准确的
        self.Width = self.window.winfo_width()  # 返回tk窗口对象的宽度
        self.Height = self.window.winfo_height()  # 返回tk窗口对象的高度
        '''按键绑定'''
        self.window.bind("<Right>", self.handlerAdaptor(self.next))  # 方向右键
        self.window.bind("<Left>", self.handlerAdaptor(self.previous))  # 方向左键
        self.window.bind("<Delete>", self.handlerAdaptor(self.del_data))  # del
        self.window.inputentry.bind("<Return>", self.handlerAdaptor(self.add_tag))  # 在输入框里按下回车增加tag
        self.window.jump_inputentry.bind("<Return>", self.handlerAdaptor(self.dump))  # 在输入框里按下回车增加tag
        self.window.jump_inputentry_id.bind("<Return>", self.handlerAdaptor(self.dump_id))  # 在输入框里按下回车增加tag
        self.window.taglist.bind("<Double-Button-1>", self.handlerAdaptor(self.del_tag))  # 双击tag删除
        self.window.bind("<z>", self.handlerAdaptor(self.change_tag, want_type='normal'))  # z
        self.window.bind("<x>", self.handlerAdaptor(self.change_tag, want_type='sexy'))  # z
        self.window.bind("<c>", self.handlerAdaptor(self.change_tag, want_type='porn'))  # z
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
        self.window.inputentry.delete(0, 'end')  # 清空输入
        if len(tag) == 0 or tag.isspace():
            tkinter.messagebox.showwarning('???', '输入空标签是什么意思?')  # 弹窗警告
            return
        self.data['tags'].append(tag.strip())  # 往列表增加内容,并去掉两端空格
        print(self.data)
        self.refresh()  # 刷新列表

    def dump(self, event=None):
        filename = self.window.jump_inputentry.get()
        self.window.jump_inputentry.delete(0, 'end')  # 清空输入
        if len(filename) == 0 or filename.isspace():
            tkinter.messagebox.showwarning('???', '什么意思?')  # 弹窗警告
            return
        self.data = setu_all.find_one({'filename': filename})
        self.pic = path + self.data['filename']
        self.refresh()

    def dump_id(self, event=None):
        id = self.window.jump_inputentry_id.get()
        self.window.jump_inputentry_id.delete(0, 'end')  # 清空输入
        if len(id) == 0 or id.isspace() or (not id.isdigit()):
            tkinter.messagebox.showwarning('???', '什么意思?')  # 弹窗警告
            return
        self.num = int(id)
        self.data = setu_all.find_one({'_id': int(id)})
        self.pic = path + self.data['filename']
        self.refresh()

    def del_tag(self, event=None):
        if tkinter.messagebox.askokcancel('tag', '红豆泥?'):
            items = self.window.taglist.curselection()[0]
            # print(items)
            del self.data['tags'][items]
            self.updata_taglist()
            # a = self.window.taglist.get(self.window.taglist.curselection())
            # print(a)

    def previous(self, event=None):  # 键盘绑定后会传入一个参数,但是又用不到这个参数......,而且必须有这个参数....
        # self.num -= 1
        previous_data = setu_all.find({'_id': {'$lt': self.num}}).sort('_id', -1).limit(1)
        self.data = list(previous_data)[0]
        # print(self.data)
        self.num = self.data['_id']
        self.pic = path + self.data['filename']
        self.refresh()
        # tkinter.messagebox.showinfo('别翻了', '一滴都没有了~')

    def next(self, event=None):
        next_data = setu_all.find({'_id': {'$gt': self.num}}).sort('_id', 1).limit(1)
        self.data = list(next_data)[0]
        self.num = self.data['_id']
        self.pic = path + self.data['filename']
        self.refresh()

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
        res = setu_all.update_one({'_id': self.data['_id']},
                                  {'$set': {'tags': self.data['tags']}})
        print('更新数量:{}'.format(res.matched_count))
        return

    def change_tag(self, event=None, want_type=''):
        # print(self.data)
        if tkinter.messagebox.askokcancel(want_type, '红豆泥?'):
            res = setu_all.update_one({'_id': self.data['_id']},  # 更新数据库信息
                                      {'$set': {'type': want_type}})
            self.data['type'] = want_type  # 改变本地变量
            self.refresh()
            print('更新数量:{}'.format(res.matched_count))

    def del_data(self, event=None):
        if tkinter.messagebox.askokcancel('删除', '红豆泥??'):
            res = setu_all.delete_one({'_id': self.data['_id']})  # 从数据库删除
            res_del = setu_del.insert_one(
                {'filename': self.data['filename'], 'artwork': self.data['artwork']})  # 记录文件名,下次爬取不再存入
            print('删除数量:{}  {}'.format(res.deleted_count, res_del.inserted_id))
        return

    def refresh(self):
        self.setu_info()
        self.updata_taglist()
        self.update_pic()
        self.type_text.set(self.data['type'])

    def setu_info(self):
        self.window.text_info.configure(state='normal')  # 设置text可写
        self.window.text_info.delete('1.0', 'end')  # 清除内容
        self.window.text_info.insert('end', self.data)  # 插入数据
        self.window.text_info.configure(state='disabled')  # 设置只读


root = Tk()

app = App(root)
root.mainloop()
