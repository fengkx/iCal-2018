# from requests_html import HTML
# coding= utf-8
from bs4 import BeautifulSoup
import re

Week = ('一', '二', '三', '四', '五', '六', '日')


def main():
    code = getHTMLText()
    infoDictList = []
    parser(code, infoDictList)
    print(infoDictList)
    for item in infoDictList:
        print(item)
    print("end")


def getHTMLText():
    with open('/home/fengkx/ical/html.html', 'r', encoding='gb2312') as f:
        doc = f.read()
        return doc


def parser(doc, infoDictList):

    soup = BeautifulSoup(doc, 'html.parser')
    tables = soup.find_all('table')
    tab = tables[0]
    table = []
    for i in range(len(tab.find_all('tr'))):
        tr = tab.find_all('tr')[i]
        for j in range(len(tr.find_all('td'))):
            cell = tr.find_all('td')[j].getText().split()
            if len(cell):
                if len(cell) > 1:
                    table.append(cell)
    # print(table)

    for lesson in table:
        infoDict = {}
        infoDict.update({'课程名称': lesson[0]})
        for i in range(len(lesson)):
            infoDict.update({'课程类型': lesson[1]})
            infoDict.update({'星期': Week.index(lesson[2][1])+1})
            rex = re.compile(r'第.*节')
            count = (rex.findall(lesson[2])[0])
            # print(count[3:5])
            length = len(count)
            if 3 < length < 6:
                infoDict.update({'节数': (int(count[1]), int(count[3]))})
            elif length <= 3:
                infoDict.update({'节数': (int(count[1]),)})
            else:
                infoDict.update({'节数': (int(count[1]), int(count[3:5]))})
            # print(lesson[2])
            infoDict.update({'周次': (abs(eval(lesson[2][-6:-2]))+1)})
            infoDict.update({'授课教师': lesson[3]})
            try:
                infoDict.update({'上课地点': lesson[4]})
            except:
                continue
            infoDictList.append(infoDict)
            # print(infoDictList)


if __name__ == '__main__':
    main()
