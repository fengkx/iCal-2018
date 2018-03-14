# from requests_html import HTML
# coding= utf-8
from bs4 import BeautifulSoup
import re
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import tempfile
import os


Week = ('一', '二', '三', '四', '五', '六', '日')  # 映射

Time = [[datetime(2018, 2, 26, 8, 30),  # 上课时间二维列表每一行表示一天
         datetime(2018, 2, 26, 9, 20),
         datetime(2018, 2, 26, 10, 20),
         datetime(2018, 2, 26, 11, 10),
         datetime(2018, 2, 26, 14, 30),
         datetime(2018, 2, 26, 15, 20),
         datetime(2018, 2, 26, 16, 10),
         datetime(2018, 2, 26, 17, 00),
         datetime(2018, 2, 26, 19, 00),
         datetime(2018, 2, 26, 19, 50)
         ], [
    datetime(2018, 2, 27, 8, 30),
    datetime(2018, 2, 27, 9, 20),
    datetime(2018, 2, 27, 10, 20),
    datetime(2018, 2, 27, 11, 10),
    datetime(2018, 2, 27, 14, 30),
    datetime(2018, 2, 27, 15, 20),
    datetime(2018, 2, 27, 16, 10),
    datetime(2018, 2, 27, 17, 00),
    datetime(2018, 2, 27, 19, 00),
    datetime(2018, 2, 27, 19, 50)
], [
    datetime(2018, 2, 28, 8, 30),
    datetime(2018, 2, 28, 9, 20),
    datetime(2018, 2, 28, 10, 20),
    datetime(2018, 2, 28, 11, 10),
    datetime(2018, 2, 28, 14, 30),
    datetime(2018, 2, 28, 15, 20),
    datetime(2018, 2, 28, 16, 10),
    datetime(2018, 2, 28, 17, 00),
    datetime(2018, 2, 28, 19, 00),
    datetime(2018, 2, 28, 19, 50)
], [
    datetime(2018, 3, 1, 8, 30),
    datetime(2018, 3, 1, 9, 20),
    datetime(2018, 3, 1, 10, 20),
    datetime(2018, 3, 1, 11, 10),
    datetime(2018, 3, 1, 14, 30),
    datetime(2018, 3, 1, 15, 20),
    datetime(2018, 3, 1, 16, 10),
    datetime(2018, 3, 1, 17, 00),
    datetime(2018, 3, 1, 19, 00),
    datetime(2018, 3, 1, 19, 50)
], [
    datetime(2018, 3, 2, 8, 30),
    datetime(2018, 3, 2, 9, 20),
    datetime(2018, 3, 2, 10, 20),
    datetime(2018, 3, 2, 11, 10),
    datetime(2018, 3, 2, 14, 30),
    datetime(2018, 3, 2, 15, 20),
    datetime(2018, 3, 2, 16, 10),
    datetime(2018, 3, 2, 17, 00),
    datetime(2018, 3, 2, 19, 00),
    datetime(2018, 3, 2, 19, 50)
]]

TimeEnd = []
for day in Time:  # 生成下课时间二维列表每一行表示一天
    dayEndList = []
    for time in day:
        time = time + timedelta(minutes=40)
        dayEndList.append(time)
    TimeEnd.append(dayEndList)
# print(TimeEnd)


def main():
    currpath = os.path.abspath('.')
    input_path = input("输入html文档目录")
    input_path = os.path.join(currpath, input_path)
    file_path = input('输入 ics 文件输出目录')
    file_path = os.path.join(currpath, file_path)
    code = getHTMLText(input_path)
    infoDictList = []
    parser(code, infoDictList)
    make_cal(infoDictList, file_path)
    print("成功")
    print("你可以在"+file_path+"找到输出的课表.ics")


def getHTMLText(path):
    """功力不足所以手动下载html文档然后直接读，参数一为HTML文档的路径，返回文档内容的字符串"""
    with open(path, 'r', encoding='gb2312') as f:
        doc = f.read()
        return doc


def parser(doc, infoDictList):
    """抓取HTML文档的内容，参数一是文档内容字符串，将内容打包成字典并形成列表，由参数二带回"""
    soup = BeautifulSoup(doc, 'html.parser')
    tables = soup.find_all('table')
    tab = tables[0]
    table = []
    """爬取每一格"""
    for i in range(len(tab.find_all('tr'))):
        tr = tab.find_all('tr')[i]
        for j in range(len(tr.find_all('td'))):
            cell = tr.find_all('td')[j].getText().split()
            if len(cell):
                if len(cell) > 1:  # 如果格子不空，加入table列表
                    table.append(cell)
    lessonList = []
    for lesson in table:  # 将每一格的列表形成一个总的课程列表
        lessonList.append(lesson)
    for lesson in lessonList:  # 分别抓取形成字典
        infoDict = {}
        infoDict.update({'课程名称': lesson[0]})
        infoDict.update({'课程类型': lesson[1]})
        infoDict.update({'星期': Week.index(lesson[2][1])+1})
        rex = re.compile(r'第.*节')
        count = (rex.findall(lesson[2])[0])
        length = len(count)
        if 3 < length < 6:
            infoDict.update({'节数': (int(count[1]), int(count[3]))})
        elif length <= 3:
            infoDict.update({'节数': (int(count[1]),)})
        else:
            infoDict.update({'节数': (int(count[1]), int(count[3:5]))})
        infoDict.update({'周次': (abs(eval(lesson[2][-6:-2]))+1)})
        infoDict.update({'授课教师': lesson[3]})
        try:
            infoDict.update({'上课地点': lesson[4]})
        except:
            infoDict.update({'上课地点': '课表没写'})
        infoDictList.append(infoDict)
        print(infoDict)  # 输出形成的列表


def make_cal(infoDictList, file_path):
    """通过 icalendar 库生成ics"""
    cal = Calendar()
    for i in range(len(infoDictList)):
        for j in infoDictList[i]['节数']:  # 每节课不一样
            for c in range(infoDictList[i]['周次']):  # 每周重复
                event1 = Event()
                event1.add('summary', infoDictList[i]['课程名称'])
                event1.add('location', infoDictList[i]['上课地点'])
                event1.add('description',
                           infoDictList[i]['课程类型']+infoDictList[i]['授课教师'])
                event1.add('dtstart', Time[infoDictList[i]['星期']-1][j-1])
                event1.add('dtend', TimeEnd[infoDictList[i]['星期']-1][j-1])
                event1.add('rule', 'FREQ=WEEKLY')
                event1.add('rule', 'COUNT='+str(infoDictList[i]['周次']))
                cal.add_component(event1)
                Time[infoDictList[i]['星期']-1][j-1] = Time[infoDictList[i]
                                                          ['星期']-1][j-1]+timedelta(days=7)
                TimeEnd[infoDictList[i]['星期']-1][j -
                                                 1] = TimeEnd[infoDictList[i]['星期']-1][j-1]+timedelta(days=7)

    f = open(file_path + '课表.ics', 'wb')
    f.write(cal.to_ical())
    f.close()


if __name__ == '__main__':
    main()
