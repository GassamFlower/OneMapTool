#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: main_qt
"""
@Author: LYG
@Date: 2024/10/30
@Description: 
"""
from map_bd import scrape_bd_api
from map_goo import scrape_gg_api
from map_by import scrape_by_api
import sys
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUiType

from logsOutput import set_logger
import logging

logger_debug = set_logger(log_name='QtLogger', name='debug_qt', log_file="debug_qt.log", level=logging.DEBUG)
logger_info = set_logger(log_name='QtLogger', name='info_qt', log_file="info_qt.log", level=logging.INFO)


class MainWindow(QMainWindow):
    def __init__(self):
        '''
            super()内置函数，它返回超类的临时对象，允许您调用它的方法
            Switch这是当前类，并且self是该类的实例
            __init__():这会调用__init__超类的方法，self作为参数传递，这确保执行超类的初始化逻辑。
        '''
        super(MainWindow, self).__init__()
        self.ui = loadUiType("config/map.ui")[0]()
        self.ui.setupUi(self)
        # threading.Thread(target=self.button_control).start()
        self.ui.pushButton.clicked.connect(self.main_save)
        self.ui.reset.clicked.connect(self.reset)
        self.ui.province.currentIndexChanged.connect(self.update_first)
        self.ui.map_type.currentIndexChanged.connect(self.update_second)
        self.ui.keyword.textChanged.connect(self.write_keywords)

    def reset(self):
        self.ui.pushButton.setEnabled(True)
        self.ui.keyword.clear()
        QMessageBox.information(self, '任务提示', '已重置信息', QMessageBox.Yes)


    def update_first(self):
        # 获取选中项的文本内容  选择的省城
        return self.ui.province.currentText()

    def update_second(self):
        # 获取选中项的文本内容  选择的地图类型
        return self.ui.map_type.currentText()

    def write_keywords(self):
        # logger_info.info(f"关键字填写：{self.ui.keyword.text()}")
        return self.ui.keyword.text()

    def main_save(self):
        logger_info.info("开始处理数据......")
        self.ui.pushButton.setEnabled(False)
        if self.update_second() == '百度地图':
            thread = Thread(target=scrape_bd_api, args=(self.update_first(), self.write_keywords()))
            thread.start()
        elif self.update_second() == '谷歌地图':
            thread = Thread(target=scrape_gg_api, args=(self.update_first(), self.write_keywords()))
            thread.start()
        elif self.update_second() == '必应地图':
            thread = Thread(target=scrape_by_api, args=(self.update_first(), self.write_keywords()))
            thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
