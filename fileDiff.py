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
            ans[courseObj['number']+courseObj['class']]= courseObj
    return ans
        
def curlDepartmentCourseTable(year, format):
    '''
        year: 學年度，4 位數字，例如: 1101
        format: 格式選項，例如: 'csv', 'html'
    '''

    # 取得所有課程的 csv 或 html
    response = session.get('https://ccweb.ncnu.edu.tw/student/current_semester_opened_listlist.php?export='+format)

    curlTime = time.strftime("%Y%m%d_%H%M%S")
    print("取得所有課程資料：", curlTime)
    
    if format == 'csv':
        return parseCsv(response.content.decode('utf-8'))
    elif format == 'html':
        return parseHtml(response.text)


if __name__ == "__main__":

    bot = CourseAlertBot()
    bot.start_polling()

    prevAns = curlDepartmentCourseTable("1101", 'html')

    # 若檔案不存在要存一份 course.csv，要給 bot 查詢 courseID
    if not os.path.isfile('course.json'):
        with open('course.json', 'w') as fp:
            json.dump(prevAns, fp)
    
    while True:
        newAns = curlDepartmentCourseTable("1101", 'html')
        
        with open('target.json') as fp:
            target = json.load(fp)

        if  (newAns != prevAns):
            for courseID in newAns:
                curCourse = newAns[courseID]
                if prevAns[courseID]['chosen'] != curCourse['chosen']:
                    gap = int(curCourse['chosen'])-int(prevAns[courseID]['chosen'])
                    print("diff!", curCourse['number'], curCourse['class'], curCourse['name'], curCourse['chosen'], gap)
                    prevAns[courseID]['chosen'] = curCourse['chosen']

                    # bot 發送訊息
                    courseNumber = curCourse['number']
                    if str(courseNumber) in target and gap<0:
                        for chatID in target[courseNumber]:
                            print("send to {}".format(chatID))
                            bot.send(
                                chatID,
                                "{}{} {}班 釋出{}個名額".format(curCourse['number'], curCourse['name'], curCourse['class'], -gap)
                            )

        time.sleep(0.5)




