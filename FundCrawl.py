import pandas as pd
import sys
from PIL import Image
from PyQt5 import QtCore, QtGui, QtWidgets
import logging
from Fund import *
from PyQt5.QtGui import QColor, QBrush
import webbrowser
from PyQt5.QtWidgets import (QLabel,QMenu, QPushButton, QWidget, QTableWidget, QVBoxLayout,QHBoxLayout, QApplication, QTableWidgetItem,
 QHeaderView)
from PyQt5.QtCore import Qt
#import Numba
import os
import cv2
import requests
from selenium import webdriver
from time import sleep
from selenium.webdriver import ActionChains
#实现规避检测
from selenium.webdriver import ChromeOptions
import shutil
import threading
from selenium.webdriver import Remote
from selenium.webdriver.chrome import options
from selenium.common.exceptions import InvalidArgumentException
'''
功能实现:
基金查询功能 √
历史查询基金 数据展示 √
随意删除数据 √
可通过各种异常处理 对症下药 抓取任意类型基金数据 √
可容纳大量基金数据 ×
未对接数据库 (wait)
 
'''

'''
当QScrollArea的宽或高，一旦小于scorllAreaWidgetContents的宽或高，就会出现滚动条。
scrollAreaWidgetContents 就是滚动层了，设置内部区域的大小，默认是跟外层一边大的。
外层 scrollArea 是设置展示区域的大小。


★★★★★★★★★★
控件自适应的方法:
布局对象 应继承 需要该布局排列小组件的父类组件
组件 继承 (父类组件)
布局要添加(addWidget)它所继承的组件 的 子组件
★★★★★★★★★★
'''

#125 一个格

#扩大表格scrollarea不用改变  scrollareawidgets 需要扩大宽和高  tablewidgets也需扩大宽高
class ReuseChrome(Remote):

    def __init__(self, command_executor, session_id):
        self.r_session_id = session_id
        Remote.__init__(self, command_executor=command_executor, desired_capabilities={})

    def start_session(self, capabilities, browser_profile=None):
        """
        重写start_session方法
        """
        if not isinstance(capabilities, dict):
            raise InvalidArgumentException("Capabilities must be a dictionary")
        if browser_profile:
            if "moz:firefoxOptions" in capabilities:
                capabilities["moz:firefoxOptions"]["profile"] = browser_profile.encoded
            else:
                capabilities.update({'firefox_profile': browser_profile.encoded})

        self.capabilities = options.Options(m).to_capabilities()
        self.session_id = self.r_session_id
        self.w3c = False

class Ui_MainWindow(object):
    DriverCounter  =  0
    counter = 0  # 定义一个计数器 便于每次查询让行数+1 保证插入的位置正确 即列的索引
    Row = 0 #定义一个计数器 即行的索引 让数据每次从现有记录的下一行开始插入
    def __init__(self):
        super().__init__()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1200,700) #设置初始窗体大小
        MainWindow.setMinimumSize(QtCore.QSize(100,50))
        MainWindow.setMaximumSize(QtCore.QSize(1900,1030))
        font = QtGui.QFont()
        font.setPointSize(9)
        MainWindow.setFont(font)

       # # 设置窗体无边框
       # MainWindow.setWindowFlags(Qt.FramelessWindowHint)
       # # 设置背景透明
       # MainWindow.setAttribute(Qt.WA_TranslucentBackground)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setStyleSheet("")
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(0, 650, 871, 41))
        self.textBrowser.setObjectName("textBrowser")

        #创建标签页控件
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 871, 651))
        self.tabWidget.setTabBarAutoHide(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tabWidget.setMaximumSize(QtCore.QSize(2000,900))

        #创建tab_1
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")

        #为tab_1创建垂直布局 便于frame能根据窗体变化
        self.QVBoxLayout_tab = QVBoxLayout(self.tab)
        self.QVBoxLayout_tab.setObjectName("QVBoxLayout_tab")

        #创建水平布局
        self.horizontalLayout1 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout1.setObjectName("horizontalLayout1")
        self.horizontalLayout1.addWidget((self.tabWidget)) #将标签页控件设置为水平布局

        # 创建frame类 将tab中所有控件装入
        self.frame_tab = QtWidgets.QFrame(self.tab)
        self.frame_tab.setObjectName("frame_tab")
        self.frame_tab.setGeometry(QtCore.QRect(11,11,894,590))
        self.frame_tab.setMinimumSize(QtCore.QSize(400,300))
        self.frame_tab.setMaximumSize(QtCore.QSize(2000, 1100))

        #创建水平布局与小组件的父类组件widget  将3个小控件装进去
        self.widget_tab=QWidget(self.frame_tab)
        self.widget_tab.setObjectName("widget_tab")
        self.widget_tab.setGeometry(QtCore.QRect(12,300,870,280))
        self.widget_tab.setMaximumSize(QtCore.QSize(2000,1200))

        #创建日历控件
        self.calendarWidget = QtWidgets.QCalendarWidget(self.frame_tab)
        self.calendarWidget.setGeometry(QtCore.QRect(12, 12, 870, 280))
        self.calendarWidget.setMinimumSize(QtCore.QSize(400,200))
        self.calendarWidget.setMaximumSize(QtCore.QSize(1920,400))
        self.calendarWidget.setObjectName("calendarWidget")

        self.label = QtWidgets.QLabel(self.widget_tab)
        self.label.setGeometry(QtCore.QRect(11,124,371,30))
        self.label.setMaximumSize(QtCore.QSize(2000,30))
        font = QtGui.QFont()
        font.setFamily("Cambria")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.pushButton = QtWidgets.QPushButton(self.widget_tab)
        self.pushButton.setGeometry(QtCore.QRect(765,125,50,30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setIcon(QtGui.QIcon(r".\icon\搜索.ico"))
        self.pushButton.setFlat(True) #去掉黑色边框
        self.pushButton.setIconSize(QtCore.QSize(90, 55))
        self.pushButton.setMinimumSize(QtCore.QSize(50, 55))
        self.pushButton.setMaximumSize(QtCore.QSize(50, 55))
        self.textEdit = QtWidgets.QTextEdit(self.widget_tab)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setGeometry(QtCore.QRect(389,124,370,30))
        self.textEdit.setMaximumSize(QtCore.QSize(2000,30))
        self.textEdit.setPlaceholderText("第一次查询会发生闪退!第二次查询即可恢复正常")
        self.textEdit.textChanged.connect(self.get_code)

        self.QHBoxLayout_tab=QHBoxLayout(self.widget_tab)
        self.QHBoxLayout_tab.setObjectName("QHBoxLayout_tab")
        # 将三个小组件在widget中的排列布局设置为水平布局
        self.QHBoxLayout_tab.addWidget(self.label)
        self.QHBoxLayout_tab.addWidget(self.textEdit)
        self.QHBoxLayout_tab.addWidget(self.pushButton)

        # 为frame类创建垂直布局 让日历和widget垂直排列
        self.QVBoxLayout_frame = QVBoxLayout(self.frame_tab)
        self.QVBoxLayout_frame.setObjectName("QVBoxLayout_tab")
        self.QVBoxLayout_frame.addWidget(self.calendarWidget)
        self.QVBoxLayout_frame.addWidget(self.widget_tab)

        #将frame添加到tab1的垂直布局当中
        self.QVBoxLayout_tab.addWidget(self.frame_tab)

        self.tabWidget.addTab(self.tab, "")
        #创建tab2
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setMinimumSize(QtCore.QSize(100,100))
        self.tab_2.setMaximumSize(QtCore.QSize(2000,1030))
        self.tab_2.setObjectName("tab_2")

        "创建垂直布局 组件为tablewidget和状态栏 还有更新按钮"
        self.verticalLayout = QVBoxLayout(self.tab_2)
        self.verticalLayout.setObjectName("verticalLayout")

        self.pushButton_tab_2=QPushButton(self.tab_2)
        self.pushButton_tab_2.setObjectName("pushButton_tab_2")
        self.pushButton_tab_2.setMinimumSize(QtCore.QSize(100,40))
        self.pushButton_tab_2.setMaximumSize(QtCore.QSize(1900,40))
        self.pushButton_tab_2.setText("数据更新")
        self.pushButton_tab_2.clicked.connect(self.UpDate)

        self.tableWidget = QtWidgets.QTableWidget(self.tab_2)
        self.tableWidget.setMinimumSize(QtCore.QSize(100, 100))
        self.tableWidget.setMaximumSize(QtCore.QSize(1900, 1000))
        self.tableWidget.setAlternatingRowColors(True) #奇数偶数行 颜色不同
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn) #使滚动条一直存在
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.tableWidget.setObjectName("tableWidget")
        self.verticalLayout.addWidget(self.pushButton_tab_2)  #加入更新按钮
        self.verticalLayout.addWidget(self.tableWidget) #加入表格控件
        self.verticalLayout.addWidget(self.textBrowser) #加入状态栏控件

        self.textBrowser.setMaximumSize(QtCore.QSize(2000,40))

        self.tabWidget.addTab(self.tab_2, "")
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)  ######允许右键产生子菜单
        self.tableWidget.customContextMenuRequested.connect(self.generateMenu)  ####右键菜单

        self.NameList = ["基金代码", "基金名称", "收盘日", "收盘净值", "当前净值", "净值涨幅", "更新时间", "近1周", "近1月", "近3月", "近6月", "今年来", "近1年",
                    "近2年", "近3年"]

        self.tableWidget.setObjectName("tableWidget")

        self.tabWidget.addTab(self.tab_2, "")

        #标签页3
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        ListItemFont = QtGui.QFont()  # 实例化字体样式对象
        ListItemFont.setPointSize(15)
        self.listWidget_tab3 = QtWidgets.QListWidget(self.tab_3)
        self.listWidget_tab3.setObjectName("listWidget_tab3")
        self.listWidget_tab3.setAlternatingRowColors(True)
        self.listWidget_tab3.clicked.connect(self.GotoBrowser) #绑定点击打开浏览器事件
        self.listWidget_tab3.setGeometry(-5, 1, 291, 621)
        self.listWidget_tab3.setMaximumSize(QtCore.QSize(400, 10000))
        self.listWidget_tab3.setGridSize(QtCore.QSize(20, 45))  # 设置行的宽和高
        self.listWidget_tab3.setFont(ListItemFont)  # 设置行对象字体大小

        self.label_tab_3=QLabel(self.tab_3)
        pe = QtGui.QPalette()
        pe.setColor(QtGui.QPalette.WindowText, Qt.red)  # 设置字体颜色
        self.label_tab_3.setFont(QtGui.QFont("Roman times", 16, QtGui.QFont.Bold))  # 设置字体以及 加粗 尺寸
        self.label_tab_3.setText("点击你想了解的基金 即可了解管理该只基金的基金经理!")
        self.label_tab_3.setPalette(pe)

        self.horizontalLayout3 = QHBoxLayout(self.tab_3)
        self.horizontalLayout3.setObjectName("horizontalLayout3")
        self.horizontalLayout3.addWidget(self.listWidget_tab3)
        self.horizontalLayout3.addWidget(self.label_tab_3)

        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget.addTab(self.tab_4, "")

        #在tab_4加入列表控件 便于定向选取基金
        ListItemFont=QtGui.QFont() #实例化字体样式对象
        ListItemFont.setPointSize(15)
        self.listWidget = QtWidgets.QListWidget(self.tab_4)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setGeometry(-5,1,291,621)
        self.listWidget.setMaximumSize(QtCore.QSize(400,10000))
        self.listWidget.setAlternatingRowColors(True) #行色变化
        self.listWidget.setSortingEnabled(True) #可排序
        self.listWidget.setGridSize(QtCore.QSize(20,45)) #设置行的宽和高
        self.listWidget.setFont(ListItemFont) #设置行对象字体大小

        #为tab_4设置水平布局
        self.horizontalLayout2 = QHBoxLayout(self.tab_4)
        self.horizontalLayout2.setObjectName("horizontalLayout2")
        #将列表控件塞到tab4的水平布局中去
        self.horizontalLayout2.addWidget(self.listWidget)
        self.listWidget.itemClicked.connect(self.captureCode) #绑定槽函数 获取代码 从而获取折线图

        #创建一个frame类 与listwidget优先级相同的控件 以便在frame控件中放置小控件
        #再将frame控件也放入tab4的水平布局中 让两个大控件对齐 在为大控件中的小控件设置其他布局
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(500, 0))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        #为frame控件设置垂直布局 容纳按钮 图片等小控件 令小控件从上到下整齐排列
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")

        #为使按钮小控件整齐对齐 再放置一个按钮的父类容纳按钮这些子类小控件
        self.widget_2 = QtWidgets.QWidget(self.frame)
        self.widget_2.setObjectName("widget_2")
        #为2个pushbutton设置水平布局
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget_2)

        self.pushButton_tab_41 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_tab_41.setObjectName("pushButton41")
        self.horizontalLayout_2.addWidget(self.pushButton_tab_41)
        #为第一个pushbutton绑定planA函数 对应A情况
        self.pushButton_tab_41.clicked.connect(self.planA)

        self.pushButton_tab_42 = QtWidgets.QPushButton(self.widget_2)
        self.pushButton_tab_42.setObjectName("pushButton42")
        self.horizontalLayout_2.addWidget(self.pushButton_tab_42)
        #为第二个pushbutton绑定planB函数 对应B情况
        self.pushButton_tab_42.clicked.connect(self.planB)

        #放置一个Label提醒使用者
        self.label_tab_4=QtWidgets.QLabel(self.widget_2)
        self.label_tab_4.setObjectName("Label_tab_4")
        self.horizontalLayout_2.addWidget(self.label_tab_4)
        pe = QtGui.QPalette()
        pe.setColor(QtGui.QPalette.WindowText, Qt.red)  # 设置字体颜色
        self.label_tab_4.setFont(QtGui.QFont("Roman times", 10, QtGui.QFont.Bold)) #设置字体以及 加粗 尺寸
        self.label_tab_4.setText("部分基金上市时间较短 若出现图像错误\n可能是您网络原因造成 多试几次即可 若多次错误 则可能由于该图像不存在\n由于图片均为实时加载 请耐心等待！")
        self.label_tab_4.setPalette(pe)


        self.verticalLayout.addWidget(self.widget_2)
        self.widget = QtWidgets.QWidget(self.frame)
        self.widget.setObjectName("widget")
        # 为7个radiobutton设置水平布局
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.radioButton_1 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_1.setObjectName("radioButton_1")
        self.horizontalLayout.addWidget(self.radioButton_1)
        self.radioButton_2 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_2.setObjectName("radioButton_2")
        self.horizontalLayout.addWidget(self.radioButton_2)
        self.radioButton_3 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_3.setObjectName("radioButton_3")
        self.horizontalLayout.addWidget(self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_4.setObjectName("radioButton_4")
        self.horizontalLayout.addWidget(self.radioButton_4)
        self.radioButton_5 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_5.setObjectName("radioButton_5")
        self.horizontalLayout.addWidget(self.radioButton_5)
        self.radioButton_6 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_6.setObjectName("radioButton_6")
        self.horizontalLayout.addWidget(self.radioButton_6)
        self.radioButton_7 = QtWidgets.QRadioButton(self.widget)
        self.radioButton_7.setObjectName("radioButton_7")
        self.rbtn1 = hex(id(self.radioButton_1))
        self.rbtn2 = hex(id(self.radioButton_2))
        self.rbtn3 = hex(id(self.radioButton_3))
        self.rbtn4 = hex(id(self.radioButton_4))
        self.rbtn5 = hex(id(self.radioButton_5))
        self.rbtn6 = hex(id(self.radioButton_6))
        self.rbtn7 = hex(id(self.radioButton_7))

        self.horizontalLayout.addWidget(self.radioButton_7)

        #将各个小组件的父类组件加入垂直布局
        self.verticalLayout.addWidget(self.widget)
        self.graphicsView = QtWidgets.QGraphicsView(self.frame)
        #self.graphicsView.setStyleSheet("padding: 0px; border: 0px;")  # 内边距和边界去除
        self.graphicsView.setMinimumSize(QtCore.QSize(0, 0))
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout.addWidget(self.graphicsView)
        self.horizontalLayout2.addWidget(self.frame)

        #创建第四个标签页
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")

        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame_2 = QtWidgets.QFrame(self.tab_5)
        self.frame_2.setMaximumSize(QtCore.QSize(1800, 900))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.listWidget_tab5 = QtWidgets.QListWidget(self.frame_2)
        self.listWidget_tab5 .setMaximumSize(QtCore.QSize(650,800))
        self.listWidget_tab5 .setObjectName("listWidget_tab5 ")
        self.listWidget_tab5.setAlternatingRowColors(True)
        self.listWidget_tab5.setGridSize(QtCore.QSize(20, 45))  # 设置行的宽和高
        self.listWidget_tab5.setFont(ListItemFont)  #设置行对象字体大小
        self.listWidget_tab5.itemClicked.connect(self.captureCode1)  # 绑定槽函数 获取代码 从而获取折线图

        self.horizontalLayout_2.addWidget(self.listWidget_tab5 )
        self.widget_tab5 = QtWidgets.QWidget(self.frame_2)
        self.widget_tab5 .setMinimumSize(QtCore.QSize(0, 0))
        self.widget_tab5 .setObjectName("widget_tab5 ")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_tab5 )
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.comboBox = QtWidgets.QComboBox(self.widget_tab5 )
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.currentIndexChanged.connect(self.Graphics_display1) #comboBox的事件选中函数
        self.verticalLayout_6.addWidget(self.comboBox)
        self.graphicsView_tab5 = QtWidgets.QGraphicsView(self.widget_tab5 )
        self.graphicsView_tab5.setMaximumSize(QtCore.QSize(16777215, 1000))
        self.graphicsView_tab5.setObjectName("graphicsView_tab5")
        self.verticalLayout_6.addWidget(self.graphicsView_tab5)
        self.horizontalLayout_2.addWidget(self.widget_tab5 )
        self.verticalLayout_5.addWidget(self.frame_2)

        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.tabWidget.addTab(self.tab_6, "")

        #为tab_6创建垂直布局
        self.QVBoxLayout_tab6=QVBoxLayout(self.tab_6)
       #self.label_tab6=QtWidgets.QLabel(self.tab_6)
       #self.label_tab6.setObjectName("label_tab6")
       #self.label_tab6.setText("<a href='https://chrome.xahuapu.net/' style='color:red font-size=20px'>谷歌浏览器下载</a>" \
       #  "<br>" "<a href='https://liushilive.github.io/github_selenium_drivers/md/Chrome.html' style='color:red font-size=20px'> \
       #   不同版本对应驱动下载</a>")
       #self.label_tab6.setOpenExternalLinks(True) #允许点击外部链接进入

        self.pushButton_tab6=QPushButton(self.tab_6)
        self.pushButton_tab6.setObjectName("pushButton_tab6")
        self.pushButton_tab6.setGeometry(QtCore.QRect(240,270,60,50))
        self.pushButton_tab6.setIcon(QtGui.QIcon(r".\icon\tab6.ico"))
        self.pushButton_tab6.setStyleSheet("background-color:white")
        self.pushButton_tab6.setFlat(True) #去掉黑色边框
        self.pushButton_tab6.setText("Click me!Way to destination!")
        self.pushButton_tab6.setFont(QtGui.QFont("宋体", 20, QtGui.QFont.Bold)) #设置字体以及 加粗 字号16磅"
        self.pushButton_tab6.setIconSize(QtCore.QSize(150, 170))
        self.pushButton_tab6.setMinimumSize(QtCore.QSize(70, 100))
        self.pushButton_tab6.setMaximumSize(QtCore.QSize(1000, 220))
        self.pushButton_tab6.clicked.connect(self.OpenBrowser)

        #将按钮放进布局
        self.QVBoxLayout_tab6.addWidget(self.pushButton_tab6)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 860, 26))
        self.menuBar.setObjectName("menuBar")
        self.menu = QtWidgets.QMenu(self.menuBar)
        self.menu.setTitle("")
        self.menu.setObjectName("menu")
        self.menu_2 = QtWidgets.QMenu(self.menuBar)
        self.menu_2.setTitle("")
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(self.menuBar)
        self.menu_3.setObjectName("menu_3")
        self.menu_4 = QtWidgets.QMenu(self.menuBar)
        self.menu_4.setTitle("")
        self.menu_4.setObjectName("menu_4")
        self.menu_5 = QtWidgets.QMenu(self.menuBar)
        self.menu_5.setObjectName("menu_5")
        self.menu_6 = QtWidgets.QMenu(self.menuBar)
        self.menu_6.setTitle("")
        self.menu_6.setObjectName("menu_6")
        self.menu_7 = QtWidgets.QMenu(self.menuBar)
        self.menu_7.setObjectName("menu_7")

        MainWindow.setMenuBar(self.menuBar)
        self.action_versionUpdate = QtWidgets.QAction(MainWindow)
        self.action_versionUpdate.setText("软件更新(暂时未实现)")
        self.menu_3.addAction(self.action_versionUpdate)

        self.action_addQQ = QtWidgets.QAction(MainWindow)
        self.action_addQQ.setText("添加作者QQ")
        self.menu_3.addAction(self.action_addQQ)
        self.action_addQQ.triggered.connect(self.addQQ)
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setShortcutContext(QtCore.Qt.WindowShortcut)
        self.action_2.setMenuRole(QtWidgets.QAction.TextHeuristicRole)
        self.action_2.setObjectName("action_2")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setVisible(True)
        self.action_3.setMenuRole(QtWidgets.QAction.TextHeuristicRole)
        self.action_3.setObjectName("action_3")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_5 = QtWidgets.QAction(MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_6 = QtWidgets.QAction(MainWindow)
        self.action_6.setObjectName("action_6")
        self.actionSend_a_email_to_me = QtWidgets.QAction(MainWindow)
        self.actionSend_a_email_to_me.setObjectName("actionSend_a_email_to_me")
        self.actionSend_a_email_to_me.setText("Click there,and send a email to me!")
        self.menu_3.addSeparator()
        self.menu_5.addSeparator()
        self.menu_5.addAction(self.action_2)
        self.menu_5.addAction(self.action_3)
        self.menu_5.addAction(self.action_4)
        self.menu_5.addAction(self.action_5)
        self.menu_5.addAction(self.action_6)
        self.menu_7.addAction(self.actionSend_a_email_to_me)
        self.actionSend_a_email_to_me.triggered.connect(self.sendEmail)

        self.menuBar.addAction(self.menu_5.menuAction())
        self.menuBar.addAction(self.menu.menuAction())
        self.menuBar.addAction(self.menu_2.menuAction())
        self.menuBar.addAction(self.menu_3.menuAction())
        self.menuBar.addAction(self.menu_4.menuAction())
        self.menuBar.addAction(self.menu_6.menuAction())
        self.menuBar.addAction(self.menu_7.menuAction())

        self.retranslateUi(MainWindow)
        icon = QtGui.QIcon() #设置窗体Icon (运行时左上角的图标)
        icon.addPixmap(QtGui.QPixmap(r".\icon\窗体Icon.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)

        self.tabWidget.setCurrentIndex(0) #让程序运行时映入眼帘的是第一个Tab

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        MainWindow.setTabOrder(self.pushButton, self.calendarWidget)
        MainWindow.setTabOrder(self.calendarWidget, self.textBrowser)
        MainWindow.setTabOrder(self.textBrowser, self.textEdit)

        #初始化无头浏览器
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging']) #取消exe运行时的弹窗
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument(
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 SLBrowser/7.0.0.6241 SLBChan/33')
        self.chrome_options.add_argument("--window-size=1920,1050")  # 专门应对无头浏览器中不能最大化屏幕的方案

        #数据预加载
        self.Show_data("展示")  # 打开界面即显示历史查询记录 通过存入excel后再读取excel载入tablewidget


    def retranslateUi(self, MainWindow): #designer设计ui的时候 转为py文件需要的翻译函数
        self._translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(self._translate("MainWindow", "基金数据查询"))
        self.textBrowser.setHtml(self._translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600; color:#ff0000;\">本软件由 一片叶飘落(yipianyepiaoluo@protonmail.com)制作 禁止用于牟利以及反编译/病毒注入 违法/侵权必究</span></p></body></html>"))
        self.label.setText(self._translate("MainWindow", "请在此输入您要查询的基金的基金代码: "))
        self.pushButton.clicked.connect(self.msg1)  #点击pushbutton出现弹窗 创建点击信号与槽函数 发送者为pushbutton 接收者为QmessageBox

        __sortingEnabled = self.tableWidget.isSortingEnabled() #实例化排序变量
        self.tableWidget.setSortingEnabled(True) #点击表头可以排序

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), self._translate("MainWindow", "基金数据查询"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), self._translate("MainWindow", "历史查询记录"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), self._translate("MainWindow", "基金近期涨幅及折线表"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), self._translate("MainWindow", "基金经理"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), self._translate("MainWindow", "基金股票持仓"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), self._translate("MainWindow", "今日基金涨幅排行(顺/逆)"))
        self.menu_3.setTitle(self._translate("MainWindow", "关于"))
        self.menu_5.setTitle(self._translate("MainWindow", "功能"))
        self.menu_7.setTitle(self._translate("MainWindow", "建议"))
        self.action_2.setText(self._translate("MainWindow", "历史基金"))
        self.action_3.setText(self._translate("MainWindow", "基金估值/涨幅"))
        self.action_4.setText(self._translate("MainWindow", "基金近期涨幅及折线表     "))
        self.action_5.setText(self._translate("MainWindow", "基金股票持仓     "))
        self.action_6.setText(self._translate("MainWindow", "今日基金涨幅排行    "))
        self.pushButton_tab_41.setText(self._translate("MainWindow", "净值走势"))
        self.pushButton_tab_42.setText(self._translate("MainWindow", "收益走势"))
        self.radioButton_1.setText(self._translate("MainWindow", "近1月"))
        self.radioButton_2.setText(self._translate("MainWindow", "近3月"))
        self.radioButton_3.setText(self._translate("MainWindow", "近6月"))
        self.radioButton_4.setText(self._translate("MainWindow", "近1年"))
        self.radioButton_5.setText(self._translate("MainWindow", "近3年"))
        self.radioButton_6.setText(self._translate("MainWindow", "今年内"))
        self.radioButton_7.setText(self._translate("MainWindow", "成立以来"))
        self.comboBox.setItemText(0,self._translate("MainWindow", "2021第1季度"))
        self.comboBox.setItemText(1,self._translate("MainWindow", "2021第2季度"))
        self.comboBox.setItemText(2,self._translate("MainWindow", "2021第3季度"))
        self.comboBox.setItemText(3,self._translate("MainWindow", "2021第4季度"))

    def generateMenu(self, pos): #创建表格右键出现菜单的槽函数  未完成功能2 3!
        row_num = -1
        for i in self.tableWidget.selectionModel().selection().indexes():
           row_num = i.row()
        if row_num < self.Row:
            menu = QMenu()
            item1 = menu.addAction("加入自选基金")
            item2 = menu.addAction("收益率大于n%提醒(未实现)")
            item3 = menu.addAction("亏损率大于n%提醒(未实现)")
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))
            if action == item1: #若加入自选基金
               self.tableWidget.item(row_num,0).setForeground(QBrush(QColor(254, 162, 61)))
               self.tableWidget.item(row_num,1).setForeground(QBrush(QColor(254, 162, 61)))
               self.font.setBold(True)  # 设置字体为粗体
               self.tableWidget.item(row_num,0).setFont(self.font)
               self.tableWidget.item(row_num,1).setFont(self.font)
            elif action == item2:
                print('您选了选项二，当前行文字内容是：', self.tableWidget.item(row_num, 0).text(),
                      self.tableWidget.item(row_num, 1).text(), self.tableWidget.item(row_num, 2).text())

            elif action == item3:
                print('您选了选项三，当前行文字内容是：', self.tableWidget.item(row_num, 0).text(),
                      self.tableWidget.item(row_num, 1).text(), self.tableWidget.item(row_num, 2).text())
            else:
                return

    def msg1(self,code):               # 定义一个弹窗消息函数
        if type(code) is bool:
           reply = QtWidgets.QMessageBox.about(self.tab_2, "tips", "请输入基金代码后再进行查询！")
           return 0
        try:
           if len(code)==6 and str.isdigit(code):   #若传入的基金代码为纯数字 且为6位 则弹出以下消息
              self.Spider = spider(code,"inquire") #实例化类对象
              self.Spider.start()
              self.GetList = self.Spider.crawl_recent_data() #调用类方法 将传回的列表用变量接收
              if self.Spider.Answer1 == "NoProblem" :  #若查询过程中没问题会将spider类属性Answer1设置为NoProblem 表明可以弹出以下信息
                 self.add_data()
                 reply=QtWidgets.QMessageBox.about(self.tab_2,"tips","查询完毕,可在历史基金页面查看结果!")
                 self.textEdit.clear()  # 查询完毕清空输入框
              elif self.Spider.Answer1 == "Error" :    #查询过程出问题弹出以下警告
                 self.add_data()
                 reply = QtWidgets.QMessageBox.warning(self.tab_2, "Error", "该基金为货币基金或其属于境外市场 只能获取部分数据 请前往历史查询记录查看!",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.Yes)
                 self.textEdit.clear()  # 查询完毕清空输入框
              elif self.Spider.Answer1 == "Fault" :
                 reply = QtWidgets.QMessageBox.warning(self.tab_2, "Error", "很抱歉 该基金不存在!",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                        QtWidgets.QMessageBox.Yes)
                 self.textEdit.clear()  # 输入字母报错后清空输入框

           else:      #若不合规 弹出以下警告
              reply=QtWidgets.QMessageBox.warning(self.tab_2,"Error", "基金代码为6位纯数字字符串!",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.Yes)
              self.textEdit.clear()  # 输入字母报错后清空输入框

        except ConnectionError:
              reply = QtWidgets.QMessageBox.warning(self.tab_2, "Error", "您查询的频率过高!请稍等片刻再作查询",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.Yes)

    def get_code(self): #获取查询的基金代码
        code=self.textEdit.toPlainText()  #实时获取输入的字符
        if str.isalpha(code):             #若输入字母直接报错
            reply = QtWidgets.QMessageBox.warning(self.tab_2, "Error", "基金代码为6位纯数字字符串！",
                                                  QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.Yes)
            self.textEdit.clear()     #输入字母报错后清空输入框
        if len(code) == 6:
           self.msg1(code)      #当输入6个字符后传入槽函数msg判断是否合规

    def delete_clicked(self): #设置点击事件 响应按下删除键
        try:
           button = QtWidgets.QPushButton.sender(self.deleteButton) #定义一个信号发射器
           if button:
               row = self.tableWidget.indexAt(button.pos()).row()
               self.tableWidget.removeRow(row) #删除指定行 并填充
               df = pd.read_excel("基金.xlsx")
               df = df.drop([row])
               df.to_excel("基金.xlsx")
        except Exception as er:
               print(er)

    def delete_data(self)->"Set a button to delete some rows":
        for i in range(self.Row-1):
            self.deleteButton = QtWidgets.QPushButton("Delete it")  # 创建self.Row个按钮
            self.deleteButton.clicked.connect(self.delete_clicked)  # 绑定敲击事件到槽函数delete_clicked
            self.tableWidget.setCellWidget(i,len(self.NameList),self.deleteButton) #在每行最后一列放置按钮

    def add_data(self)->"A function is to add the data to tableWidget":
        self.tableWidget.setRowCount(self.Row) #令表格行数加1
        item = QtWidgets.QListWidgetItem()
        ITEM = QtWidgets.QListWidgetItem()
        item1 = QtWidgets.QListWidgetItem()
        self.listWidget.addItem(item)
        self.listWidget_tab5.addItem(ITEM)
        self.listWidget_tab3.addItem(item1)
        item.setText(self.GetList[0]+self.GetList[1]) #向列表控件中添加新元素
        ITEM.setText(self.GetList[0]+self.GetList[1])
        item1.setText(self.GetList[0]+self.GetList[1])
        for i in range(len(self.NameList)):
            self.tableWidget.setItem(self.Row-1,i,QtWidgets.QTableWidgetItem(self.GetList[i]))
            if self.tableWidget.item(self.Row-1,i).text() == "--" or self.tableWidget.item(self.Row-1,i).text() =="无":
                continue
            elif i == 5 or i > 6:  # 给涨幅设置颜色和字体
                self.font.setBold(True)  # 设置字体为粗体
                self.tableWidget.item(self.Row-1,i).setFont(self.font)
                text = float(str(self.tableWidget.item(self.Row-1,i).text()).replace("%", '')) # 将%去掉 变为float 便于判断正负
                self.tableWidget.item(self.Row-1,i).setForeground(QBrush(QColor(0, 100, 0))) if text \
                    < 0 else self.tableWidget.item(self.Row-1,i).setForeground(QBrush(QColor(255, 0, 0)))
                # 若涨幅小于0 设置字体为绿色  反之 红色
        self.Row += 1 #插入的位置变为下一行
        self.delete_data()  # 给新添的数据加按钮

    def Show_data(self,mode)->"A funtion is to show the data in tab_2":
        if os.path.exists("基金.xlsx"):
           data = pd.read_excel("基金.xlsx")  # 读取文件
           RowNum = data.shape[0]  # 取出行数
           self.tableWidget.setRowCount(RowNum)                  #有几只基金就设置几行  即df.shape[0]
           self.tableWidget.setColumnCount(16)              #有几个列标就设置几列 即len(IndexList)
           for i in range(len(self.NameList)): #循环设置列标
               self.tableWidget.setHorizontalHeaderItem(i,QtWidgets.QTableWidgetItem(self.NameList[i]))
           CodeList = list(data.loc[0:RowNum, '基金代码'])  # 将基金代码放入列表
           NewCodeList = [(6 - len(str(p))) * '0' + str(p) for p in CodeList]  # 给基金代码补0
           self.font = QtGui.QFont("宋体", 13)  # 设置字体样式
           self.tableWidget.setFont(self.font)
           for i in range(RowNum):  #迭代行
               if mode == "展示":
                  item = QtWidgets.QListWidgetItem() #实例化行对象
                  ITEM = QtWidgets.QListWidgetItem()
                  item1 = QtWidgets.QListWidgetItem()
                  self.listWidget.addItem(item) #循环建立行
                  self.listWidget_tab5.addItem(ITEM)
                  self.listWidget_tab3.addItem(item1)
               for Name in self.NameList: #迭代列
                   self.tableWidget.setItem(i, self.counter, QtWidgets.QTableWidgetItem(str(data.loc[i, Name]))) #表格内容填充
                   if mode == "展示":
                      item.setText(str(data.loc[i, "基金代码"])+str(data.loc[i, "基金名称"])) if len(str(data.loc[i, "基金代码"]))==6 \
                      else item.setText((6-len(str(data.loc[i, "基金代码"])))*"0"+str(data.loc[i, "基金代码"])+str(data.loc[i, "基金名称"])) #若基金代码不足6位则填上

                      ITEM.setText(str(data.loc[i, "基金代码"]) + str(data.loc[i, "基金名称"])) if len(str(data.loc[i, "基金代码"])) == 6 \
                      else ITEM.setText((6 - len(str(data.loc[i, "基金代码"]))) * "0" + str(data.loc[i, "基金代码"]) + str(data.loc[i, "基金名称"]))

                      item1.setText(str(data.loc[i, "基金代码"]) + str(data.loc[i, "基金名称"])) if len(str(data.loc[i, "基金代码"])) == 6 \
                      else item1.setText((6 - len(str(data.loc[i, "基金代码"]))) * "0" + str(data.loc[i, "基金代码"]) + str(data.loc[i, "基金名称"]))
                     # 将基金代码+名称作为全称填入列表控件的行对象中 便于提取基金代码抓取折线图
                   if self.tableWidget.item(i, self.counter).text() == "--":
                      self.counter+=1
                      continue
                   elif self.tableWidget.item(i, self.counter).text() == "无":
                      self.counter+=1
                      continue
                   elif  self.counter == 5 or self.counter > 6 :  # 给涨幅设置颜色和字体
                       self.font.setBold(True)  # 设置字体为粗体
                       self.tableWidget.item(i, self.counter).setFont(self.font)
                       text = float(
                           str(self.tableWidget.item(i, self.counter).text()).replace("%", ''))  # 将%去掉 变为float 便于判断正负
                       self.tableWidget.item(i, self.counter).setForeground(QBrush(QColor(0, 100, 0))) if text \
                                                                                                          < 0 else self.tableWidget.item(
                           i, self.counter).setForeground(QBrush(QColor(255, 0, 0)))
                       # 若涨幅小于0 设置字体为绿色  反之 红色
                   self.counter += 1 #让列数+1
               self.counter=0 #让列数归0
           self.Row = RowNum + 1 #让行数等于已插入的行数+1 即从下一行开始插入
           self.tableWidget.resizeColumnsToContents()  # 将列调整到跟内容大小相匹配
           self.tableWidget.resizeRowsToContents()  # 将行大小调整到跟内容的大学相匹配
           self.delete_data() #放置删除按钮
        else:
            return 0

    def UpDate(self): #更新tablewidget中的基金数据
        reply = QtWidgets.QMessageBox.about(self.tab_2, "tips", "数据更新过程中请耐心等待 不要退出!")
        Spider = spider(1, "update")
        Spider.update_data()
        self.Show_data("更新")
        reply = QtWidgets.QMessageBox.about(self.tab_2, "tips", "数据更新完毕!")
        return 0

    "tab_4获取折线图 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    def captureCode(self): #获取选中列表组建的基金代码 从而作为参数传给其他槽函数抓取折线图
        return self.listWidget.currentItem().text()[:6] #获取代码

    def captureCode1(self):
        return self.listWidget_tab5.currentItem().text()[:6]

    def GotoBrowser(self):
        code=self.listWidget_tab3.currentItem().text()[:6]
        webbrowser.open(url="http://fundf10.eastmoney.com/jjjl_"+code+".html", new=0, autoraise=True)
        return 0

    def planA(self):  #这个应对按下第一个按钮对应的7个radiobutton
        self.radioButton_1.clicked.connect(self.crawl_Adata)
        self.radioButton_2.clicked.connect(self.crawl_Adata)
        self.radioButton_3.clicked.connect(self.crawl_Adata)
        self.radioButton_4.clicked.connect(self.crawl_Adata)
        self.radioButton_5.clicked.connect(self.crawl_Adata)
        self.radioButton_6.clicked.connect(self.crawl_Adata)
        self.radioButton_7.clicked.connect(self.crawl_Adata)

    def planB(self):  #应对按下第二个按钮对应的7个radiobutton
        self.radioButton_1.clicked.connect(self.crawl_Bdata)
        self.radioButton_2.clicked.connect(self.crawl_Bdata)
        self.radioButton_3.clicked.connect(self.crawl_Bdata)
        self.radioButton_4.clicked.connect(self.crawl_Bdata)
        self.radioButton_5.clicked.connect(self.crawl_Bdata)
        self.radioButton_6.clicked.connect(self.crawl_Bdata)
        self.radioButton_7.clicked.connect(self.crawl_Bdata)

    #choose不同 则抓取的图片主要内容就不同
    def crawl_Adata(self): #通过传入的内存地址判断是哪个radiobutton
        if self.rbtn1[:2]+self.rbtn1[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000",""):
           self.crawl_data(1,"A")
           return 0
        elif self.rbtn2[:2]+self.rbtn2[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000",""):
            self.crawl_data(2, "A")
            return 0
        elif self.rbtn3[:2] + self.rbtn3[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(3, "A")
            return 0
        elif self.rbtn4[:2] + self.rbtn4[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(4, "A")
            return 0
        elif self.rbtn5[:2] + self.rbtn5[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(5, "A")
            return 0
        elif self.rbtn6[:2] + self.rbtn6[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(6, "A")
            return 0
        elif self.rbtn7[:2] + self.rbtn7[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(7, "A")
            return 0

    def crawl_Bdata(self):
        if self.rbtn1[:2]+self.rbtn1[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000",""):
           self.crawl_data(1,"B")
           return 0
        elif self.rbtn2[:2]+self.rbtn2[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000",""):
            self.crawl_data(2, "B")
            return 0
        elif self.rbtn3[:2] + self.rbtn3[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(3, "B")
            return 0
        elif self.rbtn4[:2] + self.rbtn4[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(4, "B")
            return 0
        elif self.rbtn5[:2] + self.rbtn5[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(5, "B")
            return 0
        elif self.rbtn6[:2] + self.rbtn6[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(6, "B")
            return 0
        elif self.rbtn7[:2] + self.rbtn7[2:].upper() == str(MainWindow.sender())[-19:-1].replace("00000", ""):
            self.crawl_data(7, "B")
            return 0

    def crawl_data(self,index,choose):   #抓取折线图
        code=self.captureCode()
        if os.path.exists(f'AllLineCharts\\{code}AND{choose}OfLineCharts\\{code}ANDgraph{choose}AND{index}.png'):
           self.Graphics_display(code, choose, index) #若抓过一次 直接读取图像并展示 提高效率
           return 0
        url="http://fund.10jqka.com.cn/"+code+"/"
        #先创建一个级联目录
        if not os.path.exists("AllLineCharts"): #若大文件夹不存在
           os.makedirs("AllLineCharts") #r是用来转义\的 否则要加双\
        try:
            if not os.path.exists(f"AllLineCharts\\{code}AND{choose}OfLineCharts"): #若不存在该文件
               os.makedirs(f"AllLineCharts\\{code}AND{choose}OfLineCharts") #创建一个文件夹 存放折线图图片 每个基金的折线图放各自的文件夹中pi
            if self.DriverCounter==0:
               self.driver = webdriver.Chrome(options=self.chrome_options,executable_path="chromedriver.exe")
               self.executor_url = self.driver.command_executor._url
               self.session_id = self.driver.session_id
               self.driver.get(url)
               self.driver.implicitly_wait(7) #最多等5秒
            self.driver2 =ReuseChrome(command_executor=self.executor_url,session_id=self.session_id)  #浏览器对象复用 提高效率
            if choose == "B":
               self.driver2.find_element_by_xpath('//*[@id="ownSelect"]/div[1]/ul/li[2]').click() #点击收益走势
               if self.DriverCounter == 0 :
                  sleep(4.5) #等待曲线完整呈现
               else:
                  sleep(2.5)
            self.driver2.find_element_by_xpath(f'//*[@id="zsTime"]/li[{index}]').click() #选择收益周期 (默认净值走势)
            if self.DriverCounter == 0:
               sleep(7.2) #等待曲线完成整形
               self.DriverCounter += 1
            else:
                sleep(4.5)
            Graph1 = self.driver2.find_element_by_xpath('//*[@id="ownSelect"]') #选择图片区域
            Graph1.screenshot(f'AllLineCharts\\{code}AND{choose}OfLineCharts\\{code}ANDgraph{choose}AND{index}.png')
            #driver.close()  # 关掉浏览器
            self.Graphics_display(code,choose,index)
        except Exception as msg:
            print(msg)

    def Graphics_display(self,code,choose,index)->"Specifically for the display":
        img = cv2.imread(f'AllLineCharts\\{code}AND{choose}OfLineCharts\\{code}ANDgraph{choose}AND{index}.png')  # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        self.zoomscale = 1  # 图片放缩尺度
        frame = QtGui.QImage(img, x, y, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(frame)
        self.item = QtWidgets.QGraphicsPixmapItem(pix)  # 创建像素图元
        self.scene = QtWidgets.QGraphicsScene()  # 创建场景
        self.scene.addItem(self.item)
        self.graphicsView.setScene(self.scene)
        self.graphicsView.show()
        return 0

    def Preload(self,code,index): #若已存在 无需继续抓取
        img = cv2.imread(f'AllPosition\\{code}Season{index}.png')  # 读取图像
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # 转换图像通道
        x = img.shape[1]  # 获取图像大小
        y = img.shape[0]
        self.zoomscale = 1  # 图片放缩尺度
        frame = QtGui.QImage(img, x, y, x*3, QtGui.QImage.Format_RGB888) #x*3作用目前未知
        pix = QtGui.QPixmap.fromImage(frame)
        self.item_tab5 = QtWidgets.QGraphicsPixmapItem(pix)  # 创建像素图元
        self.scene_tab5 = QtWidgets.QGraphicsScene()  # 创建场景
        self.scene_tab5.addItem(self.item_tab5)
        self.graphicsView_tab5.setScene(self.scene_tab5)
        self.graphicsView_tab5.show()  # 若抓过一次 直接读取图像并展示 提高效率
        return 0

    def Graphics_display1(self): #抓第一季度的 xpath索引对应4
        Season = self.comboBox.currentText()[5] #获取信息(第几季度)
        Index = 5-int(Season)
        code = self.captureCode1() #获取基金代码
        if os.path.exists(f'AllPosition\\{code}Season{Index}.png'):
            self.Preload(code, Index)
            return 0
        # 先创建一个级联目录
        try:
            url = "http://fundf10.eastmoney.com/ccmx_" + code + ".html"
            if not os.path.exists("AllPosition"):  # 若大文件夹不存在
                os.makedirs("AllPosition")  # r是用来转义\的 否则要加双\
            driver = webdriver.Chrome(options=self.chrome_options,executable_path="chromedriver.exe")
            driver.get(url)
            sleep(0.5)
            if Index == 1:
               driver.execute_script('window.scrollTo(0, 600)')  #执行滑动操作 定位第四季度 滑一个全屏就到了
            elif Index == 2 or Index == 3:
               driver.execute_script('window.scrollTo(0, 1200)') #若要定位第二第三季度 需要滑两个全屏
            else:
               driver.execute_script('window.scrollTo(0, 1800)') #定位第一个季度 要滑到底 即滑三个全屏 一个全屏600px高
            sleep(0.4)
            Graph1=driver.find_element_by_xpath(f'//*[@id="cctable"]/div[{Index}]/div/table') #定位图片区域
            Graph1.screenshot(f'AllPosition\\{code}Season{Index}.png')
            driver.close()  # 关掉浏览器
            self.Preload(code, Index)
        except Exception as msg:
            print(msg)
        return 0

    def OpenBrowser(self)->"Reply at the pushbutton of tab6,open the browser and let the player check it her(him)self!":
        webbrowser.open(url="http://fund.eastmoney.com/fund.html", new=0, autoraise=True)
        return 0

    def addQQ(self)->"A tool of menu_bar,clikc and then add my qq":
        webbrowser.open(url="tencent://AddContact/?fromId=45&fromSubId=1&subcmd=all&uin=1493672682&website=www.oicqzone.com", new=0, autoraise=True)
        return 0

    def sendEmail(self):
        webbrowser.open(url="https://mail.qq.com/cgi-bin/loginpage", new=0, autoraise=True)
        return 0

    def __del__(self): #删除保存的图片 下次重新抓取 避免数据老旧 无参考价值
        #os.remove(path) 删除文件
        process_name1="chrome.exe"
        process_name2="chromedriver.exe"
        cmd1 = 'taskkill /f /im %s'% process_name1 #杀死未关闭的无头浏览器进程
        cmd2= 'taskkill /f /im %s' % process_name2 #杀死驱动进程 避免内存占用过多
        os.system(cmd1)
        os.system(cmd2)
        if os.path.exists("AllLineCharts"):
           shutil.rmtree('AllLineCharts') # 递归删除图片文件夹 下次重新抓取
        if os.path.exists("AllPosition"):
           shutil.rmtree('AllPosition')  # 递归删除图片文件夹 下次重新抓取

if __name__ == "__main__" :
     app = QtWidgets.QApplication(sys.argv)
     MainWindow = QtWidgets.QMainWindow()
     MainUi = Ui_MainWindow()  # 实例化一个ui对象
     MainUi.setupUi(MainWindow)
     MainUi.retranslateUi(MainWindow)
     MainWindow.show()
     sys.exit(app.exec_())
