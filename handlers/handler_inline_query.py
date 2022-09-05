# импортируем класс родитель
from handlers.handler import Handler

from models.users import user




class HandlerInlineQuery(Handler):
    """
    Класс обрабатывает входящие текстовые
    сообщения от нажатия на инлайн-кнопоки
    """

    def __init__(self, bot):
        super().__init__(bot)

    def set_rub(self, call):
        currency = 'RUB'
        user.set_user('currency', currency)
        self.bot.send_message(call.message.chat.id, 'Вы вбрали валюту: рубль',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())

    def set_usd(self, call):
        # currency = 'USD'
        user.set_user('currency', call.data)
        self.bot.send_message(call.message.chat.id, 'Вы выбрали валюту: доллар',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())

    def set_eur(self, call):
        currency = 'EUR'
        user.set_user('currency', currency)
        self.bot.send_message(call.message.chat.id, 'Вы выбрали валюту: евро',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())

    def set_ru(self, call):
        locale = 'ru_RU'
        user.set_user('locale', locale)
        self.bot.send_message(call.message.chat.id, 'Вы выбрали русский язык',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())
    def set_en(self, call):
        locale = 'en_EN'
        user.set_user('locale', locale)
        self.bot.send_message(call.message.chat.id, 'Вы выбрали английский язык',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())

    def set_non_setting(self, call):
        self.bot.send_message(call.message.chat.id, 'Вы выбрали неправильную настройку',
                              parse_mode="HTML",
                              reply_markup=self.keybords.settings_menu())



    def handle(self):
        # обработчик(декоратор) запросов от нажатия на Inline-кнопки .
        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            code = call.data
            if code == 'RUB':
                self.set_rub(call)
            elif code == 'USD':
                self.set_usd(call)
            elif code == 'EUR':
                self.set_eur(call)
            elif code == 'ru':
                self.set_ru(call)
            elif code == 'en':
                self.set_en(call)
            else:
                self.set_non_setting(call)










