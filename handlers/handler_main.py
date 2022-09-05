# импортируем класс HandlerCommands - обработка команд
from handlers.handler_command import HandlerCommands
# импортируем класс HandlerAllText -
# обработка нажатия на кнопки и иные сообщения
from handlers.handler_all_text import HandlerAllText
# импортируем класс HandlerInlineQuery обработка нажатия на кнопки инлайн
from handlers.handler_inline_query import HandlerInlineQuery

from handlers.handler_lowprice import HandlerLowprice
from handlers.handler_bestdeal import HandlerBestdeal
from handlers.handler_history import HandlerHistory



class HandlerMain:
    """
    Класс-компоновщик
    """
    def __init__(self, bot):
        # получаем объект нашего бота в модуле main
        self.bot = bot
        # здесь будет инициализация обработчиков
        self.handler_commands = HandlerCommands(self.bot)
        self.handler_all_text = HandlerAllText(self.bot)
        self.handler_inline_query = HandlerInlineQuery(self.bot)
        self.handler_lowprice = HandlerLowprice(self.bot)
        self.handler_bestdeal = HandlerBestdeal(self.bot)
        self.handler_history = HandlerHistory(self.bot)




    def handle(self):
        # здесь будет запуск обработчиков
        self.handler_commands.handle()
        self.handler_history.handle()
        self.handler_lowprice.handle()
        self.handler_all_text.handle()
        self.handler_inline_query.handle()
        self.handler_bestdeal.handle()
