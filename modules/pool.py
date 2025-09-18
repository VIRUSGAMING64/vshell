import threading as th
import time
import os
import modules.Gvar as Gvar
import typing as types

class TempFile():
    def __init__(self,name,mode):
        self.name = os.path.realpath(name)
        self.mode = mode
        self.file = open(name,mode)
    def write(self,data):
        return self.file.write(data)
    def read(self,size):
        return self.file.read(size)
    def kill(self):
        self.file.close()
        os.remove(self.name)

def Time(func:callable,tm:int):
    if Gvar.TESTING_DEPENDENCY == 1:
        return
    while 1:
        time.sleep(tm)
        func()

class v_Timer:
    def __init__(self,func=None,time:list=[],deamons = []):
        
        self.time = time
        if func is None:
            self.funcs = []
            self.threads=[]
            self.time = []
            return
        if func is callable:
            self.funcs = [func]
        else:
            self.funcs = func
            self.threads = []
        if len(func) != len(time):
            raise "len(func) < len(time)"
        i = 0
        for func in self.funcs:
            if self.time[i] < 0:
                raise "time can't be < 0"
            self.threads.append(
                th.Thread(target=Time,args=[func,self.time[i]])
            )
            i+=1
    def start(self,pos=None):
        if pos is None:
            for i in range(len(self.threads)):
                self.threads[i].start()
            pass
        else:
            self.threads[pos].start()
            pass
    def add(self,func:callable,time:int):
        self.funcs.append(func)
        self.time.append(time)
        self.threads.append(th.Thread(target=Time,args=[func,time]))
        self.start(len(self.time)-1)

class v_pool:
    funcs:list[th.Thread] = []
    def __init__(self,funcs:list,args:list[list]=[],sequence:bool=False):
        for i in range(len(funcs)):
            if(i < len(args)):
                if args[i] == None:
                    args[i] = ()    
                funcs[i] = th.Thread(target=funcs[i],args=args[i])
            else:
                funcs[i] = th.Thread(target=funcs[i])
        self.sequence = sequence
        self.funcs = funcs
    def start_all(self,deamon = 0,indices = []):
        if indices != []:
            for i in indices:
                self.Setdeamon(i,deamon)
        elif deamon != 0:
            self.Setdeamon()
        for i in range(len(self.funcs)):
            if self.funcs[i].is_alive() == 0:
                if self.sequence == 0:
                    self.funcs[i].start()
                else:
                    self.funcs[i].join()
        return 1
    def start(self,index:int=None):
        if(index == None):
            return self.start_all()
        if(self.funcs[index].is_alive()):
            return 0
        return self.funcs[index].start()
    def Setdeamon(self,index=None,deamon = 1):
        if index is None:
            for i in range(len(self.funcs)):
                self.funcs[i].daemon=deamon
        else:
            self.funcs[index].daemon=deamon
    def add_thread(self,func:callable,start = 1,deamon=0):
        func=th.Thread(target=func,deamon=deamon)
        self.funcs.append(func)
        if(start):
            self.funcs[len(self.funcs)].start()

class PoolQueueHandler:
    def __init__(self,func:callable,QUEUE:list = [],threads:int = os.cpu_count()+4,ttl:int = 1):
        self.QUEUE=QUEUE
        self.ERRORS = []
        self.THREADS = threads
        self.activator = func
        self.T_THREADS = threads
        self.TTL = ttl
        self.running = 0
        self.daemon = 0
    
    def Factivator(self,args):
        self.activator(*args)
        self.running -= 1
    
    def __run(self):
        while True:
            while self.running < self.THREADS:
                if len(self.QUEUE) == 0:
                    break
                self.running += 1            
                th.Thread(target=self.Factivator,daemon=self.daemon,args=[self.QUEUE[0]]).start()
                self.QUEUE.pop(0)
            time.sleep(self.TTL)      
    
    def run(self,daemon = False):
        self.daemon = daemon
        th.Thread(target=self.__run,daemon=daemon).start()

    def add(self,args:types.Iterable):
        lis : list = []
        for i in args:
            lis.append(i)
        self.QUEUE.append(lis)
    
    def pause(self):
        self.THREADS = 0
    
    def resume(self):
        self.THREADS = self.T_THREADS

class Counter:
    init = -1
    end = -1
    def __init__(self):
        pass
    def start(self):
        self.init = time.process_time_ns()
    def stop(self):
        self.end=time.process_time_ns()
        if self.init == -1:
            self.end = -1
            raise "don't started"
        self.elapsed = (self.end - self.init)