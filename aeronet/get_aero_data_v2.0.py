#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2022/4/29 16:01
# @Author : Evelyn Song
import wget
import time
import re
import ssl
import numpy as np
from bs4 import BeautifulSoup
from six.moves import urllib
import requests
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

if __name__ == "__main__":
    ssl._create_default_https_context = ssl._create_unverified_context
    driver = webdriver.Edge()
    downItem = ['AOD10', 'AOD15', 'AOD20', 'TOT10', 'TOT15', 'TOT20', 'SDA10', 'SDA15', 'SDA20']
    downItem = 'SDA15'  # AOD15
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
        'Connection': 'keep-alive'
    }
    session = requests.session()
    statList = np.loadtxt(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\GEO_2.0\AERONET GEO.txt', dtype=str,
                          usecols=0, skiprows=1, delimiter=',')
    for stat in statList:
        sHref = r'https://aeronet.gsfc.nasa.gov/cgi-bin/data_display_aod_v3?site={}&nachal=2&level=1&place_code=10'.format(
            stat)
        response = session.get(sHref, headers=header)
        beautifulSoup = BeautifulSoup(response.text, 'html.parser')

        date = beautifulSoup.find(text=re.compile(r'Start Date.+')).split('-')
        statHref = beautifulSoup.find('a', text=re.compile(r'More AERONET Downloadable Products\.{3}')).get('href')
        first = int(re.sub(r'\;.+', '', date[2]))
        last = int(date[4])
        print(first, last, stat)
        if 2005 <= first <= 2012 or 2005 <= last <= 2012 or (first <= 2005 and last >= 2012):
            for year in range(max(first, 2005), min(last, 2012) + 1):
                # href = 'https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3?site={}&year={}&month={}&day={}&year2={}&month2={}&day2={}&{}=1&AVG={}'.format(stat, year, 1, 1, year, 12, 31, 'SDA15', all_point)
                # filename = wget.download(href, out=r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\{0}0101_{0}1203_{1}.ONEILL_lev10'.format(year, stat))
                # input()
                filename = '{0}0101_{0}1231_{1}.zip'.format(year, stat)
                filepath = r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\{}'.format(filename)
                url = 'https://aeronet.gsfc.nasa.gov/zip_files_v3/{}'.format(filename)

                # 模拟检索动作
                statUrl = 'https://aeronet.gsfc.nasa.gov/cgi-bin/' + statHref.replace('®', '&re')
                driver.get(statUrl)
                time.sleep(3)
                try:
                    select1 = Select(driver.find_element(By.XPATH, '//*[@id="Year1"]'))
                    select1.select_by_visible_text(str(year))
                except NoSuchElementException:
                    print('No such year ', year, url)
                    break
                select2 = Select(driver.find_element(By.XPATH, '//*[@id="Year2"]'))
                select2.select_by_visible_text(str(year))
                try:
                    for item in downItem:
                        checkbox = driver.find_element(By.NAME, item)
                        checkbox.click()
                except NoSuchElementException:
                    print('No such ', downItem, year, url)
                    break
                submit = driver.find_element(By.NAME, 'Submit')
                submit.click()
                time.sleep(30)
                try:
                    urllib.request.urlretrieve(url, filepath)
                    print('Done ', year, url)
                except urllib.error.HTTPError:
                    print('Not Found', year, url)
                    print(stat, year, url,
                          file=open(r'F:\WORKSPACE\DBN-PARASOL\AERO_DATA_1.5\SDA\notfound.txt', 'a', encoding='utf-8'))
# end
