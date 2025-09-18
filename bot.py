from modules.imports import *
############################################################


def debug(e):
    _debug = open("debug-bot.txt","a")
    _debug.write(str(e) + "\n")
    _debug.close()

bot = Client(
    "virusgaming",
    api_id=Gvar.API_ID,
    api_hash=Gvar.API_HASH,
    workers=Gvar.WORKERS,
    bot_token=Gvar.TOKEN
)
"""
if you need use as bot token remove phone_code and phone_number 
and add line bot_token
"""


def DIRECT_REQUEST_HANDLER(client: Client, message: Message):
    if message == None:
        return
    temp_user = GetUser(message)
    Gvar.QUEUE_DOWNLOAD.append([message,temp_user])
    data = Utils.USER_PROCCESS(temp_user,message,bot)
    if data == 0:
        DIRECT_REQUEST_HANDLER(client,message.reply_to_message)
        return
    try:
        mes = message.reply(str(data))
    except Exception as e:
        Gvar.LOG.append(str(e))

def INLINE_REQUEST_HANDLER(client, message: InlineQuery):  # this is hard    
    query = message.query
    id=message.from_user.id
    text = 'not implementated'
    results=[]
    if message.query.startswith("/") == False:
        results.append(
        InlineQueryResultArticle(
            title="gemini-AI",
            description=text[0:15]+"...",
            input_message_content=InputTextMessageContent(
                message_text=text
            ),               
        ))
    if message.query.startswith("/stats"):
        results.append(
        InlineQueryResultArticle(
                title="stats",
                description=Utils.stats()[0:20]+"...",
                input_message_content=InputTextMessageContent(
                    message_text=Utils.stats()
                ),               
            )
        )
    
    if message.query.startswith("/queues"):
        results.append(
        InlineQueryResultArticle(
                title="queues",
                description=Utils.queuesZ()[0:20]+"...",
                input_message_content=InputTextMessageContent(
                    message_text=Utils.queuesZ()
                ),               
            )
        )

    asw = message.answer(
        results=results,
        cache_time=1000
    )

def DIRECT_MESSAGE_QUEUE_HANDLER():
    while True:
        try:
            if len(Gvar.QUEUE_DIRECT) <= 0:
                time.sleep(0.1)
                continue
            Thread(target=DIRECT_REQUEST_HANDLER,args =[Gvar.QUEUE_DIRECT[0][0], Gvar.QUEUE_DIRECT[0][1]],daemon=True).start()
        except Exception as e:
            Gvar.LOG.append(str(e) + " DIRECT_MESSAGE_QUEUE_HANDLER")
        Gvar.QUEUE_DIRECT.pop(0)

def INLINE_MESSAGE_QUEUE_HANDLER():
    while True:
        try:
            if len(Gvar.QUEUE_INLINE) == 0:
                time.sleep(0.5)
                continue
            INLINE_REQUEST_HANDLER(Gvar.QUEUE_INLINE[0][0], Gvar.QUEUE_INLINE[0][1])
        except Exception  as e:
            Gvar.LOG.append(str(e))
        Gvar.QUEUE_INLINE.pop(0)

def DOWNLOAD_HANDLER(data):
    msg:pyrogram.types.Message = data[0]
    user: t_user = data[1]
    if Gvar.DOWNLOADING == 0:
        if msg.media != None:
            try:
                Gvar.DOWNLOADING = 1
                med=bot.download_media(msg,user.current_dir+"/",progress=Utils.progress,progress_args=tuple([user,bot,"downloading"]))
                med2=bot.delete_messages(user.chat,user.download_id)
                msg.reply("Downloaded !!!!",reply_to_message_id=msg.id)
                time.sleep(60)
            except Exception as e:
                debug(e)
                print("in downloads first try")
                msg.reply("Error downloading media")
            finally:
                Gvar.DOWNLOADING = 0
                user.download_id = -1
                return 1
    return 0
    
def DOWNLOAD_QUEUE_HANDLER():
    while 1:
        def HANDLER():
            try:
                if len(Gvar.QUEUE_DOWNLOAD) < 1:
                    time.sleep(1)
                    return
                res = DOWNLOAD_HANDLER(Gvar.QUEUE_DOWNLOAD[0])
            except Exception as e:
                Gvar.LOG.append(str(e))
                print(e)
            Gvar.QUEUE_DOWNLOAD.pop(0)
        HANDLER()

@bot.on_inline_query()
async def on_inline_query(client: Client, message: Message):
    Gvar.QUEUE_INLINE.append([client, message])

@bot.on_message(filters.private)
async def on_private_message(client: Client, message: Message):
    if message.from_user.phone_number in Gvar.MUTED_USERS:
        return
    if message.text == '/start':
        await message.reply("BOT ONLINE")
        return
    Gvar.QUEUE_DIRECT.append([client, message])

@bot.on_message(filters.group)
async def on_group_message(client: Client, message: Message):
    if message.from_user.phone_number in Gvar.MUTED_USERS:
        return
    if message.text == '/start':
        await message.reply("BOT ONLINE")
        Gvar.DEBUG_GROUP_ID = message.chat.id
        return
    if message.mentioned:
        await on_private_message(client,message)

@bot.on_edited_message(filters.private)
async def on_edit_private_message(client, message:Message):
    await on_private_message(client, message)

def TO_SEND_QUEUE_HANDLER(): 
    while 1:
        try:
            if len(Gvar.QUEUE_TO_SEND) <= 0:
                time.sleep(0.1)
                continue
            data = Gvar.QUEUE_TO_SEND[0]
            Gvar.QUEUE_TO_SEND.pop(0)
            for text in data[1]:
                data[0].reply(text)
                time.sleep(1.5)
        except Exception as e:
            Gvar.LOG.append(str(e))

def TORRENT_QUEUE_HANDLER(): #TODO
    try:
        pass
    except Exception as e:
        Gvar.LOG.append(str(e))
        debug(e)

def INIT():
    try:
        time.sleep(35)
        for i in Gvar.ADMINS:
            mes=bot.send_message(i,"bot online")
    except Exception as e:
        Gvar.LOG.append(str(e))

def LOG_QUEUE_HANDLER():
    time.sleep(60)
    while 1:
        try:
            if len(Gvar.LOG) != 0:
                mes=bot.send_message(Gvar.DEBUG_GROUP_ID,Gvar.LOG[0])
                Gvar.LOG.pop(0)
            time.sleep(3)
        except Exception as e:
            print(str(e))     
            #Gvar.LOG.append(str(e))

def ACTIVATOR():
    while 1:
        try:
            time.sleep(60)
            req.get(Gvar.DEBUG_URL)
        except Exception as e:
            Gvar.LOG.append(str(e))
            print(str(e))

def TERMINAL():
    while(True):
        try:
            data = input()
            if data == "EOF":
                break
            exec(data)
        except Exception as e:
            Gvar.LOG.append(e)
            print(e)

pool = v_pool(
    [
        ACTIVATOR,
        WEB,
        INIT,
        DIRECT_MESSAGE_QUEUE_HANDLER,
        INLINE_MESSAGE_QUEUE_HANDLER,
        DOWNLOAD_QUEUE_HANDLER,
        TO_SEND_QUEUE_HANDLER,
        TORRENT_QUEUE_HANDLER,
        LOG_QUEUE_HANDLER
    ],[[],[bot]]
)

pool.start_all(1)
print("THREADS STARTEDS")
bot.run()
