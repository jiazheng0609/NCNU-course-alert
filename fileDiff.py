import os
from bs4 import BeautifulSoup as bs
import requests
import time
import subprocess
import csv

from requests.models import Response
from bot import CourseAlertBot
import json

session = requests.Session()
mainURL = "https://ccweb.ncnu.edu.tw/student/"
courses = []

def parseCsv(csvData):
    ans = {}
    courses = csvData.split('"\r\n')[1:-1]

    for course in courses:
        course = course.replace('\n', '.')
        data = course[1:].split('","')
        
        courseObj = {}

        courseObj['year']        = data[0]
        courseObj['number']      = data[1]
        courseObj['class']       = data[2]
        courseObj['name']        = data[3]
        courseObj['department']  = data[4]
        courseObj['graduated']   = data[6]
        courseObj['grade']       = data[7]
        courseObj['teacher']     = data[8]
        courseObj['place']       = data[9]
        courseObj['time']        = data[13]
        courseObj['credit']      = data[14]
        courseObj['limit']       = data[15]
        courseObj['chosen']      = data[16]
        ans[data[1]+data[2]]= courseObj
    return ans

def parseHtml(htmlData):
    ans = {}
    bsObj = bs(htmlData, "lxml")
    trs = bsObj.table.findAll("tr")

    for oneTr in trs[1:]:
        tds = oneTr.findAll("td")
        if len(tds) > 1:
            courseObj = {}

            courseObj['year']        = tds[0].get_text()
            courseObj['number']      = tds[1].get_text()
            courseObj['class']       = tds[2].get_text()
            courseObj['name']        = tds[3].get_text()
            courseObj['department']  = tds[4].get_text()
            courseObj['graduated']   = tds[6].get_text()
            courseObj['grade']       = tds[7].get_text()
            courseObj['teacher']     = tds[8].get_text()
            courseObj['place']       = tds[9].get_text()
            courseObj['time']        = tds[13].get_text()
            courseObj['credit']      = tds[14].get_text()
            courseObj['limit']       = tds[15].get_text()
            courseObj['chosen']      = tds[16].get_text()

            # 若有名額限制，則 remain 存剩餘名額，若沒有限制直接回傳 9999
            courseObj['remain']      = int(courseObj['limit']) - int(courseObj['chosen']) if courseObj['limit'] != "" else 9999
            ans[courseObj['number']+courseObj['class']]= courseObj
    return ans
        
def curlDepartmentCourseTable(year, format):
    '''
        year: 學年度，4 位數字，例如: 1101
        format: 格式選項，例如: 'csv', 'html'
    '''

    # 取得所有課程的 csv 或 html
    response = session.get('https://ccweb.ncnu.edu.tw/student/current_semester_opened_listlist.php?export='+format, verify=False)

    curlTime = time.strftime("%Y%m%d_%H%M%S")
    print("取得所有課程資料：", curlTime)

    if response.status_code != 200:
        raise ConnectionError("{} error".format(response.status_code))
    
    if format == 'csv':
        return parseCsv(response.content.decode('utf-8'))
    elif format == 'html':
        return parseHtml(response.text)


if __name__ == "__main__":

    bot = CourseAlertBot()
    bot.prevAns = curlDepartmentCourseTable("1101", 'html')
    bot.start_polling()

    while True:
        try:
            newAns = curlDepartmentCourseTable("1101", 'html')
        except:
            continue
        
        with open('target.json') as fp:
            target = json.load(fp)

        if  (newAns != bot.prevAns):
            for courseID in newAns:
                curCourse = newAns[courseID]

                # 有時候會抓到以前沒有的課號，造成 KeyError，要在舊資料的課程列表當中插入新增的課
                if courseID not in bot.prevAns:
                    print("課程列表有變動！")
                    bot.prevAns[courseID] = curCourse

                # 發現人數有變化
                if bot.prevAns[courseID]['chosen'] != curCourse['chosen']:
                    gap = int(curCourse['chosen'])-int(bot.prevAns[courseID]['chosen'])
                    print("diff!", curCourse['number'], curCourse['class'], curCourse['name'], curCourse['chosen'], gap)
                    bot.prevAns[courseID]['chosen'] = curCourse['chosen']
                    bot.prevAns[courseID]['remain'] = curCourse['remain']   # 因為人數有變化，因此 remain 必須變更
                    
                    # bot 發送訊息，當人數是增加的時候才運行
                    courseNumber = curCourse['number']
                    if str(courseNumber) in target and gap<0:
                        for chatID in target[courseNumber]:
                            print("send to {}".format(chatID))
                            bot.send(
                                chatID,
                                "{}{} {}班 釋出{}個名額".format(curCourse['number'], curCourse['name'], curCourse['class'], -gap)
                            )

        time.sleep(25)




