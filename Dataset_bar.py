from pyecharts import options as opts
from pyecharts.charts import Bar
from itertools import chain
import pymysql


def datacollect(sql):
    global resultlist
    db = pymysql.Connect(host='localhost', user='root', password='password', database='newpoly')
    cursor = db.cursor()
    try:
        db.ping(reconnect=True)  # 在每次运行sql之前，ping一次，如果连接断开就重连。否则会报错
        cursor.execute(sql)  # 执行sql语句
        result = cursor.fetchall()  # 取所有行结果
        resultlist = list(chain.from_iterable(result))  # 查询结果返回的元组转成列表
        # print(resultlist)
        db.commit()  # 提交事务
    except pymysql.Error as e:
        print(e)
        db.rollback()  # 若出现错误，则回滚
        db.close()  # 关闭数据库
    return resultlist


def datadeal(resultlist):
    global year2021, year2020, year2019, year2018, year2017
    year2021 = year2020 = year2019 = year2018 = year2017 = 0
    for i in resultlist:
        if '2021' in i:
            year2021 += 1
        elif '2020' in i:
            year2020 += 1
        elif '2019' in i:
            year2019 += 1
        elif '2018' in i:
            year2018 += 1
        elif '2017' in i:
            year2017 += 1
    return year2017, year2018, year2019, year2020, year2021


def dataanalysis():
    sql = "SELECT Date FROM 集团新闻"
    datacollect(sql)
    gn2017, gn2018, gn2019, gn2020, gn2021 = datadeal(resultlist)
    sql1 = "SELECT Date FROM 企业新闻"
    datacollect(sql1)
    en2017, en2018, en2019, en2020, en2021 = datadeal(resultlist)
    sql2 = "SELECT Date FROM 国资动态"
    datacollect(sql2)
    cn2017, cn2018, cn2019, cn2020, cn2021 = datadeal(resultlist)
    sql3 = "SELECT Date FROM 媒体聚焦"
    datacollect(sql3)
    mn2017, mn2018, mn2019, mn2020, mn2021 = datadeal(resultlist)
    sql4 = "SELECT Date FROM 时政要闻"
    datacollect(sql4)
    tn2017, tn2018, tn2019, tn2020, tn2021 = datadeal(resultlist)

    c = (
        Bar()
            .add_dataset(
            source=[
                ["年份", "2017", "2018", "2019", "2020", "2021"],
                ["集团新闻", gn2017, gn2018, gn2019, gn2020, gn2021],
                ["企业新闻", en2017, en2018, en2019, en2020, en2021],
                ["国资动态", cn2017, cn2018, cn2019, cn2020, cn2021],
                ["媒体聚焦", mn2017, mn2018, mn2019, mn2020, mn2021],
                ["时政要闻", tn2017, tn2018, tn2019, tn2020, tn2021],
            ]
        )
            .add_yaxis(series_name="2017", y_axis=[])
            .add_yaxis(series_name="2018", y_axis=[])
            .add_yaxis(series_name="2019", y_axis=[])
            .add_yaxis(series_name="2020", y_axis=[])
            .add_yaxis(series_name="2021", y_axis=[])

            .set_global_opts(
            title_opts=opts.TitleOpts(title="保利集团年新闻数量总览"),
            xaxis_opts=opts.AxisOpts(type_="category"),
        )
            .render("polynews_dataset_bar.html")
    )


if __name__ == '__main__':
    dataanalysis()
