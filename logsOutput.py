#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: logsOutput
"""
@Author:
@Date: 2024/9/12
@Description: 日志模块，所有的日志来源项
"""
import logging
import os

# 创建日志目录
LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# 配置日志记录器
def set_logger(log_name, name, log_file, level):
    """
    创建并返回一个日志记录器
    :param log_name: 日志名称
    :param log_file: 日志文件
    :param name: 这是日志记录器的名称，也是传给 getLogger() 用以获取日志记录器的值。
    :param level: 日志等级设置
    """
    # 设置全局日志处理器
    loggers = logging.getLogger(log_name)
    loggers.setLevel(logging.DEBUG)

    if not loggers.hasHandlers():
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # 文件处理器
        file_handler = logging.FileHandler(os.path.join(LOG_DIR, log_file))
        file_handler.setFormatter(formatter)

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # 获取日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger
