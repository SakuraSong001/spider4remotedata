from bs4 import BeautifulSoup
import requests

# cookie
# 登录信息 检查元素 - network - login post
formData = {
    'login': 'Evelyn',
    'password': '210601',
    'submit': 'Submit'
}
cookie = '''related_Admin=0; cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _pk_id.1.749d=15526b02b98e9d29.1637665904.; viewed_cookie_policy=yes; PHPSESSID=p4flkano7fo1p8dmu21jnfh1s1; related_Admin=0; proUrl=/asd-content/archive/; _pk_ref.1.749d=["","",1648367377,"https://www.icare.univ-lille.fr/"]; _pk_ses.1.749d=1; icare_session_id=5a126b925ca4808bc763edffaf081aa6; thisUrl=https://www.icare.univ-lille.fr/; lastUrl=https://www.icare.univ-lille.fr/'''
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36 Edg/99.0.1150.30',
           'Connection': 'keep-alive',
           'Cookie': cookie}
session = requests.session()

# download test
# h5 = 'https://web-backend.icare.univ-lille.fr/archive_file/download.php?file=PARASOL/L1_B-HDF.v1.01/2005/2005_03_22/POLDER3_L1B-BG1-007166M_2005-03-22T08-57-04_V1-01.h5'
# response = session.get(h5, headers=header, verify=False)
# with open(r'C:\Users\evelyn\Desktop\{}'.format(h5.split('/')[-1]), 'wb') as f:
#     f.write(response.content)
# f.close()

# urlLogin = 'https://www.icare.univ-lille.fr/data-access/data-archive-access/'
# response = session.get(urlLogin, headers=header)
# print(response.text, file=open(r'C:\Users\evelyn\Desktop\response.html', 'w', encoding='utf8'))

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


h5List = []
for url in dList[1:]:
    response = session.get(url, headers=header)
    soup = BeautifulSoup(response.text, 'html.parser')
    for item in soup.select('div[id="listing"] div a'):
        h5List.append(item.get('href'))
print(h5List, file=open(r'C:\Users\evelyn\Desktop\h5List.txt', 'w', encoding='utf8'))
