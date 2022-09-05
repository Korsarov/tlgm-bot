from handlers.handler import Handler
import re
import json
from typing import List, Dict, Union
from telebot.types import Message, CallbackQuery
from settings.config import querystring_for_bestdeal
from botrequests.request_main import request_bestdeal
from models.users import user


class HandlerBestdeal(Handler):

    def __init__(self, bot):
        super().__init__(bot)




    def handle(self):
        pass


