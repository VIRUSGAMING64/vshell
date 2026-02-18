import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
from modules.imports import *
############################################################

def debug(e):
    _debug = open("debug-bot.txt","a")
    _debug.write(str(e) + "\n")
    _debug.close()

# Helper function for common queue processing pattern
def process_queue(queue, handler, sleep_time=0.1, handler_args_extractor=None, context_name=""):
    """
    Generic queue handler that processes items from a queue.
    
    Args:
        queue: The queue list to process
        handler: Function to handle each queue item
        sleep_time: Time to sleep when queue is empty
        handler_args_extractor: Function to extract arguments from queue item (if None, uses item directly)
        context_name: Name for error logging context
    """
    while True:
        try:
            if len(queue) <= 0:
                time.sleep(sleep_time)
                continue
            
            item = queue[0]
            if handler_args_extractor:
                args = handler_args_extractor(item)
                handler(*args)
            else:
                handler(item)
        except Exception as e:
            error_msg = str(e)
            if context_name:
                error_msg += f" {context_name}"
            Gvar.LOG.append(error_msg)
        queue.pop(0)

bot = Client(
    "virusgaming",
    api_id=Gvar.API_ID,
    api_hash=Gvar.API_HASH,
    workers=Gvar.WORKERS,
    bot_token=Gvar.TOKEN
)

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

def INLINE_REQUEST_HANDLER(client, message: InlineQuery):
    """Handle inline queries for stats and queues."""
    query = message.query
    text = 'not implementated'
    results = []
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
    def handler_wrapper(item):
        Thread(target=DIRECT_REQUEST_HANDLER, args=[item[CLIENT], item[MESSAGE]], daemon=True).start()
    
    process_queue(
        Gvar.QUEUE_DIRECT, 
        handler_wrapper,
        sleep_time=0.1,
        context_name="DIRECT_MESSAGE_QUEUE_HANDLER"
    )

def INLINE_MESSAGE_QUEUE_HANDLER():
    def handler_wrapper(item):
        INLINE_REQUEST_HANDLER(item[0], item[1])
    
    process_queue(
        Gvar.QUEUE_INLINE,
        handler_wrapper,
        sleep_time=0.5,
        context_name="INLINE_MESSAGE_QUEUE_HANDLER"
    )

def DOWNLOAD_MEDIA_HANDLER(data):
    msg:pyrogram.types.Message = data[0]
    user: t_user = data[1]
    if user.download_id != -1:
        return INVALID
    if msg.media != None:
        try:
            bot.download_media(msg,user.current_dir+"/",progress=Utils.progress,progress_args=tuple([user,bot,"downloading",msg.id]))
            bot.delete_messages(user.chat,user.download_id)
            user.download_id = -1
            msg.reply("Downloaded !!!!",reply_to_message_id=msg.id)
            time.sleep(60)
        except Exception as e:
            if msg.text.startswith("http"):
                return "please wait..."
            debug(e)
            print("in downloads first try")
            msg.reply("Error downloading media")
        finally:
            user.download_id = -1
    
def DOWNLOAD_QUEUE_HANDLER():
    while 1:
        def HANDLER():
            try:
                if len(Gvar.QUEUE_DOWNLOAD) < 1:
                    time.sleep(3)
                    return
                while Gvar.MUTEX: time.sleep(0.001)
                Gvar.MUTEX = True
                data = Gvar.QUEUE_DOWNLOAD[0]
                Gvar.QUEUE_DOWNLOAD.pop(0)
                Gvar.MUTEX = False
                msg = DOWNLOAD_MEDIA_HANDLER(data)
            except Exception as e:
                Gvar.LOG.append(str(e))
                print(e)
            if msg == INVALID:
                Gvar.QUEUE_DOWNLOAD.append(data)
        
        Thread(target=HANDLER).start()
        time.sleep(1)

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

def TORRENT_QUEUE_HANDLER():
    """Placeholder for future torrent download feature."""
    pass

def INIT():
    """Initialize bot and notify admins."""
    try:
        time.sleep(35)
        for admin_id in Gvar.ADMINS:
            bot.send_message(admin_id, "bot online")
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
            time.sleep(40)
            req.get(Gvar.DEBUG_URL)
        except Exception as e:
            Gvar.LOG.append(str(e))
            print(str(e))

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
