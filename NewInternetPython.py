import requests
from lxml import etree
import pymysql
import time
import re


def databaseopreation(Url, Title, Date, Summary, Content, Pictureurl=None):
    db = pymysql.Connect(host='localhost', user='root', password='password', database='newpoly')
    cursor = db.cursor()
    sql = """INSERT INTO metadata(Url,
                 Title,Date,Summary,Content,Pictureurl)
                 VALUES (%s,%s,%s,%s,%s,%s)"""
    args = (Url, Title, Date, Summary, Content, Pictureurl)
    try:
        db.ping(reconnect=True)  # 在每次运行sql之前，ping一次，如果连接断开就重连。否则会报错
        cursor.execute(sql, args)  # 执行sql语句
        db.commit()  # 提交事务
    except pymysql.Error as e:
        print(e)
        db.rollback()  # 若出现错误，则回滚
    db.close()  # 关闭数据库


def ListToString(list):
    temp = [str(i) for i in list]  # 使用列表推导式把列表中的单个元素转化为str类型
    list1 = ''.join(temp)  # 把列表中的元素放在空串中，元素间用空格隔开
    return list1


def totalpage():
    global pages
    temp = []
    pages = []
    for i in range(1, 6):
        url = 'https://www.poly.com.cn/%4d.html' % (i + 1965)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
        response = requests.get(url, headers=headers)
        html = etree.HTML(response.text)
        result = etree.tostring(html, encoding='utf-8').decode("utf-8")
        totalpage = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[9]/span/span[3]/text()'
        totalpages = (html.xpath(totalpage))
        temp.append(totalpages)
    for j in temp:
        for k in j:
            page = re.sub('/', '', str(k))
            pages.append(page)
    return pages


def internetpython(Real_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'}
    requests.DEFAULT_RETRIES = 5  # 尝试重连次数
    s = requests.session()
    s.keep_alive = False  # 默认为True（保持连接）
    response = s.get(Real_url, headers=headers, timeout=300)
    html = etree.HTML(response.text)
    # print(html)
    result = etree.tostring(html, encoding='utf-8')
    # print(result.decode("utf-8"))
    newsurls = []
    titles = []
    dates = []
    summarys = []
    content = []
    images = []
    for i in range(1, 8):
        newsurl = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[%d]/div[2]/a/@href' % i
        title = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[%d]/div[2]/a/@title' % i
        date1 = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[%d]/div[1]/p[1]/text()' % i
        date2 = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[%d]/div[1]/b/text()' % i
        abstract = '/html/body/form/div[3]/div[4]/div[2]/div[2]/div/div/div[2]/div/div[2]/div/div/div[%d]/div[3]/text()' % i
        # print(html.xpath(path))
        newsurls.append(html.xpath(newsurl))
        titles.append(html.xpath(title))
        date = html.xpath(date1) + list('-') + html.xpath(date2)
        dates.append(date)
        summarys.append(html.xpath(abstract))
        # 打开具体的网页获取新闻的内容和图片url

        Web_url = ''.join(newsurls[i - 1])
        requests.DEFAULT_RETRIES = 5
        t = requests.session()
        t.keep_alive = False  # 默认为True（保持连接）
        Web_response = t.get(Web_url, headers=headers, timeout=300)
        Web_html = etree.HTML(Web_response.text)
        content.append(Web_html.xpath('//p//text()'))
        images.append(Web_html.xpath('//p/img/@src'))
    # 输出数据
    for i in range(7):
        Str_url = ListToString(newsurls[i])
        print(Str_url)
        Str_title = ListToString(titles[i])
        print(Str_title)
        Str_date = ListToString(dates[i])
        print(Str_date)
        Str_abstract = ListToString(summarys[i])
        print(Str_abstract)
        Str_text = ListToString(content[i])
        print(Str_text)
        imgurl = ''
        print(images[i])
        # 保存图片
        for j in images[i]:
            if len(j) == 0:
                continue
            else:
                img_url = ListToString(j)
                image_url = 'https://www.poly.com.cn' + img_url
                imgurl = imgurl + ' ' + image_url

                image_respond = requests.get(image_url, headers=headers)
                file_name = img_url.split('/')[-1]
                path = '新闻图片\\' + file_name
                print(path)
                try:
                    with open(path, 'wb') as f:
                        f.write(image_respond.content)
                        f.close()
                except:
                    continue

        print(imgurl)
        print('\n')
        databaseopreation(Str_url, Str_title, Str_date, Str_abstract, Str_text, imgurl)  # 将数据写入数据库


if __name__ == '__main__':
    totalpage()
    for i in range(1, 6):
        url = 'https://www.poly.com.cn/l/%4d-%4d-' % (i + 1965, i + 6723)
        if i == 1:
            n = int(pages[0])+1
        elif i == 2:
            n = int(pages[1])+1
        elif i == 3:
            n = int(pages[2])+1
        elif i == 4:
            n = int(pages[3])+1
        else:
            n = int(pages[4])+1
        for j in range(1, n):
            Real_url = url + str(j) + '.html'
            # print(Real_url)
            internetpython(Real_url)
            time.sleep(5)
