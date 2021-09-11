from telegram.ext import Updater, CommandHandler
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')
updater = Updater(token=config['TG_BOT']['TOKEN'], use_context=True)
dispacher = updater.dispatcher

class CourseAlertBot():
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

        self.updater = Updater(token=config['TG_BOT']['TOKEN'], use_context=True)
        self.dispacher = self.updater.dispatcher
        self.dispacher.add_handler(CommandHandler('start',   self.start))
        self.dispacher.add_handler(CommandHandler('help',    self.start))
        self.dispacher.add_handler(CommandHandler('add',     self.add))
        self.dispacher.add_handler(CommandHandler('remove',  self.remove))
        self.dispacher.add_handler(CommandHandler('list',    self.ls))
        self.dispacher.add_handler(CommandHandler('find',    self.find))

        self.prevAns = None # 紀錄當前的課程狀況，為了給 add 確認剩餘人數
    
    def start_polling(self):
        self.updater.start_polling()
        print("start...")
    
    def send(self, chatID, text):
        self.updater.bot.send_message(chatID, text)

    def start(self, update, context):
        '''
            說明書, for '/start' & '/help'
        '''
        user = update.effective_chat
        context.bot.send_message(
            chat_id=user.id,
            text=
                "Hi, {} {}".format(user.first_name, user.last_name)+
                "\n\n   /add [課號]" +
                "\n         - 增加「追蹤課號」" +
                "\n\n   /remove [課號]" +
                "\n         - 移除「已追蹤課號」" +
                "\n\n   /find [課程關鍵字]" +
                "\n         - 使用關鍵字查詢「課號」" +
                "\n\n   /list" +
                "\n         - 查看「已追蹤課號」列表"
                "\n\n   /help" +
                "\n         - 查看「幫助」"
        )

    def add(self, update, context):
        '''
            增加使用者的「追蹤」, for '/add'
        '''

        def checkRemain(courseID):
            '''
                確認是否當下就可以進行選課，若可以則 return false 代表不需要追蹤
            '''
            # 確認所有該課號的班別是否有名額
            remainNumber = 0
            for course in self.prevAns:
                if courseID in course:
                    remainNumber += int(self.prevAns[course]['remain'])
            
            if remainNumber>0:
                context.bot.send_message(chat_id=user.id,
                    text="你要增加的課程存在沒有名額限制的班別，如果需要取消追蹤請使用 /remove {}".format(courseID) if remainNumber >= 999
                    else "你要增加的課程現在有{}個名額，如果需要取消追蹤請使用 /remove {}".format(remainNumber, courseID)
                )
                return False
            else:
                return True
        
        user = update.effective_chat

        # 參數量錯誤
        if len(context.args) != 1:
            context.bot.send_message(chat_id=user.id, text="使用方式: /add [欲追蹤課號]")
            return
        
        # 讀紀錄檔
        with open('target.json') as fp:
            target = json.load(fp)
        
        # 判斷要添加的課號存在了沒，沒有的話要加一個 key(課號)
        courseID = context.args[0]
        if courseID in target:
            # 判斷是否已經添加
            if user.id in target[courseID]:
                context.bot.send_message(chat_id=user.id, text="{} 已經在你的追蹤清單".format(courseID))
            else:
                target[courseID].append(user.id)
                context.bot.send_message(chat_id=user.id, text="已經新增{}".format(courseID))
                checkRemain(courseID)   # 若還有班別可以選擇，就提醒 user
        else:
            target[context.args[0]] = [user.id]
            context.bot.send_message(chat_id=user.id, text="已經新增{}".format(courseID))
            checkRemain(courseID)       # 若還有班別可以選擇，就提醒 user
        
        with open('target.json', 'w') as fp:
            json.dump(target, fp)

    def remove(self, update, context):
        '''
            增加使用者的「追蹤」, for '/add'
        '''
        user = update.effective_chat

        # 參數量錯誤
        if len(context.args) != 1:
            context.bot.send_message(chat_id=user.id, text="使用方式: /remove [欲追蹤課號]")
            return
        
        # 讀紀錄檔
        with open('target.json') as fp:
            target = json.load(fp)
        
        # 判斷要添加的課號存在了沒
        courseID = context.args[0]
        if courseID in target:
            # 判斷是否已經添加
            if user.id in target[courseID]:
                target[courseID].remove(user.id)
                context.bot.send_message(chat_id=user.id, text="{}已經移除".format(courseID))

                # 清除不需要的 key
                if len(target[courseID]) == 0:
                    del target[courseID]
            else:
                context.bot.send_message(chat_id=user.id, text="{}沒有在你的清單中".format(courseID))
        else:
            context.bot.send_message(chat_id=user.id, text="{}沒有在你的清單中".format(courseID))
        
        with open('target.json', 'w') as fp:
            json.dump(target, fp)

    def ls(self, update, context):
        user = update.effective_chat

        with open('target.json') as fp:
            target = json.load(fp)
        
        ans = []
        for courseID in target:
            if user.id in target[courseID]:
                ans.append(courseID)
        
        context.bot.send_message(chat_id=user.id, text="你的清單：{}".format(ans))

    def find(self, update, context):
        '''
            利用關鍵字查詢課號

        '''
        user = update.effective_chat

        # 參數量錯誤
        if len(context.args) != 1:
            context.bot.send_message(chat_id=user.id, text="使用方式: /find [課程關鍵字]")
            return
        
        with open('course.json') as fp:
            courseData = json.load(fp)
        
        ans = set()
        for courseID in courseData:
            courseName = courseData[courseID]['name']
            courseNumber = courseData[courseID]['number']
            department = courseData[courseID]['department']

            if context.args[0] in courseName:
                ans.add("{} {} - {}\n".format(courseNumber, courseName, department))
        
        # 字串處理
        output = ""
        for course in ans:
            output += "{}\n\n".format(course)
        
        if output == "":
            context.bot.send_message(chat_id=user.id, text="查無相關課程")
        else:
            context.bot.send_message(chat_id=user.id, text="查詢結果:\n\n{}".format(output))
