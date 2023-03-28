# encoding=utf-8
# Author：Wentao Zheng
# E-mail: swjtu_zwt@163.com
# developed time: 2023/1/30 22:36
from tkinter import *
from tkinter import filedialog
import tkinter
from tkinter import tix
from tkinter.tix import Tk, Control, ComboBox  # 升级的组合控件包
from tkinter.messagebox import showinfo, showwarning, showerror  # 各种类型的提示框

import numpy as np


class Interface:
    def __init__(self):
        self.infoscenario = ""
        self.infotrajectory=""
        self.infoeval=""

    def select_directory1(self, text) -> None:
        folder_path = filedialog.askdirectory()
        text.insert('insert', folder_path)
        # if folder_path!="":
        #     self.infoscenario=folder_path

        return None

    def select_directory2(self, text) -> None:
        folder_path = filedialog.askdirectory()
        text.insert('insert', folder_path)
        #self.infotrajectory.append(folder_path)
        return None
    def select_directory3(self, text) -> None:
        folder_path = filedialog.askdirectory()
        text.insert('insert', folder_path)
        #self.infoeval.append(folder_path)
        return None

    def select_file(self, text) -> None:
        file_path = filedialog.askopenfilename()
        text.insert('insert', file_path)
        self.info.append(file_path)
        return None

    @staticmethod
    def click_button():
        windows = tix.Tk()
        windows.title('温馨提示')
        windows.geometry("300x50")
        tkinter.Button(windows, text='输出评价结果', command=windows.quit).pack(side='top')

    @staticmethod
    def process_eval(c):
        windows = tix.Tk()
        windows.title('温馨提示')
        windows.geometry("300x50")
        Label(windows,text=c, bd=10, font=("Arial", 10),width=10, height=3).grid(row=0, column=0)


    def change_state(self, entry):
        var = entry.get()  # 调用get()方法，将Entry中的内容获取出来
        self.info.append(var)

    def interface_making(self):
        windows = tix.Tk()
        windows.title("onsite_评价工具")  # 设置窗口标题
        windows.geometry("550x250")  # 设置窗口大小 注意：是x 不是*
        windows.resizable(width=True, height=True)  # 设置窗口是否可以变化长/宽，False不可变，True可变，默认为True
        windows.tk.eval('package require Tix')  # 引入升级包，这样才能使用升级的组合控件
        windows.iconphoto(True, tkinter.PhotoImage(file='onsite.png'))

        # label
        Label(windows, text="场景文件位置", bd=10, font=("Arial", 10),
              width=10, height=3).grid(row=0, column=0)

        Label(windows, text="轨迹文件位置", bd=10, font=("Arial", 10),
              width=10, height=3).grid(row=1, column=0)

        # Label(windows, text="interval", bd=10, font=("Arial", 12),
        #      width=10, height=3).grid(row=2, column=0)

        Label(windows, text="输出文件位置", bd=10, font=("Arial", 10),
              width=10, height=3).grid(row=3, column=0)

        # Label(windows, text="是否需要输出详细信息(True/False)", bd=10, font=("Arial", 12),
        #       width=30, height=3).grid(row=4, column=0)

        # text
        text1 = Entry(windows, width=44, font=('宋体', 10))
        text1.grid(row=0, column=2)


        text2 = Entry(windows, width=44, font=('宋体', 10))
        text2.grid(row=1, column=2)

        text3 = Entry(windows, width=44,  font=('宋体', 10))
        text3.grid(row=3, column=2)

        #entry
        # entry1 = Entry(windows, width=44,  font=('宋体', 10))
        # entry1.grid(row=0, column=2)


        # button
        button = Button(windows, text='选择场景文件位置', command=lambda: self.select_directory1(text1)
                        , activeforeground="black",
                        activebackground='grey',
                        fg='black')
        button.grid(row=0, column=4)

        button = Button(windows, text='选择轨迹文件位置', command=lambda: self.select_directory2(text2)
                        , activeforeground="black",
                        activebackground='grey',
                        fg='black')
        button.grid(row=1, column=4)

        # button = Button(windows, text='确定interval', command=lambda: self.change_state(entry1)
                        # , activeforeground="black",
                        # activebackground='grey',
                        # fg='black')
        # button.grid(row=2, column=4)

        button = Button(windows, text='选择输出文件位置', command=lambda: self.select_directory3(text3)
                        , activeforeground="black",
                        activebackground='grey',
                        fg='black')
        button.grid(row=3, column=4)

        # button = Button(windows, text='确定', command=lambda: self.change_state(entry2)
                        # , activeforeground="black",
                        # activebackground='grey',
                        # fg='black')
        # button.grid(row=4, column=4)

        button = Button(windows, text='完成配置，开始评价', command=lambda: self.click_button()
                        , activeforeground="black",
                        activebackground='grey',
                        fg='black')
        button.grid(row=5, column=2)

        windows.mainloop()
        self.infoscenario=text1.get()
        self.infotrajectory = text2.get()
        self.infoeval = text3.get()
        return self.infoscenario,self.infotrajectory,self.infoeval


if __name__ == "__main__":
    interface = Interface()
    infoscenario,infotrajectory,infoeval = interface.interface_making()
    #print(infoscenario,infotrajectory,infoeval)