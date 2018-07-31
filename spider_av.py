# -*- coding:utf8 -*-

import requests, re, os
from lxml import etree

# 存储目录.取当前
BASE_PATH = './'
# 次数
CNT = 1000
# 起始页
MAX = 28860-100-1000#28860-you
# url
URL = "http://m.233mr.com/show/%s.html"
# 下载的url
DOWNLOAD_URL = "https://www.bthuahua.net"
# 是否有码
HAVE_MA = "no" # no,yes,all

def main(num):
    url = URL % num
    res = requests.get(url)
    cont = res.content.lower().decode('utf8')
    if res.status_code == 200:
        # 取title
        res_h1 = r'<h1>(.*?)</h1>'
        m_h1 =  re.findall(res_h1,cont,re.S|re.M)[0].upper()
        # 取performer
        page = etree.HTML(cont)
        hrefs = page.xpath(u"//div[@class='neiye-dh-left']/a")
        m_name = hrefs[0].text
        # 取番号
        m_fh = cont.split("<p>番号：")[1].split("</p>")[0]
        m_ma = cont.split("<p>是否有码：")[1].split("</p>")[0]
        # check
        if HAVE_MA=="no" and m_ma=="有码": return
        if HAVE_MA=="yes" and m_ma!="有码": return
        print(str(num) + ": " + m_ma + " | " + m_h1)
        
        # 初始化存储目录.主角/步兵or骑兵/番号
        nowPath = os.path.join(BASE_PATH, m_name, m_ma, m_fh)
        if not os.path.exists(nowPath):
            os.makedirs(nowPath)
        
        # 取封面图并存储
        hrefs = page.xpath(u"//div[@class='letter-box']/p/img")
        m_img = hrefs[0].attrib
        bytes = requests.get(m_img.get('src'));
        f = open(os.path.join(nowPath, m_img.get('title')+'.jpg' ), 'wb');
        f.write(bytes.content);
        f.flush();
        f.close();
        
        # 取下载地址.模拟请求DOWNLOAD_URL搜索
        download_str = ""
        down = requests.get(DOWNLOAD_URL + "/index.php?r=files/index&kw=" + m_fh)
        down_nr = down.content.decode('utf8')
        down_nr = etree.HTML(down_nr)
        li = down_nr.xpath(u"//ul[@class='row list-group']/li/a")
        for i in li:
            d = requests.get(DOWNLOAD_URL + i.attrib.get('href'))
            d_nr = d.content.decode('utf8')
            d_nr = etree.HTML(d_nr)
            h = d_nr.xpath(u"//span[@class='label label-warning']")
            size = h[0].text
            hurl = d_nr.xpath(u"//h4/a")
            download4xunlei = hurl[0].attrib.get('href')
            download_str += size + "\t\t" + download4xunlei + "\n"
        print(download_str)
        print()
        f2 = open(os.path.join(nowPath, m_img.get('title')+'.txt'), 'wb')
        f2.write(download_str.encode('utf8'))
        f2.flush()
        f2.close()
        

if __name__=="__main__":
    end = MAX
    while end > (MAX-CNT):
        try:
            main(end)
        except:
            # 部分形如URL的页内容不完全符合main()中的html结构，这里只处理符合的数据
            pass
        end -= 1
