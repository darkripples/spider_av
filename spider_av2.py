# -*- coding:utf8 -*-

import requests, re, os
from lxml import etree

# 存储目录.取当前
BASE_PATH = './'
# 页数
CNT = 1000
# 起始页
MAX = 2
# url
URL = "http://www.hmrenti.com"
# 下载的url
DOWNLOAD_URL = "https://www.bthuahua.net"
# 是否有码
HAVE_MA = "all" # no,yes,all

def main(num):
    if(num>1):
        url = (URL+"/fanhao/%s.html") % num
    else:
        url = (URL+"/fanhao/index.html")
    res = requests.get(url)
    cont = res.content.lower().decode('gb18030', 'ignore')
    if res.status_code == 200:
        # 取row
        page = etree.HTML(cont)
        hrefs = page.xpath(u"//td[@style='text-indent: 1em']/a")
        for h in hrefs:
            urlT = h.attrib.get('href')
            m_fh = urlT.split("/")[-1].split(".")[0]
            title = h.text.split(m_fh)[1]
            
            # 打开明细view-source:http://www.hmrenti.com/fanhao/IPX-142.html
            resMx = requests.get(URL+urlT)
            contMx = resMx.content.lower().decode('gb18030')
            pageMX = etree.HTML(contMx)
            
            nameMx = pageMX.xpath(u"//meta[@name='keywords']")
            m_name = nameMx[0].attrib.get('content').split(",")[1]
            
            m_ma = contMx.split("<p>是否有码：")[1].split("</p>")[0]
            # check
            if HAVE_MA=="no" and m_ma=="有码": return
            if HAVE_MA=="yes" and m_ma!="有码": return
            
            # 初始化存储目录.主角/步兵or骑兵/番号
            nowPath = os.path.join(BASE_PATH, m_name, m_ma, m_fh)
            if not os.path.exists(nowPath):
                os.makedirs(nowPath)
            else:
                return
            
            print(str(m_fh) + ":" + m_ma + title)
            
            # 取封面图并存储
            imgMx = pageMX.xpath(u"//div[@class='article_img_left']/img")
            m_img = imgMx[0].attrib
            bytes = requests.get(m_img.get('src'))
            f = open(os.path.join(nowPath, title+'.jpg' ), 'wb')
            f.write(bytes.content)
            f.flush()
            f.close()
            
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
            f2 = open(os.path.join(nowPath, title+'.txt'), 'wb')
            f2.write(download_str.encode('utf8'))
            f2.flush()
            f2.close()
            

if __name__=="__main__":
    end = MAX
    while end < (MAX+CNT):
        try:
            main(end)
        except Exception as ex:
            # 部分形如URL的页内容不完全符合main()中的html结构，这里只处理符合的数据
            print(ex)
        end += 1
