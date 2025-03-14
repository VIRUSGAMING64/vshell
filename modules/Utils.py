import urllib.request as uq
import sys
import os
import xmrig
from modules.VidDown import *
from modules.users import *
import subprocess as sbp
from math import *
import pyrogram.utils
import yt_dlp
from modules.pool import *
from pyrogram.emoji import *
from pyrogram.types import *
import threading as th
import psutil as st
import time
import requests as rq
from modules.datatypes import *
import modules.Gvar as Gvar
from pyrogram.client import *
import tarfile as tar

def prog(cant,total,prec=2,UD = "uploading"):
    per = int((cant/total)*10)
    per2 = round((cant/total)*100)
    res = 10-per
    s = f"{per2}%\n"
    s += f"{round(cant/(1024**2),prec)}MB of {round(total/(1024**2),prec)}MB\n"
    if per2 <= 33.333:
        s += f"{pyrogram.emoji.RED_CIRCLE}"*per
    elif per2 <= 80.0:
        s += f"{pyrogram.emoji.ORANGE_CIRCLE}"*per
    else:
        s += f"{pyrogram.emoji.GREEN_CIRCLE}"*per
    s += f"{pyrogram.emoji.WHITE_CIRCLE}"*res
    s += f"\n{UD}"
    s += "\n"+uptime()
    return s

def get_speed(cant:int,user:t_user):
    L = user.last_edit_time
    R = time.time_ns()
    time_elapsed = (R-L+1)
    user.last_edit_time = R
    mb_in_time = (cant - user.bytes_transmited) / (1024**2)
    user.bytes_transmited = cant
    return round(mb_in_time / time_elapsed)

def progress(cant, total,user:t_user,bot:pyrogram.client.Client,UD = "uploading"):
    if (time.time_ns()//10**8)%5 == 0:
        UD += f"\n{get_speed(cant,user)}MB/S"
        cant = prog(cant,total,UD=UD)
        if user.download_id == -1:
            user.download_id = bot.send_message(user.chat,cant).id
        else:
            user.download_id = bot.edit_message_text(user.chat,user.download_id,cant).id

def GenerateDirectLink(message:Message):
    try:
        text = message.text.split(" ")[1]
        uid = message.from_user.id
        name = message.from_user.first_name
    except:
        return "try to use: /link filePath\examples:\n /link hola/new.zip\n /link hola.txt"
    return f"vshell.onrender.com/file/env/{uid}-{name}/{text}"

def round(fl:float,prec:int=2):
    if prec > 1e2:
        raise prec > 1e2
    r=str(fl)
    e = ''
    if "." in r:
        r=r.split('.')
        r[0] += "."    
        if 'e' in r[1]:
            temp = str(cp(r[1]))
            temp = temp.split('e')
            e = 'e'+temp[len(temp)-1]
        for i in range(prec):
            if i >= len(r[1]):
                r[0] += '0'
            else:
                r[0]+=r[1][i]
    else:
        r = [r]
    return float(r[0]+e)

def __geturl(url,filename,user:t_user):
    ret = "Downloaded..."
    try:
        Dn = uq.urlopen(url)
        D = Dn.read(1024 * 1024)
        file = open(filename,"wb")
        while D:
            file.write(D)
            D = Dn.read(1024 * 1024)
    except Exception as e:
        Gvar.LOG.append(str(e) +" "+ str(user.id))
        ret = "Error: " + str(e) 
    finally:
        file.close()
        return ret

def GetParent(url):
    url = list(url)
    parent = ""
    if "/" in url:
        while url[len(url)-1] != "/":
            parent = url[len(url)-1]+parent
            url.pop()
        return parent 
    else:
        Gvar.nulls_parents += 1
        return f"null{Gvar.nulls_parents}"
    
def geturl(user:t_user, msg: str):
    if(os.path.islink(msg)):
        try:
            return __geturl(msg,GetParent(msg),user)
        except Exception as e:
            return str(e)
    elif msg.startswith("/geturl"):
        try:
            msg = msg.split(' ')
            if len(msg) == 2:
                msg.append(GetParent(msg[1]))
            return __geturl(msg[1],msg[2],user)
        except Exception as e:
            
            Gvar.LOG.append(str(e) +" "+ str(user.id))
            return "command sintaxis: /geturl URL FILENAME"
    else:
        try:
            msg = msg.split(' ')
            return __geturl(msg[0],msg[1])
        except Exception as e:
            Gvar.LOG.append(str(e) +" "+ str(user.id))
            return "incorrect link and filename format"   

def cp(a):
    return a

def uptime():
    seconds_uptime = round(cp(Gvar.UPTIME)) 
    minutes_uptime = round(seconds_uptime // 60)
    hours_uptime = round(minutes_uptime // 60)
    days_uptime = round(hours_uptime // 24)
    seconds_uptime%=60
    minutes_uptime%=60
    hours_uptime%=24
    s = ""
    if(floor(days_uptime) != 0):
        s += f"{floor(days_uptime)}d"
    if(floor(hours_uptime) != 0):
        if(s != ""): s+='-'
        s += f"{floor(hours_uptime)}h"
    if(floor(minutes_uptime) != 0):
        if(s != ""): s+='-'
        s+= f"{floor(minutes_uptime)}m"
    if(floor(seconds_uptime) != 0):
        if(s != ""): s+='-'
        s+= f"{floor(seconds_uptime)}s"
    return s

def stats():
    s = uptime()
    s = "Uptime: " + s + "\n"
    CPU_P=round(st.cpu_percent(interval=1))
    CPU_F=round(st.cpu_freq().current)
    CPU_C=round(st.cpu_count())
    MEM_P = round(st.virtual_memory().percent)
    MEM_FREE= round(st.virtual_memory().available/Gvar.GB)
    RAM = round(st.virtual_memory().total/Gvar.GB)
    DISK_USED=round(100.0-st.disk_usage(os.getcwd()).percent)
    DISK_FREE=round(st.disk_usage(os.getcwd()).free/Gvar.GB)
    DISK_T = round(st.disk_usage(os.getcwd()).total/Gvar.GB)
    s += f"CPU: {CPU_P}%\n"
    s += f"CPU SPEED: {CPU_F}Mhz\n" 
    s += f"CPU COUNT: {CPU_C}\n"
    try:
        temp = st.sensors_temperatures()["coretemp"][0]
        s+=f"CPU_TEMP: {temp.current}C\n"
        s+=f"MAX_CPU_TEMP: {temp.critical}C\n"
    except Exception as e:
        print(e)
    s += f"RAM: {RAM}GB\n"
    s += f"RAM USED: {MEM_P}%\n" 
    s += f"RAM FREE: {MEM_FREE}GB\n"
    s += f"TOTAL DISK: {DISK_T}GB\n"
    s += f"DISK USED: {DISK_USED}%\n" 
    s += f"DISK FREE: {DISK_FREE}GB\n"
    return s

def upd(msg:pyrogram.types.Message,Ifile,Ofile):
    time.sleep(1)
    while 1:
        time.sleep(1)
        if Gvar.END_THREAD == 1:
            return
        try:
            total=os.path.getsize(Ifile)
            curr=os.path.getsize(Ofile)
            s=prog(curr,total,10,"compressing")
            if s != msg.text:
                msg=msg.edit_text(s)
            time.sleep(1)
        except Exception as e:
            print(e)
            time.sleep(1)

def ffmpegW(Ifile,Ofile):
    os.system(f'ffmpeg -i "{Ifile}" -c:v libx265 -compression_level 10 -tune "ssim" -preset "medium" "{Ofile}"')

def ffmpegL(Ifile,Ofile):
    os.system(f'ffmpeg -i "{Ifile}" -c:v libx265 -compression_level 10 -tune "ssim" -preset "medium" "{Ofile}"')

def VidComp(message:pyrogram.types.Message):
    try:
        msg = message.text.split(" ")
        Ifile = msg[1]
        Ofile = msg[2]
        try:
            NoPass = int(msg[3])
        except:
            NoPass = 1
    except:
        return "try use /comp Ifile Ofile number of pass"
    try:
        f=open(Ifile,"r")
        f.close()
    except:
        return "file not found"
    try:
        f=open(Ofile,"r")
        f.close()
        return "Ofile already exist"
    except:
        pass
    nms = message.reply("compressing...")
    while NoPass > 0:
        NoPass -= 1
        Gvar.END_THREAD = 0
        Tth=th.Thread(target=upd,args=[nms,Ifile,Ofile])
        Tth.start()
        if sys.platform != "win32":
            ffmpegW(Ifile,Ofile) 
        else:
            ffmpegL(Ifile,Ofile)
        Gvar.END_THREAD = 1
        os.remove(Ifile)
        os.rename(Ofile,Ifile)
    
def NoExt(s:str):
    st = ""
    for i in s:
        st = i + st
    st = st.split('.',1)[1]
    s = ""
    for i in st:
        s = i + s
    return s

def AdjustSize(size:int):
    GB = size / 1024**3
    MB = size / 1024**2
    KB = size / 1024**1
    if GB >= 1:
        return str(round(GB,3)) + "GB"
    if MB >= 1:
        return str(round(MB,3)) + "MB"
    if KB >= 1:
        return str(round(KB,3)) + "KB"
    return str(size) + "B"
    pass

def vid_down(user:t_user,msg:Message,bot:pyrogram.client.Client):
    try:
        do = VidDownloader(bot,user,user.chat,progress,[user,bot,"downloading video..."])
        link = msg.text
        if "instagram" in link:
            msg.text=link.replace("ddinstagram","instagram")
        do.download_video(msg.text)
        file = do.file
        thumb = (NoExt(file) + ".jpg")
        size = -1
        try:
            size = os.path.getsize(thumb)
            size = os.path.getsize(file)
        except Exception as e:
            Gvar.LOG.append(str(e)+f"\nthumb: {thumb}")
            thumb = (NoExt(file) + ".webp")
            size = -1
            try:
                size = os.path.getsize(file)
                size = os.path.getsize(thumb)
                size = os.path.getsize(file)
                size = AdjustSize(size)
            except Exception as e:
                Gvar.LOG.append(str(e)+f"\nthumb: {thumb}")
                thumb = None
        SendFile(user,file,bot,progress,[user,bot,"uploading video"],thumb,str(size))
        if(size != -1):
            os.remove(thumb)
    except Exception as e:
        msg.reply(str(e))
        Gvar.LOG.append(str(e))
        print(e)

def SetZero(i:int):
    s = str(i)
    if len(s) == 1:
        s = '000'+s
    elif len(s) == 2:
        s = "00"+s
    elif len(s) == 3:
        s = "0"+s
    return s

class Compressor:
    def __init__(self,user:t_user, bot:Client):
        self.size = -1
        self.running = -1
        self.name = -1
        self.curr = 0
        self.total = 0
        self.bot = bot
        self.user= user

    def t_progress(self):
        time.sleep(3)
        while self.running:
            try:
                self.curr = sizeof(self.name)
                progress(self.curr,self.total,self.user,self.bot,"compressing")
            except Exception as e:
                print(str(e))
                Gvar.LOG.append("compressing progress: " + str(e))
    
    def DirToTar(self,dirname,user:t_user,bot:Client):
        self.running = 1
        file=tar.TarFile(dirname+".01","w")
        self.total = sizeof(dirname)
        self.name = dirname + ".01"
        try:
            Thread(target=self.t_progress).start()
        except Exception as e:
            Gvar.LOG.append(str(e))
        file.add(dirname)
        self.running = 0
        file.close()
        return dirname + ".01"

def Compress(filename,MAX_Z = 2000*Gvar.MB):
    id = 1
    fid = 1
    file = open(filename,"rb")
    ch_file = open(filename + ".0001","wb")
    chunk = file.read(Gvar.MB)
    files = [filename + ".0001"]
    while chunk:
        ch_file.write(chunk)
        chunk = file.read(Gvar.MB)
        if(chunk):
            if id % (MAX_Z // Gvar.MB) == 0:
                fid += 1
                ch_file.close()
                ch_file = open(filename+ "." + SetZero(fid),"wb")
                files.append(filename + "." + SetZero(fid))
            id = id+1
    ch_file.close()
    file.close()
    return files

def SendFile(user:t_user,filename,bot:Client,progress:Callable = None,args = None,thumb = None,text = ""):
    try:
        if os.path.isdir(filename):
            comp = Compressor(user,bot)
            filename = comp.DirToTar(filename,user,bot)
        size = os.path.getsize(filename)
        files = [filename]
        if size > Gvar.MB * 2000:
            files = Compress(filename)
        file:str = ""
        for file in files:
            if file.endswith(".mp4") or file.endswith(".mpg") or file.endswith('.mkv'):
                bot.send_video(user.chat,file,progress=progress,progress_args=args,thumb=thumb,caption=text)
            elif file.endswith(".jpg") or file.endswith(".png"):
                bot.send_photo(user.chat,file,progress=progress,progress_args=args,thumb=thumb,caption=text)
            else:
                bot.send_document(user.chat,file,progress=progress,progress_args=args,thumb=thumb,caption=text)
            bot.delete_messages(user.chat,user.download_id)
            user.download_id = -1
    except Exception as e:
        Gvar.LOG.append(str(e))
        print(str(e))
        return str(e)

def send_file(bot:pyrogram.client.Client,message:Message,user:t_user):
    try:
        MSG = str(message.text.split(' ',1)[1])
        if MSG.isnumeric():
            MSG = int(MSG)
            dirs = os.listdir(user.current_dir)
            dirs.sort()
            MSG = dirs[MSG-1]
        
        MSG = user.current_dir + "/" + MSG
        
        if(os.path.isdir(MSG)):
            comp = Compressor(user,bot)
            MSG = user.current_dir+"/"+comp.DirToTar(MSG,user,bot)

        try:
            SendFile(user,MSG,bot,progress,[user,bot])
        except Exception as e:
            Gvar.LOG.append(str(e))
            return "error sending: "+str(e) 
        
        return "uploaded"
    except Exception as e:
        Gvar.LOG.append(str(e))
        return f"File not found E:\n{str(e)}"

def queuesZ():
    s = f"DOWNLOADS:{len(Gvar.QUEUE_DOWNLOAD)}\n"
    s += f"DOWNLOADS LINK:{len(Gvar.FUNC_QUEUE)}\n"
    s += f"MESSAGES:{len(Gvar.QUEUE_DIRECT)}\n"
    s += f"TO_SEND:{len(Gvar.QUEUE_TO_SEND)}\n"
    return s

def reset(uid):
    res = "access denied"
    if uid in Gvar.ADMINS:
        try:
            rq.get(Gvar.DEPLOY_HOOK)
            res = "restarting..."
        except Exception as e:
            res = str(e)
    return res

def remove(MSG,user:t_user):
    DIRECT = ""
    try:
        MSG = MSG.split(" ")[1]
        dirs = os.listdir(user.current_dir)
        dirs.sort()
        if MSG.isnumeric():
            MSG = int(MSG)
            DIRECT = user.current_dir+"/"+dirs[MSG-1]
        else:
            DIRECT = user.current_dir+'/'+MSG
        if os.path.isdir(DIRECT):
            os.removedirs(DIRECT)
        else:
            os.remove(DIRECT)
        return "removed"
    except Exception as e:
        Gvar.LOG.append(str(e))
        return str(e)

def ClearCommand(command:str):
    command = command.split(" ",1)
    while len(command) < 2:
        command.append(None)
    return command

def USER_PROCCESS(user:t_user, message: Message,bot:pyrogram.client.Client):
    MSG = str(message.text)
    command = ClearCommand(MSG)[1]
    if MSG.startswith("http"):
        Gvar.FUNC_QUEUE.append([vid_down,[user,message,bot]])
    elif MSG.startswith("/comp"):
        tth=th.Thread(target=VidComp,args=[message],daemon=True)
        tth.start()
        return "in progress"
    elif MSG.startswith("/help"):
        return Gvar.HELP
    elif MSG.startswith("/dir"):
        return user.current_dir
    elif MSG.startswith("/queues"):
        return queuesZ()
    elif MSG.startswith("/sz"):
        return user.size(command)
    elif MSG.startswith("/ls"):
        return user.ls()
    elif MSG.startswith("/restart") :
        return reset(message.from_user.id)
    elif MSG.startswith("/cd"):
        user.chdir(command)
        return "Changed !!!"
    elif MSG.startswith("/mkdir"):
        user.mkdir(command)
        return "Created !!!"
    elif MSG.startswith("/geturl"):
        return geturl(user,message.text)
    elif MSG.startswith('/stats'):
        return stats()
    elif MSG.startswith("/link"):
        return GenerateDirectLink(message)
    elif MSG.startswith("/eval") and message.from_user.id in Gvar.ADMINS:
        exec(command)
    elif MSG.startswith('/send'):
        return send_file(bot,message,user)
    elif MSG.startswith("/rm"):
        return remove(MSG,user)
    return 0

def UPD_HOUR():
    Gvar.UPTIME+=1

def FUNC_QUEUE_HANDLER():
    if len(Gvar.FUNC_QUEUE) > 0:
        func,args = Gvar.FUNC_QUEUE[0]
        Gvar.FUNC_QUEUE.pop(0)
        func(*args)

timer = Timer(
    [   UPD_HOUR,
        FUNC_QUEUE_HANDLER],
    [1,60]
)
timer.start()