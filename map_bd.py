#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: crawl_map
"""
@Author:
@Date: 2024/9/12
@Description:
"""
import time

import requests
from logsOutput import set_logger
import logging

import os
from os import makedirs
from os.path import exists

import openpyxl
from openpyxl import Workbook
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger_debug = set_logger(log_name='BdLogger', name='debug_bd', log_file="debug_bd.log", level=logging.DEBUG)
logger_info = set_logger(log_name='BdLogger', name='info_bd', log_file="info_bd.log", level=logging.INFO)
"""
  :param c-城市
  :param wd-关键字
  :param pn-页数
  :param nn-pn * 10
"""


def crawl_bd_map(city, key_word, page):
    '''proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }'''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    params = {
        "newmap": "1",
        "reqflag": "pcmap",
        "biz": "1",
        "from": "webmap",
        "da_par": "after_baidu",
        "pcevaname": "pc4.1",
        "qt": "s",
        "c": city,
        "wd": key_word,
        "wd2": "",
        "pn": page,
        "nn": page * 10,
        "db": "0",
        "sug": "0",
        "addr": "0",
        "on_gel": "1",
        "src": "7",
        "gr": page,
        "l": "12",
        "device_ratio": "2",
        "tn": "B_NORMAL_MAP",
        "u_loc": "12718411,3562885",
        "ie": "utf-8"
    }
    response = requests.get(url='https://map.baidu.com/', headers=headers, params=params)
    try:
        if 'content' in response.json():
            for contents in response.json()['content']:
                if contents is not None:
                    if len(contents) > 0 and 'tel' in contents and 'admin_info' in contents:
                        logger_info.info("开始清洗满足条件one的数据......")
                        yield {'addr': contents['addr'], 'tel': contents['tel'], 'name': contents['name'],
                               'admin_area': contents['admin_info']['area_name']}
                        logger_info.info(f"成功处理处理当前数据......{page}")
                    else:
                        logger_debug.debug("contents is not None!")
        else:
            logger_debug.debug(f"当前页{page}-没有任何数据，初始数据为：{response.json()}")
    except Exception as e:
        logger_debug.debug("***********新异常***********", e)
    finally:
        logger_info.info('数据处理完成......')


def save_data(province, city_code, key_word, page, city_name, key_word_bs):
    # city_name = '城市'
    exists(province) or makedirs(province)
    # 如果Excel文件不存在，则创建一个新的Excel文件
    if not os.path.exists(f'{province}/{city_name}.xlsx'):
        # with open(f'{province}/{city_name}.xlsx', 'w', newline='') as file:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(['Area_name', 'Display_Name', 'Tel', 'Addr'])
        for content in crawl_bd_map(city_code, key_word, page):
            if key_word_bs in content['name']:
                worksheet.append(
                    [content['admin_area'], content['name'], content['tel'], content['addr']])
                workbook.save(f'{province}/{city_name}.xlsx')
        logger_info.info("数据处理完成")
    else:
        try:
            # 如果Excel文件已存在，则读取现有数据并将新的JSON数据追加到其中
            workbook = openpyxl.load_workbook(f'{province}/{city_name}.xlsx')
            worksheet = workbook.active
            for content in crawl_bd_map(city_code, key_word, page):
                if key_word_bs in content['name']:
                    worksheet.append(
                        [content['admin_area'], content['name'], content['tel'], content['addr']])
                    workbook.save(f'{province}/{city_name}.xlsx')
                logger_info.info("数据处理完成")
        except Exception as e:
            logger_debug.debug(f"追加数据时异常，当前异常为：{e}")


def scrape_bd_api(province, key_word):
    print("scrape_bd_api 被调用")
    with open("config/provinces", 'r', encoding='utf-8') as province_text:
        province_text = province_text.readlines()
        if province + '\n' in province_text:
            logger_info.info(f"当前选择的省城是：{province}")
            with open('config/city_name.json', 'r', encoding='utf-8') as province_json:
                datas = json.load(province_json)
            for data in datas[province]:
                for key_city, value_city in data.items():
                    logger_info.info(f"{key_city}: {value_city}")
                    with open('config/area_name.json', 'r', encoding='utf-8') as area_json:
                        area_datas = json.load(area_json)
                    for area in area_datas[key_city]:
                        logger_info.info(f"&&&&&&&&&&&&&&&开始处理‘{key_city}-{area}’的数据&&&&&&&&&&&&&&&")
                        for page in range(0, 20):
                            save_data(province=province, city_code=value_city, key_word=key_word + ' ' + area,
                                      page=page,
                                      city_name=key_city, key_word_bs=key_word)


if __name__ == '__main__':
    '''province = input("请输入省份（例：湖北省、湖南省等）：")
    key_word = input("请输入查询条件：")
    with open("config/provinces", 'r', encoding='utf-8') as province_txt:
        province_txt = province_txt.readlines()
    if province+'\n' in province_txt:
        logger_info.info(f"当前输入：{province}")
        with open('config/city_name.json', 'r', encoding='utf-8') as province_json:
            datas = json.load(province_json)
        for data in datas[province]:
            for key_city, value_city in data.items():
                logger_info.info(f"{key_city}: {value_city}")
                with open('config/area_name.json', 'r', encoding='utf-8') as area_json:
                    area_datas = json.load(area_json)
                for area in area_datas[key_city]:
                    logger_info.info(f"&&&&&&&&&&&&&&&开始处理‘{key_city}-{area}’的数据&&&&&&&&&&&&&&&")
                    for page in range(0, 20):
                        save_data(province=province, city_code=value_city, key_word=key_word + ' ' + area, page=page,
                                  city_name=key_city, key_word_bs=key_word)
    else:
        logger_info.info(f"格式不正确！参考提示：{[item.strip() for item in province_txt]}")'''
