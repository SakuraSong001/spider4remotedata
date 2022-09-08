# spider4remotedata - AERONET  
本项目提供AERONET AOD SSA FMF等数据，以及PARASOL HDF和哨兵五号SENTINEL-5数据下载连接的批量获取。  
写在前面的小结：预检索动态资源，正则化工具匹配标签，SELENIUM模拟人为操作。  
## 更新  
- 7.21 增加多线程并行下载和selenium后台运行。  
- 5.05 增加FMF、SSA数据下载（见GitHub），针对SSA、FMF等产品的网站网页解析进行修改，实现自动化批量下载。  
- 4.10更新 通过CURL、WGET等方式下载目标数据。
[AOD AND SDA : Data - Aerosol Robotic Network (AERONET) Homepage (nasa.gov)  ](https://aeronet.gsfc.nasa.gov/print_web_data_help_v3_new.html)
__Wget__  
wget --no-check-certificate  -q  -O test.out "https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3?site=Cart_Site&year=2000&month=6&day=1&year2=2000&month2=6&day2=14&AOD15=1&AVG=10"  
__Curl__  
curl -s -k -o test.out "https://aeronet.gsfc.nasa.gov/cgi-bin/print_web_data_v3?site=Cart_Site&year=2000&month=6&day=1&year2=2000&month2=6&day2=14&AOD15=1&AVG=10"  
## AERONET AOD 数据自动化下载 + PYTHON + SELENIUM  
### 1. 获取下载地址  
__AERONET AOD 数据下载__  
AErosol RObotic NETwork (AERONET)是由NASA 和 LOA-PHOTONS (CNRS) 联合建立的地基气溶胶遥感观测网，提供对不同气溶胶状态下的光谱气溶胶光学深度（AOD），反演产物和可沉淀水的全球分布式观测。现行版本 3 AOD 数据提供：级别 1.0（未筛选）、级别 1.5（云筛选和质量控制）和级别 2.0（质量保证）。  
官网地址：[Aerosol Robotic Network (AERONET) Homepage (nasa.gov) ](https://aeronet.gsfc.nasa.gov/)  
![这是图片](https://img-blog.csdnimg.cn/ce4d9e0cc4f2480d87af56d1fbcc64a3.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_19,color_FFFFFF,t_70,g_se,x_16)  
Aeronet 网站支持灵活筛选条件，可根据需求下载特定时间、级别、站点的数据。同时可通过网页提供的筛选功能筛选符合特定条件的数据。  
![这是图片](https://img-blog.csdnimg.cn/5f88fd2049584b7f84f7d7596f1eb828.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  
例如下载 2012年 Alboran 站点的 AOD1.5 数据，点击 2012 - level 1.5 - Alboran 进入站点数据详情页面，点击 AOD Level 1.5 进入数据请求下载页面，点击 Accept 即可下载数据。
![这是图片](https://img-blog.csdnimg.cn/aba3435574ae4d61be451b9d9df75bf5.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  
![这是图片](https://img-blog.csdnimg.cn/d1e92391258d4fe5b11566ad6511ff70.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  

![这是图片]()  
### 利用 PYTHON + SELENIUM 自动化下载中国站点数据  
__获得站点URL列表__  
首先通过网站提供的地图筛选工具，大致选择中国范围，并将页面另存为本地HTML文件，利用BEAUTIFULSOUP解析页面获得站点列表。利用正则化工具筛选、获得所有站点URL，并通过父节点获得站点名称、经纬度等信息。  
![这是图片](https://img-blog.csdnimg.cn/a6fb46888d41455d9fc7bce5002b6d7a.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  
![这是图片](https://img-blog.csdnimg.cn/6a86ac4082aa4152a8370b305f34b0da.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  
```python
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
```  
__获取站点数据时间__  
根据给定时间范围筛选站点、并获取站点数据的有效时间节点。  
```python
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
__下载数据__  
由于aeronet网站的特殊设置，部分数据需要先检索才可以下载，否则按照正确的下载地址也会提示 HTTPError: 404 not found。  
```python
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
批量自动加载结果：  
![这是图片](https://img-blog.csdnimg.cn/741e9c7e1dba4e48a146f82c570140af.png?x-oss-process=image/watermark,type_d3F5LXplbmhlaQ,shadow_50,text_Q1NETiBARXZlbHluIFNvbmc=,size_20,color_FFFFFF,t_70,g_se,x_16)  
