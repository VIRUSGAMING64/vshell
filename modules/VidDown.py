import yt_dlp
import time
from pyrogram.types import *
from pyrogram.client import *
import modules.Gvar as Gvar
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
        curr = 0
        try:
            curr = down["downloaded_bytes"]
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
        time.sleep(1)
        self.progress(curr,total,*self.args)

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
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except Exception as e:
                Gvar.LOG.append(str(e)+ " " + str(self.user.id))
            finally:
                self.bot.delete_messages(self.user.chat,self.user.download_id)