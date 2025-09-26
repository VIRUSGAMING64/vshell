import os
import pyrogram
from tarfile import TarFile
import modules.Gvar as Gvar
from modules.datatypes import *
from pyrogram.emoji import *

USERS = {}

def sizeof(dir:str):
    try:
        if os.path.isfile(dir):
            return os.path.getsize(dir)
        sx = 0
        for pth in os.listdir(dir):
            sz=sizeof(dir+"/"+pth)
            if str(sz).isnumeric() == False:
                continue
            sx += sz
    except Exception as e:
        Gvar.LOG.append(str(e))
        print(e)
    return sx

class t_user:
    def fron_json(self,json:dict):
        self.id = json["id"]
        self.dc_id = json["dc_id"]
        self.first_name = json["first_name"]
        self.last_name = json["last_name"]
        self.lang_code = json["lang_code"]
        self.username = json["username"]
        self.is_premium = json["is_premium"]
        self.base_dir = json["base_dir"]
        self.current_dir = json["current_dir"]
        self.bytes_transmited = json["bytes_transmited"]
        self.chat = json["chat"]
        self.last_edit_time = 0
        self.download_id = -1

    def __init__(self,message:pyrogram.types.Message|dict) -> None:
        try:
            self.download_chat = None
            self.id = message.from_user.id
            self.dc_id = message.from_user.dc_id
            self.first_name = message.from_user.first_name
            self.last_name = message.from_user.last_name
            self.lang_code = message.from_user.language_code
            self.username = message.from_user.username
            self.is_premium = message.from_user.is_premium
            self.base_dir = Gvar.ROOT + f"/{self.id}-{self.first_name}"
            self.current_dir = self.base_dir
            self.chat = message.chat.id
            self.bytes_transmited = 0
            self.download_id = -1
            self.last_edit_time = 0
        except:
            self.fron_json(message)
        try:
            os.mkdir(self.base_dir)
        except:
            pass
    def getcwd(self):
        return self.current_dir
    
    def chdir(self,dir):
        dir = "."+self.GetDir(dir)
        if dir == "...":
            return self.back_dir()
        if dir.startswith("."):
            if os.path.isdir(self.current_dir +"/"+ dir.removeprefix(".")):
                self.current_dir = self.current_dir +"/"+ dir.removeprefix(".")
            else:
                return 0
        else:
            if len(dir) < self.base_dir:
                return 0
            elif os.path.isdir(dir):
                self.current_dir = dir
            else:
                return 0
        return 1
    
    def size(self,dir):
        dir = self.GetDir(dir)
        if dir == INVALID:
            return "Not Found"
        return sizeof(dir)
    
    def GetDir(self,k:str):
        if k.isnumeric():
            try:
                data = os.listdir(self.current_dir)
                data.sort()
                return data[int(k)-1]
            except:
                return INVALID
        else:
            return k

    def __str__(self):
        dic = {
            "id":self.id,
            "dc_id":self.dc_id,
            'first_name':self.first_name,
            "last_name":self.last_name,
            "lang_code":self.lang_code,
            "username":self.username,
            "is_premiun":self.is_premium,
            "base_dir":self.base_dir,
            "bytes_transmited":self.bytes_transmited,
            "chat":self.chat
        }
        return str(dic).replace("'",'"').replace("True","true").replace("False","false")

    def ls(self):
        dirs = os.listdir(self.current_dir)
        dirs.sort()
        sstr = f"|{self.current_dir}|\n"
        j = 1
        for i in dirs:
            obj = self.current_dir+"/"+str(i)
            if os.path.isdir(obj):
                sstr += f"{j} {FILE_FOLDER} " + i + "\n"
            elif os.path.isfile(obj):
                sstr += f"{j} {PAGE_FACING_UP} " + i + "\n"
            elif os.path.islink(obj):
                sstr += f"{j} {LINK} " + i + "\n"
            else:
                sstr += f"[{j}][other] " + i + "\n"
            j+=1
        return sstr

    def mkdir(self,newdir):
        try:
            newdir = self.GetDir(newdir)
            os.mkdir(self.current_dir+"/"+newdir)
        except Exception as e:
            Gvar.LOG.append(str(e))
            return str(e)
        return "changed\n"+str(self.ls())

    def back_dir(self):
        self.current_dir = os.path.dirname(self.current_dir)
        if len(self.current_dir) < len(self.base_dir):
            self.current_dir = self.base_dir
        return self.current_dir

def GetUser(message:pyrogram.types.Message):
    id = message.chat.id
    try:
        return USERS[id]
    except:
        USERS[id] = t_user(message)
        return USERS[id]

def save_users():
    tar = TarFile("users.7z","w")
    for name in USERS.keys():
        file = open(str(name)+".json","w")
        file.write(str(USERS[name]))
        file.close()
        tar.add(str(name)+".json")
        os.remove(str(name)+".json")
    tar.close()