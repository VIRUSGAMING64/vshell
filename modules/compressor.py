import time
import modules.Gvar as Gvar
import tarfile as tar
import threading as th
from modules.users import *

class Compressor:
    def __init__(self,user, bot,progress = None):
        self.size = -1
        self.progress = progress
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
                self.progress(self.curr,self.total,self.user,self.bot,"compressing")
            except Exception as e:
                print(str(e))
                Gvar.LOG.append("compressing progress: " + str(e))
    
    def DirToTar(self,dirname,user,bot):
        self.running = 1
        file=tar.TarFile(dirname+".01","w")
        self.total = sizeof(dirname)
        self.name = dirname + ".01"
        try:
            th.Thread(target=self.t_progress).start()
        except Exception as e:
            Gvar.LOG.append(str(e))
        file.add(dirname)
        self.running = 0
        file.close()
        return dirname + ".01"