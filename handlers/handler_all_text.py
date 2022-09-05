# импортируем ответ пользователю
from settings.message import MESSAGES
from settings.config import KEYBOARD
# импортируем класс-родитель
from handlers.handler import Handler

from models.users import user



class HandlerAllText(Handler):
    """
    Класс обрабатывает входящие текстовые сообщения от нажатия на кнопки
    """

    def __init__(self, bot):
        super().__init__(bot)


    def pressed_btn_settings(self, message):
        """
        обрабатывает входящие текстовые сообщения
        от нажатия на кнопоку 'Настройки'.
        """
        self.bot.send_message(message.chat.id, MESSAGES['settings'],
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())


    def pressed_btn_help(self, message):
        """
        обрабатывает входящие текстовые сообщения
        от нажатия на кнопоку 'Help'.
        """
        self.bot.send_message(message.chat.id, MESSAGES['HELP'],
                              parse_mode="HTML",
                              reply_markup=self.keybords.help_menu())

    def pressed_btn_lowprice(self, message):
        """
        Обработка события нажатия на кнопку 'Lowprice'.
        """
        self.bot.send_message(message.chat.id, "Ваш выбор \U00002198 Lowprice",
                              reply_markup=self.keybords.remove_menu())
        user.set_user('command', 'lowprice')
        self.bot.send_message(message.chat.id, "Для возврата назад нажмите ⏪",
                              reply_markup=self.keybords.lowprice_menu())

    def pressed_btn_highprice(self, message):
        """
        Обработка события нажатия на кнопку 'Highprice'.
        """
        self.bot.send_message(message.chat.id, "Ваш выбор \U00002197 Highprice",
                              reply_markup=self.keybords.remove_menu())
        user.set_user('command', 'highprice')
        self.bot.send_message(message.chat.id, "Для возврата назад нажмите ⏪",
                              reply_markup=self.keybords.lowprice_menu())

    def pressed_btn_bestdeal(self, message):
        """
        Обработка события нажатия на кнопку 'Bestdeal'.
        """
        self.bot.send_message(message.chat.id, "Ваш выбор \U00002705 Bestdeal",
                              reply_markup=self.keybords.remove_menu())
        user.set_user('command', 'bestdeal')
        print('pressed_btn_bestdeal(command)=', user)
        self.bot.send_message(message.chat.id, "Для возврата назад нажмите ⏪",
                              reply_markup=self.keybords.bestdeal_menu())

    def pressed_btn_history(self, message):
        """
        Обработка события нажатия на кнопку 'History'.
        """
        self.bot.send_message(message.chat.id, "Ваш выбор \U0001F4D3 History",
                              reply_markup=self.keybords.remove_menu())
        user.set_user('command', 'bestdeal')
        self.bot.send_message(message.chat.id, "Для возврата назад нажмите ⏪",
                              reply_markup=self.keybords.history_menu())

    def pressed_btn_back(self, message):
        """
        обрабатывает входящие текстовые сообщения от нажатия на кнопку 'Назад'.
        """
        self.bot.send_message(message.chat.id, "Вы вернулись назад",
                              reply_markup=self.keybords.start_menu())

    def pressed_btn_currency(self, message):
        """
        обрабатывает входящие текстовые сообщения от нажатия на кнопку 'Currency'
        (для выбора валюты).
        """
        self.bot.send_message(message.chat.id, "Выберете валюту:",
                              reply_markup=self.keybords.set_select_currency())

    def pressed_btn_lang(self, message):
        """
        обрабатывает входящие текстовые сообщения от нажатия на кнопку 'Language'
        (для выбора валюты).
        """
        self.bot.send_message(message.chat.id, "Выберете язык:",
                              reply_markup=self.keybords.set_select_lang())



    def handle(self):
        # обработчик(декоратор) сообщений,
        # который обрабатывает входящие текстовые сообщения от нажатия кнопок.
        @self.bot.message_handler(func=lambda message: True)
        def handle(message):
            # ********** меню ********** #


            if message.text == KEYBOARD['Lowprice']:
                self.pressed_btn_lowprice(message)

            if message.text == KEYBOARD['Highprice']:
                self.pressed_btn_highprice(message)

            if message.text == KEYBOARD['Bestdeal']:
                self.pressed_btn_bestdeal(message)

            if message.text == KEYBOARD['History']:
                self.pressed_btn_history(message)

            if message.text == KEYBOARD['HELP']:
                self.pressed_btn_help(message)

            if message.text == KEYBOARD['SETTINGS']:
                self.pressed_btn_settings(message)

            if message.text == KEYBOARD['<<']:
                self.pressed_btn_back(message)

            if message.text == KEYBOARD['CURRENCY']:
                self.pressed_btn_currency(message)

            if message.text == KEYBOARD['LANG']:
                self.pressed_btn_lang(message)


