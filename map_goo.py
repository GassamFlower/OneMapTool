#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: map_2
"""
@Author: LYG
@Date: 2024/10/15
@Description: 
"""
import requests
import json
from logsOutput import set_logger
import logging
import random
import os
from os import makedirs
from os.path import exists

import openpyxl
from openpyxl import Workbook
from excel_cleanse import execl_qc

logger_debug = set_logger(log_name='GgLogger', name='debug_gg', log_file="debug_gg.log", level=logging.DEBUG)
logger_info = set_logger(log_name='GgLogger', name='info_gg', log_file="info_gg.log", level=logging.INFO)

"""
  :param city_name-城市
  :param wd-关键字
  :param page-页数
  :param latitude/longitude 经纬度
"""
agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5',
    'Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US) AppleWebKit/532.9 (KHTML, like Gecko) Chrome/5.0.310.0 Safari/532.9',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/9.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.14 (KHTML, like Gecko) Chrome/10.0.601.0 Safari/534.14',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.20 (KHTML, like Gecko) Chrome/11.0.672.2 Safari/534.20", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.24 Safari/535.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
]


def scrape_parse(province, page, multiples, key_word, city_name, latitude, longitude, agent):
    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://www.google.com/',
        'user-agent': agent
    }
    proxies = {
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    }
    d1 = multiples
    params = {
        "tbm": "map",
        "authuser": "0",
        "hl": "zh-CN",
        "gl": "gz",
        "pb": f"!4m12!1m3!1d{d1}!2d{latitude}!3d{longitude}!2m3!1f0!2f0!3f0!3m2!1i402!2i730!4f13.1!7i20!8i{page * 10}!10b1!12m22!1m2!18b1!30b1!2m3!5m1!6e2!20e3!10b1!12b1!13b1!16b1!17m2!3e1!3e1!20m4!5e2!6b1!8b1!14b1!46m1!1b0!94b1!19m4!2m3!1i360!2i120!4i8!20m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m42!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e9!2b1!3e2!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!2b1!4b1!9b0!22m5!1sY8ERZ-KWJMKfvr0P29SliQU%3A400!2s1i%3A0%2Ct%3A150714%2Cp%3AY8ERZ-KWJMKfvr0P29SliQU%3A400!7e81!12e3!17sY8ERZ-KWJMKfvr0P29SliQU%3A422!24m122!1m31!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m20!3b1!4b1!5b1!6b1!9b1!12b1!13b1!14b1!17b1!20b1!21b1!22b1!25b1!27m1!1b0!28b0!31b0!32b0!33m1!1b0!10m1!8e3!11m2!3e1!3e1!14m1!3b1!17b1!20m4!1e3!1e6!1e3!1e6!24b1!25b1!26b1!29b1!30m1!2b1!36b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!65m9!3m8!1m3!1m2!1i224!2i298!1m3!1m2!1i224!2i298!71b1!72m30!1m5!1b1!2b1!3b1!5b1!7b1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_reviews!6m1!1e1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4!3sother_user_reviews!6m1!1e1!9b1!89b1!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!125b0!126b1!127b1!26m4!2m3!1i80!2i92!4i8!30m0!34m18!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!37m1!1e81!42b1!47m0!49m9!3b1!6m2!1b1!2b1!7m2!1e3!2b1!8b1!9b1!50m4!2e2!3m2!1b1!3b1!67m2!7b1!10b1!69i709",
        "q": key_word
    }
    response = requests.get(
        url='https://www.google.com/search', headers=headers, params=params, proxies=proxies
    )

    content1 = response.text[3:]
    content2 = content1.replace("null,", '').replace("'", "")
    for content in json.loads(content2)[0][1]:
        if key_word not in content[2][0] and len(content[2]) > 5:
            try:
                print(content[2][2][1])
                if isinstance(content[2][2][1], str) and city_name[:2] in content[2][2][1]:
                    # print(content[2][2], content[2][5])
                    for index in range(28, 33):
                        try:
                            if isinstance(content[2][index], list):
                                for tel in content[2][index]:
                                    if isinstance(tel, list):
                                        if isinstance(tel[0], str) and '+86' in tel[0]:
                                            # 如果Excel文件不存在，则创建一个新的Excel文件
                                            if not os.path.exists(f'{province}/{city_name}_谷歌.xlsx'):
                                                # with open(f'{province}/{city_name}.xlsx', 'w', newline='') as file:
                                                workbook = Workbook()
                                                worksheet = workbook.active
                                                worksheet.append(['Addr', 'Display_Name', 'Tel'])
                                                worksheet.append(
                                                    [" ".join(content[2][2]), content[2][5], tel[0]])
                                                workbook.save(f'{province}/{city_name}_谷歌.xlsx')
                                            else:
                                                try:
                                                    # 如果Excel文件已存在，则读取现有数据并将新的JSON数据追加到其中
                                                    workbook = openpyxl.load_workbook(
                                                        f'{province}/{city_name}_谷歌.xlsx')
                                                    worksheet = workbook.active
                                                    worksheet.append(
                                                        [" ".join(content[2][2]), content[2][5], tel[0]])
                                                    workbook.save(f'{province}/{city_name}_谷歌.xlsx')
                                                except Exception as e:
                                                    logger_debug.debug(f"追加数据时异常，当前异常为：{e}")
                        except IndexError:
                            logger_info.info("下标超出，没有电话信息")
                            break
            except IndexError:
                logger_debug.debug(f"IndexError:{content[2][2]}")
                logger_info.info("下标超出，没有店铺信息")
                break


def scrape_gg_api(province, key_word):
    exists(province) or makedirs(province)
    with open("config/provinces", 'r', encoding='utf-8') as province_text:
        province_text = province_text.readlines()
    if province + '\n' in province_text:
        logger_info.info(f"当前输入：{province}")
    with open("config/经纬度.json", "r", encoding="utf-8") as f:
        read_data = json.load(f)
    if province in read_data:
        items = read_data[province].items()
        for city_name, value in items:
            logger_info.info(f"当前城市：{city_name}")
            for multiples in range(111111, 999999, 1000):
                for page in range(1, 30):
                    random_agent = random.choice(agents)
                    scrape_parse(province, page, multiples, key_word, city_name, value[0], value[1], random_agent)
                    execl_qc(province=province, city_name=city_name, map_type="谷歌")


if __name__ == '__main__':
    scrape_gg_api(province='重庆市', key_word='水果')

