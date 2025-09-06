import urllib.request as reqs
import http.client
from threading import *
import time
import os

class downloader:
    def __init__(self,progress:callable = None,threads = os.cpu_count()):
        self.index = [] #TODO
        self.progress = progress
        self.threads = threads
        self.running = 0
        self.ids = 0

    def save_pointers(self):
        file = open("savefile.pyidm","w")
        self.pause = 1
        while self.running != 0:
            time.sleep(1)
        for i in self.index:
            file.write(str(i)+"\n")
        file.close()
    
    def worker(self,l,r,url,id):
        response:http.client.HTTPResponse = reqs.urlopen(url)
        response.seek(0,l) #TODO saber que retorna esa funcion
        SIZE = 4096
        size = (r-l+1)
        try:
            os.mkdir("temp")
        except:
            pass
        file = open(f"temp/{id}","wb")
        for i in range(size / SIZE):
            data = response.read(SIZE)
            file.write(data)
            print(len(data)*8)
        file.write(response.read(size%SIZE))
        file.close()
        response.close()

    def __download(self,url,size):
        chunks_size = size // self.threads
        mod = size % self.threads
        i = 0
        j = chunks_size
        id = 1
        while(j-chunks_size < size-mod):
            self.running += 1
            Thread(target=self.worker,args=[i,j,url,id]).start()
            id += 1
            while self.running >= self.threads:
                time.sleep(1)

        return 1

    def download(self,url):
        response:http.client.HTTPResponse = reqs.urlopen(url)
        if 1:
            size = response.length
            response.close()
            return self.__download(url,size)
        else:
            return False
    