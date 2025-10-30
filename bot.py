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

# Create the Application with token
application = Application.builder().token(Gvar.TOKEN).build()
bot = application.bot

def DIRECT_REQUEST_HANDLER(bot_instance: Bot, message: Message):
    if message == None:
        return
    temp_user = GetUser(message)
    Gvar.QUEUE_DOWNLOAD.append([message,temp_user])
    data = Utils.USER_PROCCESS(temp_user,message,bot_instance)
    if data == 0:
        if message.reply_to_message:
            DIRECT_REQUEST_HANDLER(bot_instance, message.reply_to_message)
        return
    try:
        message.reply_text(str(data))
    except Exception as e:
        Gvar.LOG.append(str(e))

async def INLINE_REQUEST_HANDLER(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline queries for stats and queues."""
    query = update.inline_query.query
    text = 'not implementated'
    results = []
    
    if not query.startswith("/"):
        results.append(
            InlineQueryResultArticle(
                id="1",
                title="gemini-AI",
                description=text[0:15]+"...",
                input_message_content=InputTextMessageContent(
                    message_text=text
                ),               
            ))
    
    if query.startswith("/stats"):
        results.append(
            InlineQueryResultArticle(
                id="2",
                title="stats",
                description=Utils.stats()[0:20]+"...",
                input_message_content=InputTextMessageContent(
                    message_text=Utils.stats()
                ),               
            )
        )
    
    if query.startswith("/queues"):
        results.append(
            InlineQueryResultArticle(
                id="3",
                title="queues",
                description=Utils.queuesZ()[0:20]+"...",
                input_message_content=InputTextMessageContent(
                    message_text=Utils.queuesZ()
                ),               
            )
        )

    await update.inline_query.answer(
        results=results,
        cache_time=1000
    )

def DIRECT_MESSAGE_QUEUE_HANDLER():
    def handler_wrapper(item):
        Thread(target=DIRECT_REQUEST_HANDLER, args=[item['bot'], item['message']], daemon=True).start()
    
    process_queue(
        Gvar.QUEUE_DIRECT, 
        handler_wrapper,
        sleep_time=0.1,
        context_name="DIRECT_MESSAGE_QUEUE_HANDLER"
    )

def INLINE_MESSAGE_QUEUE_HANDLER():
    def handler_wrapper(item):
        # For PTB inline queries are handled differently - through async handlers
        pass
    
    process_queue(
        Gvar.QUEUE_INLINE,
        handler_wrapper,
        sleep_time=0.5,
        context_name="INLINE_MESSAGE_QUEUE_HANDLER"
    )

def DOWNLOAD_MEDIA_HANDLER(data):
    msg:Message = data[0]
    user: t_user = data[1]
    if user.download_id != -1:
        return INVALID
    
    # PTB handles media differently - check for photo, video, document, etc.
    has_media = msg.photo or msg.video or msg.document or msg.audio or msg.voice
    
    if has_media:
        try:
            # Get the file object based on media type
            file_obj = None
            if msg.photo:
                file_obj = bot.get_file(msg.photo[-1].file_id)
            elif msg.video:
                file_obj = bot.get_file(msg.video.file_id)
            elif msg.document:
                file_obj = bot.get_file(msg.document.file_id)
            elif msg.audio:
                file_obj = bot.get_file(msg.audio.file_id)
            elif msg.voice:
                file_obj = bot.get_file(msg.voice.file_id)
            
            if file_obj:
                # Download to user's directory
                file_obj.download_to_drive(custom_path=user.current_dir+"/")
                bot.delete_message(chat_id=user.chat, message_id=user.download_id)
                user.download_id = -1
                msg.reply_text("Downloaded !!!!", reply_to_message_id=msg.message_id)
                time.sleep(60)
        except Exception as e:
            debug(e)
            print("in downloads first try")
            try:
                msg.reply_text("Error downloading media")
            except:
                pass
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

async def on_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    
    # Check if user is muted (using user_id instead of phone_number as PTB doesn't expose phone)
    if message.from_user.id in Gvar.MUTED_USERS:
        return
    
    if message.text == '/start':
        await message.reply_text("BOT ONLINE")
        return
    
    Gvar.QUEUE_DIRECT.append({'bot': bot, 'message': message})

async def on_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return
    
    # Check if user is muted
    if message.from_user.id in Gvar.MUTED_USERS:
        return
    
    if message.text == '/start':
        await message.reply_text("BOT ONLINE")
        Gvar.DEBUG_GROUP_ID = message.chat.id
        return        

    # Check if bot is mentioned (PTB doesn't have 'mentioned' directly, need to check entities)
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.MENTION:
                await on_private_message(update, context)
                return

async def on_edit_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await on_private_message(update, context)

def TO_SEND_QUEUE_HANDLER(): 
    while 1:
        try:
            if len(Gvar.QUEUE_TO_SEND) <= 0:
                time.sleep(0.1)
                continue
            data = Gvar.QUEUE_TO_SEND[0]
            Gvar.QUEUE_TO_SEND.pop(0)
            for text in data[1]:
                data[0].reply_text(text)
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
            bot.send_message(chat_id=admin_id, text="bot online")
    except Exception as e:
        Gvar.LOG.append(str(e))

def LOG_QUEUE_HANDLER():
    time.sleep(60)
    while 1:
        try:
            if len(Gvar.LOG) != 0:
                bot.send_message(chat_id=Gvar.DEBUG_GROUP_ID, text=Gvar.LOG[0])
                Gvar.LOG.pop(0)
            time.sleep(3)
        except Exception as e:
            print(str(e))     

def ACTIVATOR():
    while 1:
        try:
            time.sleep(40)
            req.get(Gvar.DEBUG_URL)
        except Exception as e:
            Gvar.LOG.append(str(e))
            print(str(e))

# Register handlers
application.add_handler(InlineQueryHandler(INLINE_REQUEST_HANDLER))
application.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, on_private_message))
application.add_handler(MessageHandler(filters.ChatType.GROUPS & filters.TEXT, on_group_message))
application.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.ChatType.PRIVATE, on_edit_private_message))
application.add_handler(CommandHandler("start", on_private_message))

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
print("THREADS STARTED")

# Run the bot with polling
application.run_polling(allowed_updates=Update.ALL_TYPES)
