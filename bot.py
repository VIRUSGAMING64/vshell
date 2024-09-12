from modules.imports import *
############################################################
def WEB():
    web = Flask("vshell")

    @web.route("/debug",methods = ['POST', 'GET'])    
    def web_debug():
        try:
            if request.method == "POST":
                Gvar.POST_QUERYS+=1
            else:
                Gvar.GET_QUERYS+=1
                if __name__ != "__main__":        
                    while bot.is_connected == None:
                        time.sleep(1)
                    bot.send_message(Gvar.DEBUG_GROUP_ID,f"GET: {Gvar.GET_QUERYS} POST: {Gvar.POST_QUERYS}\n"+Utils.stats())
                    
            return open(Gvar.FILEROOT+"/web/index.html","rb").read(2**31)        
        except Exception as e:
            for i in Gvar.ADMINS:
                bot.send_message(i,str(e))
        return "nothing"
    
    @web.route("/api/users")
    def api_users():
        enc = JSONEncoder()        
        dic = {}
        for i in USERS.keys():
            dic[i] = str(USERS[i])
        return Response(enc.encode(dic),mimetype="application/json")
    
    @web.route("/api/logs")
    def bot_logs():
        enco = JSONEncoder()
        return Response(enco.encode(Gvar.LOG),mimetype="application/json")
    
    @web.route("/api/stats")
    def bot_stats():
        stats = Utils.stats().split("\n")
        stats.pop()
        for i in range(len(stats)):
            stats[i] = stats[i].split(":")
            try:    
                while stats[i][1][0] == " ":
                    stats[i][1] = stats[i][1].removeprefix(" ")
            except Exception as e:
                print(e)
        enc = JSONEncoder()
        stats = enc.encode(stats)       
        return Response(stats,mimetype="application/json")
    
    @web.route("/api/queues")
    def QUEUES_SIZES():
        queues = Utils.queuesZ()
        queues = queues.split("\n")
        for i in range(len(queues)):
            queues[i] = queues[i].split(":")
        di = {
            "downloads":queues[0],
            "download_links":queues[1],
            "messages":queues[2],
            "to_send":queues[3]
        }
        return Response(di,mimetype="application/json")
    
    @web.route("/api/commands")
    def api_command():
        enc = JSONEncoder()
        BOT_COMMANDS = Gvar.BOT_COMMANDS.copy()
        BOT_COMMANDS.pop(0)        
        return Response(enc.encode(BOT_COMMANDS),mimetype="application/json")
    
    @web.route("/")
    def main():
        return route(Gvar.FILEROOT+"/web/index.html")
    
    @web.route("/file/<path:filename>")
    def Gfile(filename):
        return send_file(filename)
    
    @web.route("/ftp/<path:dir>")
    def ftp(dir):
        dir = str(dir)
        if(dir.endswith('.css')):
            if dir.startswith("ftp"):
                dir.removeprefix("ftp")
        if(dir.endswith('.css')):
            while dir.startswith("/"):
                dir = dir.removeprefix("/")
            return Response(route(Gvar.FILEROOT+'/web/'+dir), mimetype='text/css')
        
        if(dir.endswith('.svg')):
            if dir.startswith("ftp"):
                dir.removeprefix("ftp")
        if(dir.endswith('.svg')):
            while dir.startswith("/"):
                dir = dir.removeprefix("/")
            return Response(route(Gvar.FILEROOT+'/web/'+dir), mimetype='image/svg+xml')
        
        pat = "[]//|&&&|"
        dirs = os.listdir(Gvar.FILEROOT +'/'+ dir)
        for i in range(len(dirs)):
            if os.path.isdir(Gvar.FILEROOT+"/"+dir+f"/{dirs[i]}"):    
                href = str("ftp/"+dir+"/"+str(dirs[i]))
                if dir == "":
                    href = "ftp/"+str(dirs[i])
                dirs[i] = [str(dirs[i]),"folder",href]
            else:    
                href = str("file/"+dir+"/"+str(dirs[i]))
                if dir == "":
                    href = "file/"+str(dirs[i])
                dirs[i] = [str(dirs[i]),"file",href]

        webpage = open(Gvar.FILEROOT+"/templates/ftp.html","r").read(2**30)
        webpage = webpage.replace(pat,str(dirs))
        return webpage
    
    @web.route("/<path:sub_path>")
    def public(sub_path):   
        sub_path = str(sub_path)
        if (sub_path.endswith('.svg')):
            return Response(route(Gvar.FILEROOT+'/web/'+sub_path), mimetype='image/svg+xml')
        if(sub_path.endswith('.css')):
            return Response(route(Gvar.FILEROOT+'/web/'+sub_path), mimetype='text/css')
        if(sub_path.endswith('.js') or sub_path.endswith('.ts')):
            return Response(route(Gvar.FILEROOT+'/web/'+sub_path), mimetype='application/javascript')
        if(sub_path.startswith("ftp")):
            return ftp("")
        return route(Gvar.FILEROOT+'/web/'+sub_path)  
    
    def route(url):
        try:
            file = open(url,'rb')
            line = file.read(65535)
            text = b""
            while line:
                text = text + line
                line = file.read(65535)
            return text
        except Exception as e:
            return str(e)

    web.run("0.0.0.0",80)

#############################################################
## FLASK ##
###########

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

def DIRECT_REQUEST_HANDLER(client: Client, message: Message):
    temp_user = GetUser(message)
    Gvar.QUEUE_DOWNLOAD.append([message,temp_user])
    data = Utils.USER_PROCCESS(temp_user,message,bot)
    try:
        message.reply(data)
    except Exception as e:
        Gvar.LOG.append(str(e))

def INLINE_REQUEST_HANDLER(client, message: InlineQuery):  # this is hard    
    query = message.query
    id=message.from_user.id
    gemini = GetAI(id)
    text = gemini.query(query)
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

    message.answer(
        results=results,
        cache_time=1000
    )

def DIRECT_MESSAGE_QUEUE_HANDLER():
    while True:
        try:
            if len(Gvar.QUEUE_DIRECT) <= 0:
                time.sleep(0.01)
                continue
            DIRECT_REQUEST_HANDLER(Gvar.QUEUE_DIRECT[0][0], Gvar.QUEUE_DIRECT[0][1])
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
                bot.download_media(msg,user.current_dir+"/",progress=Utils.progress,progress_args=[user,bot,"downloading"])
                bot.delete_messages(user.chat,user.download_id)
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
            bot.send_message(i,"bot online")
    except Exception as e:
        Gvar.LOG.append(str(e))

def LOG_QUEUE_HANDLER():
    time.sleep(60)
    while 1:
        try:
            if len(Gvar.LOG) != 0:
                bot.send_message(Gvar.DEBUG_GROUP_ID,Gvar.LOG[0])
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
    ]
)

pool.start_all(1)
print("THREADS STARTEDS")

try:
    bot.run()
except Exception as e:
    print(str(e))

time.sleep(1200)