import os
from bs4 import BeautifulSoup as bs
import requests
import time
import subprocess
import csv

from requests.models import Response
from bot import CourseAlertBot
import json

YEAR = "1102"

session = requests.Session()
mainURL = "https://ccweb6.ncnu.edu.tw"
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
    # print(htmlData)
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

            # ???????????????????????? remain ????????????????????????????????????????????? 9999
            courseObj['remain']      = int(courseObj['limit']) - int(courseObj['chosen']) if courseObj['limit'] != "" else 9999
            ans[courseObj['number']+courseObj['class']]= courseObj
    return ans
        
def curlDepartmentCourseTable(year, format):
    '''
        year: ????????????4 ??????????????????: 1101
        format: ?????????????????????: 'csv', 'html'
    '''

    global mainURL
    # ????????????????????? csv ??? html
    # print("https://ccweb.ncnu.edu.tw/student/aspmaker_course_opened_detail_viewlist.php?cmd=search&t=aspmaker_course_opened_detail_view&x_year='.format(YEAR)")
    # response = session.get('https://ccweb.ncnu.edu.tw/student/aspmaker_course_opened_detail_viewlist.php?cmd=search&t=aspmaker_course_opened_detail_view&x_year={}'.format(YEAR))
    response = session.get('{mainURL}/student/aspmaker_course_opened_detail_viewlist.php?export={format}'.format(mainURL=mainURL, format=format), verify=False)
    print('{mainURL}/student/aspmaker_course_opened_detail_viewlist.php?export={format}'.format(mainURL=mainURL, format=format))

    curlTime = time.strftime("%Y%m%d_%H%M%S")
    print("???????????????????????????", curlTime)


    if response.status_code != 200:
        raise ConnectionError("{} error".format(response.status_code))
    
    if format == 'csv':
        return parseCsv(response.content.decode('utf-8'))
    elif format == 'html':
        return parseHtml(response.text)


if __name__ == "__main__":

    bot = CourseAlertBot()
    bot.prevAns = curlDepartmentCourseTable(YEAR, 'html')
    bot.start_polling()

    while True:
        try:
            newAns = curlDepartmentCourseTable(YEAR, 'html')
        except:
            continue
        
        with open('target.json') as fp:
            target = json.load(fp)

        if  (newAns != bot.prevAns):
            for courseID in newAns:
                curCourse = newAns[courseID]

                # ???????????????????????????????????????????????? KeyError?????????????????????????????????????????????????????????
                if courseID not in bot.prevAns:
                    print("????????????????????????")
                    bot.prevAns[courseID] = curCourse

                # ?????????????????????
                if bot.prevAns[courseID]['chosen'] != curCourse['chosen']:
                    gap = int(curCourse['chosen'])-int(bot.prevAns[courseID]['chosen'])
                    print("diff!", curCourse['number'], curCourse['class'], curCourse['name'], curCourse['chosen'], gap)
                    bot.prevAns[courseID]['chosen'] = curCourse['chosen']
                    bot.prevAns[courseID]['remain'] = curCourse['remain']   # ?????????????????????????????? remain ????????????
                    
                    # bot ???????????????????????????????????????????????????
                    courseNumber = curCourse['number']
                    if str(courseNumber) in target and gap<0:
                        for chatID in target[courseNumber]:
                            print("send to {}".format(chatID))
                            bot.send(
                                chatID,
                                "{}{} {}??? ??????{}?????????".format(curCourse['number'], curCourse['name'], curCourse['class'], -gap)
                            )

        time.sleep(25)




