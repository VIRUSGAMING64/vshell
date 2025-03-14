import yt_dlp
import time
from pyrogram.types import *
from pyrogram.client import *
import modules.Gvar as Gvar
from modules.users import t_user

class VidDownloader:
    file = ""
    arg = "downloading video"
    def __init__(self, bot:Client,user,chat_id,progress:callable,args:list):
        self.bot = bot
        self.progress = progress
        self.args = args
        self.user = user
        self.chat_id = chat_id
        self.file = None
        
    def my_hook(self, down):
        try:
            curr = 0
            try:
                curr = down["downloaded_bytes"]
            except Exception as e:
                print(e)
            try:
                self.file = down["filename"]
            except:
                pass
            total = curr * 2
            try:
                total = down["total_bytes"]
            except Exception as e:
                try:
                    total = int(down["total_bytes_estimate"])
                except:
                    pass
                e=str(e)
            self.progress(curr,total,*self.args)
        except Exception as e:
            Gvar.LOG.append(str(e))

    def download_video(self, url):
        self.user.download_id = self.bot.send_message(self.user.chat,"downloading").id
        ydl_opts = {
            "paths":{
                "home":self.user.current_dir
            },
            'format': 'best',
            'writethumbnail': True,
            'progress_hooks': [self.my_hook],
        }
        Gvar.DOWNLOADING = 1
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                Gvar.LOG.append(str(e)+ " " + str(self.user.id))
                self.bot.edit_message_text(self.chat_id,self.user.download_id,"unknow error\n"+str(e))
                time.sleep(60)
            finally:
                self.bot.delete_messages(self.user.chat,self.user.download_id)
                self.user.download_id = -1
        Gvar.DOWNLOADING = 0