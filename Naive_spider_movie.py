from urllib.request import urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from time import sleep
import re
import pymysql
import time
#利用BeautifulSoup库爬取电影天堂网站上电影信息
#全局变量，来储存主网页的链接
moviesLinks = set()
#数据库信息
conn = pymysql.connect(host = '127.0.0.1',port = 3306,user='root',passwd='yang96110210',db='mysql',charset = 'utf8')
cur = conn.cursor()

#采用movies数据库
cur.execute('use movies')

def getLinks(pageUrl):
    global moviesLinks
    html = urlopen(pageUrl)
    bs4 = BeautifulSoup(html,"xml")
    for link in bs4.findAll("a",{"href":re.compile("/html/gndy/+[a-z]+/[0-9]+/[0-9]+\.html")}):  #正则表达式选取电影链接(过滤掉游戏下载链接，动漫链接，综艺链接)
        if link.attrs['href'] not in moviesLinks:
            newLink = link.attrs['href']
            moviesLinks.add(newLink)
            getPageImformation(newLink)

def getPageImformation(pageUrl):
    try:
        url = 'http://www.dytt8.net/' + pageUrl
        html = urlopen(url)
        bs4 = BeautifulSoup(html, "xml")
        name = bs4.find("div",{"id":"Zoom"}).p.get_text().split('◎')[1][4:].strip()  #名字的处理
        downloadLink = bs4.find("td",{"bgcolor":"#fdfddf"}).a.get_text()
        print(name+ " "+downloadLink)
        store(name,downloadLink)
    except Exception:
        print("不符合模式的页面！")
    print("--------------------------------\n")

def store(name,downloadLink):
    cur.execute('select * from Movie_heaven where name = %s',name)
    row = cur.fetchone()
    if row == None:
        #写入movies数据库中的Movie_heaven表
        cur.execute('insert into Movie_heaven(name,downloadLink) values (%s,%s)',(name,downloadLink))
        cur.connection.commit()
    else:
        print('已经存在数据库中！')

while(True):
    getLinks('http://www.dytt8.net/')
    time.sleep(20)
cur.close()
conn.close()