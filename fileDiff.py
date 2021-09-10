import os
from bs4 import BeautifulSoup as bs
import requests
import time
import subprocess
import csv
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
        
def curlDepartmentCourseTable(year):
    '''
        先取得各科系的開課表格連結
        再將連結丟給 extractDepartmentCourseTable() 取得課程資訊
    '''

    # 取得 所有課程的 csv
    response = session.get('https://ccweb.ncnu.edu.tw/student/current_semester_opened_listlist.php?export=csv')

    curlTime = time.strftime("%Y%m%d_%H%M%S")
    print("取得所有課程資料：", curlTime)
    
    return parseCsv(response.content.decode('utf-8'))


if __name__ == "__main__":

    bot = CourseAlertBot()
    bot.start_polling()

    prevAns = curlDepartmentCourseTable("1101")

    # 若檔案不存在要存一份 course.csv，要給 bot 查詢 courseID
    if not os.path.isfile('course.json'):
        with open('course.json', 'w') as fp:
            json.dump(prevAns, fp)
    
    while True:
        newAns = curlDepartmentCourseTable("1101")
        
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




