#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/4/29 16:01
# @Author : Evelyn Song
import os
import time
import re
import ssl
import numpy as np
from bs4 import BeautifulSoup
from six.moves import urllib
import requests
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium import webdriver
from multiprocessing.dummy import Pool as ThreadPool


def func(args):
    item = args[0]
    stat = args[1]
    ssl._create_default_https_context = ssl._create_unverified_context

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/103.0.1264.62 ',
        'Connection': 'keep-alive'
    }
    session = requests.session()
    # 后台运行
    edge_options = Options()
    edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    driver = webdriver.Edge(options=edge_options)

    sHref = r'https://aeronet.gsfc.nasa.gov/cgi-bin/data_display_aod_v3?site={}&nachal=2&level=1&place_code=10'.format(
        stat)
    response = session.get(sHref, headers=header)
    beautifulSoup = BeautifulSoup(response.text, 'html.parser')

    date = beautifulSoup.find(text=re.compile(r'Start Date.+')).split('-')
    first = int(re.sub(r'\;.+', '', date[2]))
    last = int(date[4])
    statHref = beautifulSoup.find('a', text=re.compile(r'More AERONET Downloadable Products\.{3}')).get('href')
    statUrl = 'https://aeronet.gsfc.nasa.gov/cgi-bin/' + statHref.replace('®', '&re')

    print('\n', first, last, stat, statUrl)
    if 2005 <= first <= 2012 or 2005 <= last <= 2012 or (first <= 2005 and last >= 2012):
        # 模拟检索动作
        try:
            driver.get(statUrl)
            checkbox = driver.find_element(By.ID, item)
            checkbox.click()
        except Exception as e:
            print(e)
            return
        # time.sleep(3)
        for year in range(max(first, 2005), min(last, 2012) + 1):
            filename = '{0}0101_{0}1231_{1}'.format(year, stat, item)
            filepath = r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\{}_{}.zip'.format(filename, item)
            if os.path.exists(filepath):
                print('Done ', year, stat)
                continue
            url = 'https://aeronet.gsfc.nasa.gov/zip_files_v3/{}.zip'.format(filename)
            try:
                select1 = Select(driver.find_element(By.XPATH, '//*[@id="Year1"]'))
                select1.select_by_visible_text(str(year))
            except Exception as e:
                print(e)
                print('select year faild', stat, year, url,
                      file=open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SSA\error.txt', 'a', encoding='utf-8'))
                continue

            select2 = Select(driver.find_element(By.XPATH, '//*[@id="Year2"]'))
            select2.select_by_visible_text(str(year))

            submit = driver.find_element(By.NAME, 'Submit')
            submit.click()
            time.sleep(30)
            try:
                urllib.request.urlretrieve(url, filepath)
                print('Done ', year, url)
            except Exception as e:
                time.sleep(30)
                try:
                    urllib.request.urlretrieve(url, filepath)
                    print('Done ', year, url)
                except Exception as e:
                    time.sleep(30)
                    try:
                        urllib.request.urlretrieve(url, filepath)
                        print('Done ', year, url)
                    except Exception as e:
                        time.sleep(30)
                        try:
                            urllib.request.urlretrieve(url, filepath)
                            print('Done ', year, url)
                        except urllib.error.HTTPError:
                            print('Not Found', year, url)
                            print(stat, year, url,
                                  file=open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\error.txt', 'a',
                                            encoding='utf-8'))


if __name__ == "__main__":
    file = open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\error.txt', 'w')
    file.close()

    statList = np.loadtxt(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\GEO_3.0\AERONET GEO 3.0.txt', dtype=str,
                          usecols=0, skiprows=1, delimiter=',')

    # downItem = ['AOD10', 'AOD15', 'AOD20', 'TOT10', 'TOT15', 'TOT20', 'SDA10', 'SDA15', 'SDA20']
    items = ['SDA15', 'TOT15', 'AOD15']

    for downItem in items:
        pool = ThreadPool()
        pool.map(func, zip([downItem]*statList.size, statList))
        pool.close()
        pool.join()
# end
