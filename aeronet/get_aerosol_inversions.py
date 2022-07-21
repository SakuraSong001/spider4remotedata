#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/4/29 20:12
# @Author : Evelyn Song
import ssl
from selenium import webdriver
import requests
import numpy as np
from bs4 import BeautifulSoup
import re
import time
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, UnexpectedAlertPresentException
from selenium.webdriver.edge.options import Options
from six.moves import urllib
import os


if __name__ == "__main__":
    file = open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SSA\error.txt', 'w')
    file.close()
    ssl._create_default_https_context = ssl._create_unverified_context
    driver = webdriver.Edge()

    # 后台运行
    edge_options = Options()
    edge_options.add_argument('--headless')
    edge_options.add_argument('--disable-gpu')
    driver = webdriver.Edge(options=edge_options)

    downItem = ['VOL', 'RIN', 'SSA']

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/103.0.1264.62 ',
        'Connection': 'keep-alive'
    }
    session = requests.session()
    statList = np.loadtxt(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\GEO_3.0\AERONET GEO 3.0.txt', dtype=str,
                          usecols=0, skiprows=1, delimiter=',')
    for stat in statList:
        sHref = r'https://aeronet.gsfc.nasa.gov/cgi-bin/data_display_inv_v3?site={}' \
                r'&nachal=2&level=2&place_code=10&DATA_TYPE=76'.format(stat)
        response = session.get(sHref, headers=header)
        beautifulSoup = BeautifulSoup(response.text, 'html.parser')

        date = beautifulSoup.find(text=re.compile(r'Start Date.+')).split('-')
        statHref = beautifulSoup.find('a', text=re.compile(r'More AERONET Downloadable Products\.{3}')).get('href')

        first = int(re.sub(r'\;.+', '', date[2]))
        last = int(date[4])
        statUrl = 'https://aeronet.gsfc.nasa.gov' + statHref.replace('®', '&re')
        print('\n', first, last, stat, statUrl)
        if 2005 <= first <= 2012 or 2005 <= last <= 2012 or (first <= 2005 and last >= 2012):
            # 模拟检索动作
            try:
                driver.get(statUrl)
                for item in downItem:
                    checkbox = driver.find_element(By.ID, item)
                    checkbox.click()
                checkbox = driver.find_element(By.ID, 'Level15')
                checkbox.click()
            except Exception as e:
                print(e)
                print(stat, url,
                      file=open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SSA\error.txt', 'a', encoding='utf-8'))
                continue
            # time.sleep(3)
            for year in range(max(first, 2005), min(last, 2012) + 1):
                filename = '{0}0101_{0}1231_{1}.zip'.format(year, stat)
                filepath = r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SSA\{}'.format(filename)
                if os.path.exists(filepath):
                    print('Done ', year)
                    continue
                url = 'https://aeronet.gsfc.nasa.gov/zip_files_v3/inv/{}'.format(filename)
                try:
                    select1 = Select(driver.find_element(By.XPATH, '//*[@id="Year1"]'))
                    select1.select_by_visible_text(str(year))
                except Exception as e:
                    print(e)
                    print(stat, year, url,
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
                            except Exception as e:
                                print(e, stat, year)
                                print(stat, year, url,
                                      file=open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SSA\error.txt', 'a',
                                                encoding='utf-8'))
# end
