from telegram.ext import Updater, CommandHandler
import configparser
import json

config = configparser.ConfigParser()
config.read('config.ini')
updater = Updater(token=config['TG_BOT']['TOKEN'], use_context=True)
dispacher = updater.dispatcher

def start(update, context):
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
            "\n\n   /list" +
            "\n         - 查看「已追蹤課號」列表"
            "\n\n   /help" +
            "\n         - 查看「幫助」"
    )

def add(update, context):
    '''
        增加使用者的「追蹤」, for '/add'
    '''
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
    else:
        target[context.args[0]] = [user.id]
        context.bot.send_message(chat_id=user.id, text="已經新增{}".format(courseID))
    
    with open('target.json', 'w') as fp:
        json.dump(target, fp)

def remove(update, context):
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

def ls(update, context):
    user = update.effective_chat

    with open('target.json') as fp:
        target = json.load(fp)
    
    ans = []
    for courseID in target:
        if user.id in target[courseID]:
            ans.append(courseID)
    
    context.bot.send_message(chat_id=user.id, text="你的清單：{}".format(ans))

dispacher.add_handler(CommandHandler('start', start))
dispacher.add_handler(CommandHandler('help', start))
dispacher.add_handler(CommandHandler('add', add))
dispacher.add_handler(CommandHandler('remove', remove))
dispacher.add_handler(CommandHandler('list', ls))

updater.start_polling()
updater.idle()