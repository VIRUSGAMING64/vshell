import modules.Gvar as Gvar
from telegram import Update, InlineQueryResultArticle, InputTextMessageContent, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, InlineQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError
from math import *
import time
from modules.datatypes import *
import threading as th
import requests as req
import modules.Utils as Utils
from modules.pool import *
from modules.users import *
import os
from ctypes import *
from json.encoder import JSONEncoder
from json.decoder import JSONDecoder
import asyncio
from modules.IDM import *
from modules.web import WEB
from threading import Thread