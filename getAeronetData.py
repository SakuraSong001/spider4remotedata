import os
import csv
import time
import re
import ssl
from bs4 import BeautifulSoup
from six.moves import urllib
import requests
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
ssl._create_default_https_context = ssl._create_unverified_context
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
    'Connection': 'keep-alive'
}

session = requests.session()
driver = webdriver.Edge()


def get_stations(area_file):
    result = []
    pattern = r'https\:\/\/aeronet\.gsfc\.nasa\.gov\/cgi\-bin\/data\_display\_aod\_v3\?site\=.+'

    # 本地页面
    chinaAreaPage = r'AERONET Data Display Interface - WWW DEMONSTRAT.html'
    soup = BeautifulSoup(open(chinaAreaPage, 'r', encoding='utf-8').read(), 'html.parser')
    aList = soup.find_all('a')
    for item in aList:
        sHref = item.get('href')
        if re.match(pattern, str(sHref)):
            station = re.sub(r'\n', '', item.get_text())
            geoInfo = re.sub(r'\n+.+\(\s', r'(', item.parent.get_text())

            response = session.get(sHref, headers=header)
            beautifulSoup = BeautifulSoup(response.text, 'html.parser')

            pageUrl = beautifulSoup.find('a', text=re.compile(r'More AERONET Downloadable Products\.{3}')).get('href')

            date = beautifulSoup.find(text=re.compile(r'Start Date.+')).split('-')
            start_year = re.sub(r'\;.+', '', date[2])
            latest_year = date[4]

            result.append([station, geoInfo, pageUrl, start_year, latest_year])
    # print(result, file=open(area_file, 'w', encoding='utf-8'))
    result = np.array(result)
    dataframe = pd.DataFrame(
        {'station': result[:, 0], 'geoInfo': result[:, 1], 'pageUrl': result[:, 2], 'start_year': statList[:, 3],
         'latest_year': result[:, 4]}
    )
    dataframe.to_csv(area_file, index=False, sep=',', encoding='utf-8')
    return result


if __name__ == '__main__':
    chinaAreaFile = r'F:\WORKSPACE\DBN-PARASOL\aeronet data 1.5\aeroChinaGeo.csv'
    if os.path.exists(chinaAreaFile):
        with open(chinaAreaFile, 'r', encoding='utf-8') as csvFile:
            reader = csv.reader(csvFile)
            stationList = [row for row in reader]
        # print(stationList[1:])
    else:
        stationList = get_stations(chinaAreaFile)

    for stat, geo, statHref, first, latest in stationList[137:]:
        if '2005' <= first <= '2012' or '2005' <= latest <= '2012' or (first <= '2005' and latest >= '2012'):
            print('\n')
            begin = end = '0'

            statUrl = 'https://aeronet.gsfc.nasa.gov/cgi-bin/' + statHref.replace('®', '&re')
            driver.get(statUrl)
            time.sleep(3)
            ele = driver.find_element(By.XPATH, '//*[@id="Year1"]')
            options = ele.find_elements(By.TAG_NAME, 'option')
            for option in options:
                # print(option.get_attribute('value'))
                # print(option.text)
                if option.text >= '2013':
                    break
                if begin == '0' and '2005' <= option.text:
                    begin = option.text
                if end < option.text:
                    end = option.text
            # -- end for options --
            if begin == '0' or end == '0':
                print('wrong time', stat, first, latest, begin, end, statUrl)
                continue
            print(stat, first, latest, begin, end, statUrl)

            # download file
            for year in range(int(begin), int(end) + 1):
                # print(year)
                filename = '{0}0101_{0}1231_{1}.zip'.format(year, stat)
                filepath = r'F:\WORKSPACE\DBN-PARASOL\aeronet data 1.5\{}'.format(filename)
                url = 'https://aeronet.gsfc.nasa.gov/zip_files_v3/{}'.format(filename)
                if os.path.exists(filepath):
                    print('exist ', year, url)
                    continue

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
                    aod15_checkbox = driver.find_element(By.NAME, 'AOD15')
                    aod15_checkbox.click()
                except NoSuchElementException:
                    print('No such aod 1.5 ', year, url)
                    break
                submit = driver.find_element(By.NAME, 'Submit')
                submit.click()
                time.sleep(30)
                try:
                    opener = urllib.request.build_opener()
                    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'), ('Cookie', '_ga=GA1.2.479127296.1609393316; _ga=GA1.4.479127296.1609393316'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(url, filepath)
                    print('Done ', year, url)
                except urllib.error.HTTPError:
                    print('Not Found', year, url)
                    print(stat, year, url, file=open(r'F:\WORKSPACE\DBN-PARASOL\aeronet data 1.5\notfound.txt', 'a', encoding='utf-8'))

