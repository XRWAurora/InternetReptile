import jieba
import re
import pyecharts.options as opts
from pyecharts.charts import WordCloud
import pymysql


def datacollect(c):
    global resultlist
    i = 0
    sql = "SELECT Content FROM 集团新闻"
    db = pymysql.Connect(host='localhost', user='root', password='password', database='newpoly')
    cursor = db.cursor()
    try:
        db.ping(reconnect=True)  # 在每次运行sql之前，ping一次，如果连接断开就重连。否则会报错
        cursor.execute(sql)  # 执行sql语句
        while i < c:
            result = cursor.fetchone()  # 取一条结果进行分析
            i += 1
        resultlist = list(result)  # 将获取到的数据转为列表
        # print(resultlist)
        db.commit()  # 提交事务
    except pymysql.Error as e:
        print(e)
        db.rollback()  # 若出现错误，则回滚
        db.close()  # 关闭数据库
    return resultlist


def stopwordslist():  # 创建停用词列表
    f = open('baidu_stopwords.txt', encoding='UTF-8')
    stopwords = []
    for line in f:
        stopword = line.strip()
        stopwords.append(stopword)
    # print(stopwordlist)
    return stopwords


def removestopwords(c):  # 去掉停用词
    global outstrlist
    raw = datacollect(c)
    outstrlist = []
    for i in raw:
        sentence_depart = jieba.cut(i.strip())
    stopwords = stopwordslist()
    outstr = ''
    for word in sentence_depart:
        if word not in stopwords:
            if word != '\t':
                outstr += word
    outstrlist.append(outstr)
    return outstrlist


def dataprocessing(c):  # 数据处理函数
    global items
    items = {}  # 字典，用于存放前15的词语
    rawlist = removestopwords(c)
    for i in rawlist:
        line = re.sub("[A-Za-z0-9\'\：\·\—\，\。\“ \”\n\u3000\？\、\'*\',\'\r\xa0\《\》\!\-\(\)]", "", i)
        words = jieba.lcut(line)
        # print(words)
        counts = {}  # 创建一个字典，用于统计文章中每个词出现的次数
        for word in words:
            if len(word) == 1:  # 单个词语不计算在内
                continue
            else:
                counts[word] = counts.get(word, 0) + 1  # 遍历所有词语，每出现一次其对应的值加 1
        items = list(counts.items())  # 将键值对转换成列表
        items.sort(key=lambda x: x[1], reverse=True)  # 根据词语出现的次数进行从大到小排序
        # lambda函数 lambda 参数：操作
        # ls = [('s','he',3), ('q', 'she', 2), ('p', 'they', 1)]中，x:x[0]相当于按's', 'q', 'p'进行排序
        for i in range(15):  # 选出排名前15的词语
            word, count = items[i]
            # print("{0:<5}{1:>5}".format(word, count))
    return items


def wordcloud(c):
    data = dataprocessing(c)
    (
        WordCloud()
            .add(series_name="新闻热词", data_pair=data, word_size_range=[6, 66])
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="新闻热点分析", title_textstyle_opts=opts.TextStyleOpts(font_size=23)
            ),
            tooltip_opts=opts.TooltipOpts(is_show=True),
        )
            .render("groupnews_wordcloud.html")
    )


if __name__ == '__main__':
    n = int(input("请输入要分析哪一篇: \n")) + 1
    for c in range(1, n):
        wordcloud(c)
