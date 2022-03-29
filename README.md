# aeronet_spider

AErosol RObotic NETwork (AERONET)是由NASA 和 LOA-PHOTONS (CNRS) 联合建立的地基气溶胶遥感观测网，提供对不同气溶胶状态下的光谱气溶胶光学深度（AOD），
反演产物和可沉淀水的全球分布式观测。官网地址：[Aerosol Robotic Network (AERONET) Homepage (nasa.gov)](https://aeronet.gsfc.nasa.gov/)

现行版本 3 AOD 数据提供：级别 1.0（未筛选）、级别 1.5（云筛选和质量控制）和级别 2.0（质量保证）。


![Aerosol Robotic Network (AERONET) Homepage (nasa.gov)](https://aeronet.gsfc.nasa.gov/cgi-bin/bamgomas_maps_v3?long1=-180&long2=180&lat1=-90&lat2=90&multiplier=2&what_map=4&level=1&place_code=10&place_limit=0)

### 1. 获取站点详情列表

首先通过网站提供的地图筛选工具，并将中国区域页面另存为本地HTML文件，利用BEAUTIFULSOUP和正则表达式筛选、获得所有站点URL，并通过父节点获得站点名称、经纬度等信息。

```
  pattern = r'https\:\/\/aeronet\.gsfc\.nasa\.gov\/cgi\-bin\/data\_display\_aod\_v3\?site\=.+'
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
```

### 2. 匹配目标站点 
根据给定时间范围筛选站点、并获取站点数据的有效时间节点。
```
if '2005' <= first <= '2012' or '2005' <= latest <= '2012' or (first <= '2005' and latest >= '2012'):# 不在此时间范围内的直接跳过
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
```

### 3. 预检索网站资源
由于aeronet网站的特殊设置，部分数据需要先检索才可以下载，否则按照正确的下载地址也会提示 HTTPError: 404 not found。
```
# 模拟检索动作
statUrl = 'https://aeronet.gsfc.nasa.gov/cgi-bin/' + statHref.replace('®', '&re')
driver.get(statUrl)
time.sleep(3)
select1 = Select(driver.find_element(By.XPATH, '//*[@id="Year1"]'))
select1.select_by_visible_text(str(year))
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
```

### 4. 下载数据
```
# download file
for year in range(int(begin), int(end) + 1):
    # print(year)
    filename = '{0}0101_{0}1231_{1}.zip'.format(year, stat)
    filepath = r'F:\WORKSPACE\DBN-PARASOL\aeronet data 1.5\{}'.format(filename)
    url = 'https://aeronet.gsfc.nasa.gov/zip_files_v3/{}'.format(filename)
    if os.path.exists(filepath):
        print('exist ', year, url)
        continue
 
    try:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46'), ('Cookie', '_ga=GA1.2.479127296.1609393316; _ga=GA1.4.479127296.1609393316'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filepath)
        print('Done ', year, url)
    except urllib.error.HTTPError:
        print('Not Found', year, url)
        print(stat, year, url, file=open(r'F:\WORKSPACE\DBN-PARASOL\aeronet data 1.5\notfound.txt', 'a', encoding='utf-8'))
```

————————————————

版权声明：本文为CSDN博主「Evelyn Song」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/qq_33561322/article/details/123807409
