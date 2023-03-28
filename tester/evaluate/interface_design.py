# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/2/4 8:57
from tkinter import *


class Application(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.grid()
        self.createWidget()

    def createWidget(self):
        global photo
        photo = PhotoImage(file='GUI_fig/label_1.gif')
        Label(self, image=photo, borderwidth=1, relief='solid').grid(row=0, column=0, rowspan=3, columnspan=2, sticky=EW)

        Button(root, text='评价工具', borderwidth=1, relief='solid', command=self.enter_interface).grid(row=2, column=0, columnspan=2, sticky=EW)
        Label(self, text="场景文件位置", bd=10, font=("Arial", 12),
              width=10, height=3).grid(row=2, column=4)

        Label(self, text="轨迹文件位置", bd=10, font=("Arial", 12),
              width=10, height=3).grid(row=3, column=4)

        Label(self, text="interval", bd=10, font=("Arial", 12),
              width=10, height=3).grid(row=4, column=4)

        Label(self, text="输出文件位置", bd=10, font=("Arial", 12),
              width=10, height=3).grid(row=5, column=4)

        Label(self, text="是否需要输出详细信息(True/False)", bd=10, font=("Arial", 12),
              width=30, height=3).grid(row=6, column=4)

    def enter_interface(self):
        pass


if __name__ == "__main__":
    root = Tk()
    root.geometry("1200x600+200+100")
    root.title('onsite_评价工具')
    app = Application(master=root)
    root.mainloop()
