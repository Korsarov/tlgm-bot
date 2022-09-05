from handlers.handler import Handler
import string
import requests
from typing import Union, List
from telebot.types import Message, InputMediaPhoto, CallbackQuery
from models.users import user
from settings.constants import HISTORY_TEMPLATE_RU, HISTORY_TEMPLATE_EN, LOOK_OR_CLEAR_LIST, FULL_OR_LAST_LIST
from settings.message import MESSAGES
from settings.config import KEYBOARD

class HandlerHistory(Handler):

    def __init__(self, bot):
        super().__init__(bot)


    def history_menu(self, message: Union[Message, CallbackQuery]) -> None:
        """
        Функция выводит пользователю меню раздела History в виделе inline-кнопок.
        Проверяет входящий аргумент на тип данных.

        :param message: Message
        :return: None
        """
        if isinstance(message, Message):
            message_text = message.text
        else:
            message_text = message.data
        bot_message = self.bot.send_message(
            message.from_user.id, 'Вы можете просматривать и очищать историю поиска.\nВыберите действие: ',
            reply_markup=self.keybords.look_or_clear_history()
        )
        user.set_user('bot_message', bot_message)

    def callback_history_menu(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик  inline-кнопок. Реагирует только на элменты списка HISTORY_LIST.
        В случае выбора пользователем - Просмотреть, выводит клавиатуру с подменю выбора режима просмотра истории.
        В случае выбора пользователем - Очистить, очищает историю пользователя и выводит сообщении
        об успешной очистке и дальнейших действиях.

        :param call: CallbackQuery
        :return: None
        """
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        if call.data == LOOK_OR_CLEAR_LIST[0]:
            bot_message = self.bot.send_message(call.from_user.id,
                                                'Полная история - содержит все ваши результаты поиска отелей.'
                                                '\nПоследние действия - содержит последние 5 результатов поиска.',
                                                reply_markup=self.keybords.full_or_last_history())
            user.set_user('bot_message', bot_message)
        else:
            self.BD.delete_all_user_and_hotel(call.from_user.id)
            self.bot.send_message(call.from_user.id, 'История успешно очищена')
            bot_message = self.bot.send_message(call.from_user.id, MESSAGES['HELP'], parse_mode='HTML',
                                                reply_markup=self.keybords.start_menu())
            user.set_user('bot_message', bot_message)

    def callback_history_showing(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-кнопок. Реагирует только на команды из списка HISTORY_SHOW_LIST.
        Исходя из выбранного варианта, делает запрос к БД, и с полученным ответом перенаправляет в функцию
        history_showing. Если ответ пуст, то сообщает пользователю, что история пуста.

        :param call: CallbackQuery
        :return: None
        """
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        if call.data == FULL_OR_LAST_LIST[0]:
            user_command = self.BD.select_history_user_five(call.from_user.id)
            if user_command:
                self.history_showing(call, user_command)
            else:
                self.bot.send_message(call.from_user.id, 'История запросов пустая.')
                bot_message = self.bot.send_message(call.from_user.id, MESSAGES['HELP'], parse_mode='HTML',
                                                    reply_markup=self.keybords.start_menu())
                user.set_user('bot_message', bot_message)
        else:
            user_command = self.BD.select_history_user_five(call.from_user.id)
            if user_command:
                if len(user_command) > 5:
                    user_command = user_command[:5]
                user_command.reverse()
                self.history_showing(call, user_command)
            else:
                self.bot.send_message(call.from_user.id, 'История запросов пустая.')
                bot_message = self.bot.send_message(call.from_user.id, MESSAGES['HELP'], parse_mode='HTML',
                                                    reply_markup=self.keybords.start_menu())
                user.set_user('bot_message', bot_message)

    def history_showing(self, call: CallbackQuery, user_command: List[tuple]) -> None:
        """
        Функция - обрабатывает ответ с БД и циклом выводит пользователю шаблон с данными о команде.
        Сам шаблон в зависимости от языка запроса получаем из функции locale_history.
        На каждой итерации делает запрос к БД, для получения истории найденных отелей. Если отели найдены,
        то направляется в функцию history_hotels_show. В противном случае, сообщает пользователю,
        что по данной команде не были найдены отели.

        :param call: CallbackQuery
        :param user_command: List[tuple]
        :return: None
        """
        for command in user_command:
            history_template = self.locale_history(command[3])
            self.bot.send_message(call.from_user.id, history_template.format(
                command[1], command[2], command[3], command[4], command[5])
                             )
            hotels = self.BD.select_history_hotel(command[0])
            if hotels:
                for hotel in hotels:
                    self.history_hotels_show(call, hotel)
            else:
                self.bot.send_message(call.from_user.id, 'По данному запросу отели не были найдены')
        self.bot.send_message(call.from_user.id, 'Показ истории завершён')
        bot_message = self.bot.send_message(call.from_user.id, MESSAGES['HELP'], parse_mode='HTML',
                                            reply_markup=self.keybords.start_menu())
        user.set_user('bot_message', bot_message)

    def history_hotels_show(self, call: CallbackQuery, hotel: tuple) -> None:
        """
        Функция - обрабатывающая кортеж с данными об отеле и выводящий пользователя информацию о найденном отеле.
        Если в БД хранились url фото, то выводит сообщение пользователю медиагруппой, с фотографиями.

        :param call: CallbackQuery
        :param hotel: tuple
        :return: None
        """
        if hotel[1] != '':
            photo_list = hotel[1].split()
            media_massive = []
            index = 0
            for photo in photo_list:
                response = requests.get(photo)
                if str(response.status_code).startswith('2'):
                    index += 1
                    media_massive.append(
                        InputMediaPhoto(photo, caption=hotel[0] if index == 1 else '', parse_mode='Markdown')
                    )
            self.bot.send_media_group(call.from_user.id, media=media_massive)
        else:
            self.bot.send_message(call.from_user.id, hotel[0])

    def locale_history(self, city: str) -> str:
        """
        Функция - проверяюща введённые пользователем данные и исходя из них,
        возвращает шаблон на русском, или английском языках.

        :param city: str
        :return: str
        """
        for sym in city:
            if sym not in string.printable:
                return HISTORY_TEMPLATE_RU
        return HISTORY_TEMPLATE_EN

    def handle(self):
        @self.bot.message_handler(func=lambda message: message.text == KEYBOARD['LOOK'])
        def handle_history(message):
            self.history_menu(message)

        @self.bot.message_handler(func=lambda message: message.text == KEYBOARD['History'])
        def handle_history(message):
            self.history_menu(message)

        @self.bot.callback_query_handler(func=lambda call: call.data in LOOK_OR_CLEAR_LIST)
        def callback_inline(call):
            self.callback_history_menu(call)

        @self.bot.callback_query_handler(func=lambda call: call.data in FULL_OR_LAST_LIST)
        def callback_inline(call):
            self.callback_history_showing(call)


