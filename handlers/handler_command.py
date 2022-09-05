# импортируем класс родитель
from handlers.handler import Handler
from models.users import user
from settings.config import KEYBOARD

class HandlerCommands(Handler):
    """
    Класс обрабатывает входящие команды /start и /help и т.п.
    """
    def __init__(self, bot):
        super().__init__(bot)

    def pressed_command_start(self, message):
        """
        обрабатывает входящие /start команды
        """
        # user.set_user('user_id', message.from_user.id)
        self.bot.send_message(message.chat.id,
                              '{} добро пожаловать в телеграм-бот турагентства по поиску отелей.\n'
                              'Для начала нажмите кнопку START'.format(
                                  message.from_user.first_name),
                              reply_markup=self.keybords.button_start())

    def pressed_button_start(self, message):
        """
        обрабатывает входящие /start команды
        """
        user.set_user('user_id', message.from_user.id)
        self.bot.send_message(message.chat.id,
                              '{} выбирите необходимую команду\n'
                              'или для получения справки нажмите кнопку Help'.format(
                                  message.from_user.first_name),
                              reply_markup=self.keybords.start_menu())

    def handle(self):
        # обработчик(декоратор) сообщений,
        # который обрабатывает входящие /start команды.
        @self.bot.message_handler(commands=['start'])
        def handle(message):
            if message.text == '/start':
                self.pressed_command_start(message)
        @self.bot.message_handler(func=lambda message: message.text == KEYBOARD['START'])
        def handrer_start_button(message):
            self.pressed_button_start(message)

