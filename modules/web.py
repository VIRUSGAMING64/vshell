import time
import modules.Gvar as Gvar
from modules.users import USERS
import os
import random
import modules.Utils as Utils
from json import *
from flask import *

def WEB(bot):
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

    @web.route("/api/routes")
    def api_routes():
        try:
            routes = []
            for rule in web.url_map.iter_rules():
                if rule.endpoint == 'static':
                    continue
                methods = sorted([m for m in rule.methods if m in ['GET','POST','PUT','DELETE','PATCH','OPTIONS']])
                routes.append({
                    "endpoint": rule.endpoint,
                    "methods": methods,
                    "path": str(rule)
                })
            return jsonify(routes)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
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
    for i in range(10000):
        port = random.randint(0,65535)
        try:
            web.run("0.0.0.0",port)
            break
        except Exception as e:
            print(f"port {port} allready used or permission denied (run as sudo): ", str(e))
#############################################################
## FLASK ##
###########