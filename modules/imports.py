import modules.Gvar as Gvar
import pyrogram
from pyrogram.client import Client
from pyrogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from pyrogram import filters
from math import floor
import time
from modules.datatypes import t_user, GetUser, INVALID, MESSAGE, CLIENT, USER_ID
import threading as th
import requests as req
import modules.Utils as Utils
from modules.pool import v_pool, v_Timer
from modules.users import USERS
import os
from modules.web import WEB
