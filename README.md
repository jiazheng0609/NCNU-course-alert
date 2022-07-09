# NCNU-course-alert
監測暨大課程的選課人數變化

定期 (目前設定約間隔 30 秒) 從校務系統簡易版抓所有課程資訊下來，且做 parse，若有選課人數變動則印出來。

Telegram Bot 能紀錄誰想訂閱啥課，若使用者追蹤的課程有人退選，會發訊息通知，使用者再趕快去登入校務系統搶課。

## Usage 程式執行方法
1. 把這整個 repo 下載下來放在一個目錄裡
   `git clone https://github.com/jiazheng0609/NCNU-course-alert.git` 或是 GitHub 界面上的 Code -> Download ZIP 下載後解壓縮
2. 安裝虛擬化環境
   `pip install pipenv`
3. 安裝所需套件
   `pipenv install`
4. 去跟 [BotFather](https://t.me/botfather) 申請一個 Telegram Bot，並把 token 複製下來
在 BotFather 裡照著 `/newbot`、`/setname`、`/token` 流程跑完，會得到 token
5. 把設定檔 config.ini.sample 複製一份，重新命名為 config.ini，並在 `TOKEN =` 後貼上從 [BotFather](https://t.me/botfather) 拿到的 token
```
[TG_BOT]
TOKEN = 123456789:XXXXxxxxXXXXxxxxXXXXxxxxXXXXxxxxXXX
```
6. 把所有使用者追蹤列表 target.json.sample 複製一份，重新命名為 target.json
7. `pipenv run python fileDiff.py` 來執行主程式

## Telegram 機器人指令列表
https://t.me/ncnu_course_alert_bot (由 @snsd0805 營運)
-  `/add [課號]`  ，增加「追蹤課號」

-  `/remove [課號]` ，移除「已追蹤課號」

-  `/find [課程關鍵字]` ，使用關鍵字查詢「課號」

-  `/list ` ，查看「已追蹤課號」列表

-  `/help` ，查看幫助
