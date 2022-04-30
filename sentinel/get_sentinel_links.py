from bs4 import BeautifulSoup
import pandas as pd
import requests

# filepath = 'Sentinel-5P Pre-Operations Data Hub.html'  # 保存的网页，自己按照实际保存位置调整
filepath = 'D:/SOFTDOCS/Tencent/WeChat/WeChat Files/songqi0708/FileStorage/File/2021-08/21.7.html'
with open(filepath, 'rb') as f:
    ss = f.read()

soup = BeautifulSoup(ss, 'html.parser')
# 获取所有id为cart-row-attributes的div标签
divfind = soup.find_all('div', attrs={"class": "list-link selectable"})
linklist = []
# idlist = []
for df in divfind:
    # 获取满足条件的div下的a标签
    # 提取a标签的内容，即为数据链接
    link = df.find('a').string
    # id = link.split('\'')[1]
    linklist.append(link)
    # idlist.append(id)

divfind = soup.find_all('div', attrs={"class": "list-item-title ng-binding"})
itemList = []
for df in divfind:
    item = df
    itemList.append(item)

linkDataframe = pd.DataFrame(linklist)
# iddataframe = pd.DataFrame(idlist)
itemDataframe = pd.DataFrame(itemList)

# 将数据链接写出
with pd.ExcelWriter('D:/SOFTDOCS/Tencent/WeChat/WeChat Files/songqi0708/FileStorage/File/2021-08/21.7.xlsx') as hifile:
    linkDataframe.to_excel(hifile, sheet_name='URL', header=False, index=False)
    # iddataframe.to_excel(hifile, sheet_name='ID', header=False, index=False)
    itemDataframe.to_excel(hifile, sheet_name='fileName', header=False, index=False)

linkDataframe.to_csv('Httpandid.csv')

