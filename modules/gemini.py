import modules.Gvar as Gvar
import google.generativeai as googleIA
import os
try:
    googleIA.configure(api_key=Gvar.GOOGLE_API)
except Exception as e:
    Gvar.LOG.append("Gemini: "+str(e))
    
class GenAI:
    def __init__(self):
        self.model = googleIA.GenerativeModel().start_chat()
    def query(self,qe:str):
        return "don't working..."
        return self.model.send_message(qe).text

chats = {}

def NewChat(id):
    chats[id] = GenAI()
    return chats[id]

def GetAI(id):
    try:
        chat = chats[id]
        return chat 
    except Exception as e:
        print(str(e))
        return NewChat(id)
