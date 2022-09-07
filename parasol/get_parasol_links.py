from bs4 import BeautifulSoup
import requests

# cookie
# 登录信息 检查元素 - network - login post
formData = {
    'login': 'Evelyn',
    'password': '210601',
    'submit': 'Submit'
}
cookie = 'cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _pk_id.1.749d=15526b02b98e9d29.1637665904.; viewed_cookie_policy=yes; PHPSESSID=kh0uv4asc7di6375dj4shpu4h0; related_Admin=0; thisUrl=https://www.icare.univ-lille.fr/; _pk_ref.1.749d=["","",1658411132,"https://www.icare.univ-lille.fr/"]; _pk_ses.1.749d=1; lastUrl=https://www.icare.univ-lille.fr/'

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
           'Connection': 'keep-alive',
           'Cookie': cookie}
session = requests.session()

urlParasol = 'https://www.icare.univ-lille.fr/data-access/data-archive-access/?dir=PARASOL/L1_B-HDF.v1.01/'
response = session.get(urlParasol, headers=header)
print(response.text, file=open(r'C:\Users\evelyn\Desktop\para.html', 'w', encoding='utf8'))

# 解析网页
soup = BeautifulSoup(response.text, 'html.parser')
yList = []
for item in soup.select('div[id="listing"] div a'):
    yList.append(item.get('href'))
print(yList)

dList = []
for url in yList[1:]:
    response = session.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    for item in soup.select('div[id="listing"] div a'):
        dList.append(item.get('href'))
print(dList)


for url in dList[1:]:
    response = session.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    for item in soup.select('div[id="listing"] div a'):

        print(item, file=open(r'C:\Users\evelyn\Desktop\h5List.txt', 'a', encoding='utf8'))
