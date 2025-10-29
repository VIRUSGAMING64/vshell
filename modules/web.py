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
    
    # Helper function to get MIME type based on file extension
    def get_mime_type(filename):
        mime_types = {
            '.css': 'text/css',
            '.svg': 'image/svg+xml',
            '.js': 'application/javascript',
            '.ts': 'application/javascript'
        }
        for ext, mime in mime_types.items():
            if filename.endswith(ext):
                return mime
        return None
    
    # Helper function to clean path prefix
    def clean_path_prefix(path, prefix="ftp"):
        path = str(path)
        if path.startswith(prefix):
            path = path.removeprefix(prefix)
        while path.startswith("/"):
            path = path.removeprefix("/")
        return path
    
    # Helper function to build href for file/folder listing
    def build_href(prefix, base_dir, item_name):
        if base_dir == "":
            return f"{prefix}/{item_name}"
        return f"{prefix}/{base_dir}/{item_name}"

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
        # Check if request is for a static file
        mime_type = get_mime_type(dir)
        if mime_type:
            dir = clean_path_prefix(dir)
            return Response(route(Gvar.FILEROOT+'/web/'+dir), mimetype=mime_type)
        
        pat = "[]//|&&&|"
        dirs = os.listdir(Gvar.FILEROOT +'/'+ dir)
        for i in range(len(dirs)):
            if os.path.isdir(Gvar.FILEROOT+"/"+dir+f"/{dirs[i]}"):
                href = build_href("ftp", dir, dirs[i])
                dirs[i] = [str(dirs[i]),"folder",href]
            else:
                href = build_href("file", dir, dirs[i])
                dirs[i] = [str(dirs[i]),"file",href]

        webpage = open(Gvar.FILEROOT+"/templates/ftp.html","r").read(2**30)
        webpage = webpage.replace(pat,str(dirs))
        return webpage
    
    @web.route("/<path:sub_path>")
    def public(sub_path):   
        sub_path = str(sub_path)
        # Check if request is for a static file with specific MIME type
        mime_type = get_mime_type(sub_path)
        if mime_type:
            return Response(route(Gvar.FILEROOT+'/web/'+sub_path), mimetype=mime_type)
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
            web.run("0.0.0.0",80)
            break
        except Exception as e:
            print(f"port {port} allready used or permission denied (run as sudo): ", str(e))
#############################################################
## FLASK ##
###########
