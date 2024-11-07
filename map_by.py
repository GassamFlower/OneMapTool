#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File_Name: map_by
"""
@Author: LYG
@Date: 2024/11/4
@Description: 
"""
import json
import time
from datetime import datetime
from logsOutput import set_logger
import logging
import random
import os
from os import makedirs
from os.path import exists
import requests
from bs4 import BeautifulSoup
import numpy as np
import itertools
import openpyxl
from openpyxl import Workbook
from excel_cleanse import execl_qc

logger_debug = set_logger(log_name='ByLogger', name='debug_by', log_file="debug_by.log", level=logging.DEBUG)
logger_info = set_logger(log_name='ByLogger', name='info_by', log_file="info_by.log", level=logging.INFO)


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


def scrape_url(key_word,  latitude1, latitude2, longitude1, longitude2, agent):
    logger_info.info(f"纬度1:{latitude1}, 纬度2：{latitude2}——经度1：{longitude1}，经度2：{longitude2}")
    """
    :param key_word: 关键字
    :param latitude1:  纬度1
    :param latitude2: 纬度2
    :param longitude1: 经度1
    :param longitude2: 经度2
    :param agent: ua
    :return:
    """

    headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': agent,
    }
    params = {
        "q": key_word,
        "count": 100,
        "localMapView": f"{latitude1}, {longitude1}, {latitude2}, {longitude2}"
    }
    time.sleep(random.randint(1, 2))
    response = requests.get(
        'https://cn.bing.com/maps/overlaybfpr',
        headers=headers,
        params=params
    )
    if response.status_code == 200:
        return response.content.decode('utf-8')


def parser_html(html, province, city_name):
    logger_info.info("开始解析数据...")
    soups = BeautifulSoup(html, 'html.parser')
    contents = soups.find_all('div', attrs={'class': 'b_vPanel'})
    try:
        for content_parser in contents:
            soup = BeautifulSoup(str(content_parser), 'html.parser')
            content_soup = soup.find_all('div', attrs={'class': 'b_factrow'})
            if len(content_soup) > 3:
                logger_info.info(f"DZ类型：{(content_soup[2].text)[:6]}")
                if city_name in content_soup[2].text:
                    logger_info.info(f"类型：{content_soup[1].text}")
                    save_date(province, city_name, content_soup[0].text, content_soup[2].text, content_soup[3].text)
    except Exception as e:
        print(f"当前报错：{e}，打印{contents}")


def save_date(province, city_name, name, addr, tel):
    logger_info.info("save data starting......")
    try:
    # 如果Excel文件不存在，则创建一个新的Excel文件
        if not os.path.exists(f'{province}/{city_name}_必应.xlsx'):
            logger_info.info(f"创建{city_name}数据")
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.append(['Display_Name', 'Addr', 'Tel'])
            worksheet.append([name, addr, tel])
            workbook.save(f'{province}/{city_name}_必应.xlsx')
        else:

                logger_info.info(f"追加{city_name}数据")
                # 如果Excel文件已存在，则读取现有数据并将新的JSON数据追加到其中
                workbook = openpyxl.load_workbook(f'{province}/{city_name}_必应.xlsx')
                worksheet = workbook.active
                worksheet.append([name, addr, tel])
                workbook.save(f'{province}/{city_name}_必应.xlsx')
    except Exception as e:
        logger_debug.debug(f"数据时异常，当前异常为：{e},append{[name, addr, tel]}")


def ll_itertools(latitude_list, longitudes_list):
    """
    :param latitude_list: 经度
    :param longitudes_list: 纬度
    :return: 随机组合的经纬度
    """
    latitudes_combinations = list(itertools.combinations(latitude_list, 2))
    longitudes_combinations = list(itertools.combinations(longitudes_list, 2))
    # 生成所有可能的组合并过滤掉重复的组合
    unique_combinations = []
    for combo in itertools.product(latitudes_combinations, longitudes_combinations):
        # 将组合扁平化并检查是否有重复元素
        flattened_combo = combo[0] + combo[1]
        if len(flattened_combo) == len(set(flattened_combo)):
            unique_combinations.append(combo)
    # 展示结果
    for combo in unique_combinations:
        yield combo[0][0], combo[0][1], combo[1][0], combo[1][1]


def scrape_by_api(province, key_word):
    exists(province) or makedirs(province)
    with open("config/provinces", 'r', encoding='utf-8') as province_text:
        province_text = province_text.readlines()
    if province + '\n' in province_text:
        logger_info.info(f"当前输入：{province}")
    # wh_json = {"北京市": [116.4, 39.9]}
    with open("config/经纬度.json", "r", encoding="utf-8") as f:
        read_data = json.load(f)
    longitudes = []  # 经度
    latitudes = []  # 纬度
    if province in read_data:
        items = read_data[province].items()
        for city_name, value in items:
            logger_info.info(f"当前城市：{city_name}")
    # for k, v in wh_json.items():
            for float_range in np.arange(0.000001, 0.999999, 0.131102):
                longitudes.append(value[0] + float_range)
                latitudes.append(value[1] + float_range)
            start_time = datetime.now()
            for content in ll_itertools(latitudes, longitudes):
                random_agent = random.choice(agents)
                parser_html(scrape_url(key_word, content[0], content[1], content[2], content[3], random_agent), province, city_name)  # 解析数据
                logger_info.info("数据去重工作准备......")
                time.sleep(1)
                execl_qc(province=province, city_name=city_name, map_type="必应")  # 数据去重
            end_time = datetime.now()
            logger_info.info(f"用时：{end_time - start_time}")

if __name__ == '__main__':
    scrape_by_api("湖北省", '1')