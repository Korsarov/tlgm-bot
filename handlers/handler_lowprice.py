from handlers.handler import Handler
from settings.message import MESSAGES
from models.users import user
from telebot.types import CallbackQuery, Message
from settings.constants import CALLBACK_HOTELS_AND_PHOTOS, LSTEP, CURRENCY_LIST, YES_OR_NO_LIST
from settings.config import KEYBOARD
from datetime import date, timedelta, datetime
from botrequests.request_main import request_bestdeal, request_property_list, request_get_photo, request_location
from requests import Response
import json
from typing import Any, Dict, Union
from models.hotels import Hotel
import re
from telegram_bot_calendar import DetailedTelegramCalendar
from settings.additional import check_num, check_status_code, hotel_template, bestdeal_logic, photo_append



class CustomCalendar(DetailedTelegramCalendar):
    """
    Дочерний Класс (Родитель - DetailedTelegramCalendar). Необходим для изменения
    дефолтного значения у параметров empty month_button и empty_year_button.
    """
    empty_month_button: str = ''
    empty_year_button: str = ''

class HandlerLowprice(Handler):

    def __init__(self, bot):
        super().__init__(bot)

    def choice_city(self, message: Union[Message, CallbackQuery]) -> None:
        """
        Функция, проверяет входящий тип данных из предыдущей функции и запрашивает город
        для поиска отелей.

        :param message: Union[Message, CallbackQuery]
        :return: None
        """
        self.bot.send_message(message.from_user.id, 'В каком городе ищем отель?')
        if isinstance(message, CallbackQuery):
            self.bot.register_next_step_handler(message.message, self.search_city)
        else:
            self.bot.register_next_step_handler(message, self.search_city)


    def search_city(self, message: Message) -> None:
        """
        Функция - обрабатывает введённый пользователем город. Делает запрос на rapidapi.com.
        В случае ошибки запроса, сообщает о неполадках и возвращает пользователя на ввод города.
        В случае положительного ответа, обрабатывает его и в виде inline-кнопок отправляет
        пользователю все похожие варианты ответа.

        :param message: Message
        :return: None
        """
        response = request_location(message)
        pattern_city_group = r'(?<="CITY_GROUP",).+?[\]]'
        find_cities = re.findall(pattern_city_group, response.text)
        if len(find_cities[0]) > 20:
            pattern_destination_id = r'(?<="destinationId":")\d+'
            destination = re.findall(pattern_destination_id, find_cities[0])
            pattern_city = r'(?<="name":")\w+[\s, \w]\w+'
            city = re.findall(pattern_city, find_cities[0])
            city_list = list(zip(destination, city))
            print('city_list=', city_list)
            bot_message = self.bot.send_message(
                message.from_user.id, 'Уточните, пожалуйста локацию:',
                reply_markup=self.keybords.set_select_city(city_list)
            )
            user.set_user('bot_message', bot_message)
            # user.set_user('user_id', message.from_user.id)
        else:
            self.bot.send_message(message.from_user.id, 'Город не найден. Попробуйте ввести город ещё раз.',
                                  reply_markup=self.keybords.button_start())



    def callback_city(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-кнопок. Реагирует только на информацию из кнопок
        выбора города. Далее, в формате inline-кнопок, предоставляет пользователю выбор валюты.

        :param call: CallbackQuery
        :return: None
        """
        for city in call.message.json['reply_markup']['inline_keyboard']:
            if city[0]['callback_data'] == call.data:
                user.set_user('city', city[0]['text'])
                user.set_user('city_id', call.data)
                break
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text='Вы выбрали город: {}'.format(user.city)
        )
        bot_message = self.bot.send_message(
            call.from_user.id, 'Выберите валюту, в которой желаете увидеть стоимость отелей:',
            reply_markup=self.keybords.set_select_currency()
        )
        user.set_user('bot_message', bot_message)

    def callback_currency(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-кнопок. Реагирует только на информацию входящую
        в список аббревиатур валют. Если начальная команда введенная пользователем равна 'bestdeal',
        то запрашиваем у пользователя информацию о диапазоне цен. Переходя в функцию 'price_min'
        Если команда равна 'lowprice', или 'highprice', переходим в следующую функцию 'count_hotel'.

        :param call: CallbackQuery
        :return: None
        """
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        self.bot.edit_message_text(
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            text='Стоимость отелей будет показана в {}'.format(call.data)
        )
        user.set_user('currency', call.data)

        if user.command != 'bestdeal':
            self.count_hotel(call)
        else:
            self.bot.send_message(call.from_user.id,
                                  'Давайте зададим диапазон цены на проживание в указанной вами валюте '
                                  '({}).'.format(user.currency))
            bot_message = self.bot.send_message(call.from_user.id, 'Введите минимальную цену (целое число):')
            user.set_user('bot_message', bot_message)
            self.bot.register_next_step_handler(call.message, self.price_min)

    def price_min(self, message: Message) -> None:
        """
        Функция - Проверяющая на корректность введённой информации пользователем о минимальной цене.
        Если ответ корректный, запрашивает данные о максимальной цене, если нет, повторяет предыдущий запрос.

        :param message: Message
        :return: None
        """

        if message.text.isdigit():
            user.set_user('price_min', int(message.text))
            self.bot.edit_message_text(
                chat_id=user.bot_message.chat.id, message_id=user.bot_message.message_id,
                text='Минимальная цена: {}'.format(message.text)
            )
            bot_message = self.bot.send_message(message.from_user.id, 'Введите максимальную цену (целое число):')
            user.set_user('bot_message', bot_message)
            self.bot.register_next_step_handler(message, self.price_max)
        else:
            self.bot.send_message(message.from_user.id, 'Не корректный ввод. Цена должна быть целым числом!')
            self.bot.send_message(message.from_user.id, 'Введите минимальную цену в целых числах:')
            self.bot.register_next_step_handler(message, self.price_min)

    def price_max(self, message: Message) -> None:
        """
        Функция - Проверяющая на корректность введённой информации пользователем о максимальной цене.
        Если ответ корректный, запрашивает данные о минимальном расстоянии поиска, если нет, повторяет предыдущий запрос.

        :param message: Message
        :return: None
        """

        if message.text.isdigit():
            user.set_user('price_max', int(message.text))
            if user.price_min >= user.price_max:
                self.bot.send_message(message.from_user.id, 'Не корректный ввод. '
                                                            'Максимальная цена должна быть больше минимальной')
                self.bot.send_message(message.from_user.id, 'Введите максимальную цену (целое число):')
                self.bot.register_next_step_handler(message, self.price_max)
            else:
                self.bot.edit_message_text(
                    chat_id=user.bot_message.chat.id, message_id=user.bot_message.message_id,
                    text='Максимальная цена: {}'.format(message.text)
                )
                self.bot.send_message(message.from_user.id, 'Теперь зададим расстояния от отеля до центра города.')
                bot_message = self.bot.send_message(message.from_user.id, 'Введите минимальное расстояние в километрах:')
                user.set_user('bot_message', bot_message)
                self.bot.register_next_step_handler(message, self.distance_min)
        else:
            self.bot.send_message(message.from_user.id, 'Не корректный ввод. Цена должна быть целым числом!')
            self.bot.send_message(message.from_user.id, 'Введите максимальную цену (целое число):')
            self.bot.register_next_step_handler(message, self.price_max)

    def distance_min(self, message: Message) -> None:
        """
        Функция - Отправляющая запрос на корректность введенных данных в функцию check_num.
        Если ответ корректный, запрашивает данные о максимальном расстоянии поиска, если нет,
        повторяет предыдущий запрос.

        :param message: Message
        :return: None
        """

        min_dist = check_num(message.text)
        if min_dist:
            user.set_user('min_distance', float(min_dist))
            self.bot.edit_message_text(
                chat_id=user.bot_message.chat.id, message_id=user.bot_message.message_id,
                text='Минимальное расстояние: {}'.format(message.text)
            )
            bot_message = self.bot.send_message(message.from_user.id, 'Введите максимальное расстояние в километрах:')
            user.set_user('bot_message', bot_message)
            self.bot.register_next_step_handler(message, self.distance_max)
        else:
            self.bot.send_message(message.from_user.id, 'Не корректный ввод. Расстояние должно быть целым числом,'
                                                        ' или числом в виде десятичной дроби!')
            self.bot.send_message(message.from_user.id, 'Введите минимальное расстояние (целое число, '
                                                        'или число в виде десятичной дроби):')
            self.bot.register_next_step_handler(message, self.distance_min)

    def distance_max(self, message: Message) -> None:
        """
        Функция - Отправляющая запрос на корректность введенных данных в функцию check_num. Если
        ответ корректный, совершается переход в функцию check_distance для проверки разницы расстояния
        (Чтобы минимальное расстояние, не было больше максимального), если нет, повторяется запрос
        о максимальном расстоянии.

        :param message: Message
        :return: None
        """

        max_dist = check_num(message.text)
        if max_dist:
            user.set_user('max_distance', float(max_dist))
            self.check_distance(message)
        else:
            self.bot.send_message(message.from_user.id, 'Не корректный ввод. Расстояние должно быть целым числом,'
                                                        ' или числом в виде десятичной дроби!')
            self.bot.send_message(message.from_user.id, 'Введите максимальное расстояние (целое число '
                                                        'или число в виде десятичной дроби):')
            self.bot.register_next_step_handler(message, self.distance_max)


    def count_hotel_bestdeal(self, message: Message) -> None:
        """
        Функция - предоставляющая пользователю выбрать количество отелей (от 1 до 10), в формате inline-кнопок.

        :param message: Message
        :return: None
        """
        bot_message = self.bot.send_message(
            message.from_user.id, 'Выберите, сколько отелей показать? ',
            reply_markup=self.keybords.set_count_hotels_and_photos()
        )
        user.set_user('bot_message', bot_message)

    def check_distance(self, message) -> None:
        """
        Функция - Проверяющая на корректность введённой информации пользователем о минимальном и максимальном расстоянии.
        (Чтобы минимальное расстояние, не было больше максимального) Если ответ корректный, возвращает в
         функцию для дальнейшего прохождения сценария. Eсли ответ не корректный,
        повторяется запрос о максимальном расстоянии.

        :param message: Message
        :return: None
        """
        if user.min_distance >= user.max_distance:
            self.bot.send_message(message.from_user.id, 'Не корректный ввод. Максимальное расстояние должно '
                                                        'быть больше минимального!')
            self.bot.send_message(message.from_user.id, 'Введите максимальное расстояние в километрах: ')
            self.bot.register_next_step_handler(message, self.distance_max)
        else:
            self.bot.edit_message_text(
                chat_id=user.bot_message.chat.id, message_id=user.bot_message.message_id,
                text='Максимальное расстояние: {}'.format(message.text)
            )
            self.count_hotel_bestdeal(message)


    def count_hotel(self, call: CallbackQuery) -> None:
        """
        Функция - предоставляющая пользователю выбрать количество отелей или фотографий (от 1 до 10)
        в формате inline-кнопок.

        :param call: CallbackQuery
        :return: None
        """
        bot_message = self.bot.send_message(
            call.from_user.id, 'Выберите сколько показать? ',
            reply_markup=self.keybords.set_count_hotels_and_photos()
        )
        user.set_user('bot_message', bot_message)


    def set_choice_photo(self, call: CallbackQuery):
        """
        Функция - уточняющая у пользователя необходимость вывода фотографий к отелям, в формате inline-кнопок.

        :param call: CallbackQuery
        :return: None
        """
        bot_message = self.bot.send_message(
            call.from_user.id, 'Желаете вывести фотографии к отелям? ',
            reply_markup=self.keybords.set_choice_photo()
        )
        user.set_user('bot_message', bot_message)


    def callback_count_hotels_and_photos(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-кнопок. Реагирует только на запросы о количестве отелей и количестве фотографий.
        Исходя из дефолтных данных у экземпляра класса UserHandle, направляет пользователя далее.
        Если аргумент 'count_hotel', имеет дефолтное значение (0), то переходим в функцию date_in, файла calendar,
        пакета keyboards. Если значение не равно нулю, то отправляет далее по сценарию в функцию
        'load_result'.

        :param call: CallbackQuery
        :return: None
        """
        self.bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        for nombers_list in call.message.json['reply_markup']['inline_keyboard']:
            for i_number in nombers_list:
                if i_number['callback_data'] == call.data:
                    if user.count_hotel == 0:
                        user.set_user('count_hotel', int(i_number['text']))
                        self.bot.edit_message_text(
                            chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text='Будет показано отелей: {}'.format(user.count_hotel)
                        )
                        self.date_in(call)

                    else:
                        user.set_user('count_photo', int(i_number['text']))
                        self.bot.edit_message_text(
                            chat_id=call.message.chat.id, message_id=call.message.message_id,
                            text='Будет показано фотографий: {}'.format(user.count_photo)
                        )
                        self.load_result(call)

    def date_in(self, call: CallbackQuery) -> None:
        """
        Функция - запрашивающая у пользователя минимальную дату для проживания в отеле.
        После запроса, для взаимодействия с пользователем, создаёт inline-календарь.

        :param call: CallbackQuery
        :return: None
        """
        calendar, step = CustomCalendar(
            calendar_id=0,
            locale='ru',
            min_date=date.today() + timedelta(days=1),
            max_date=date.today() + timedelta(days=180)
        ).build()
        self.bot.send_message(call.from_user.id, 'Уточните дату заезда:')
        bot_message = self.bot.send_message(call.from_user.id, f"Выберите {LSTEP[step]}:", reply_markup=calendar)
        user.set_user('bot_message', bot_message)


    def date_out(self, call: CallbackQuery, result: datetime) -> None:
        """
        Функция - запрашивающая у пользователя максимальную дату для проживания в отеле.
        После запроса,для взаимодействия с пользователем, создаёт inline-календарь.

        :param call: CallbackQuery
        :param result: datetime
        :return: None
        """
        min_date = result + timedelta(days=1)
        second_calendar, second_step = CustomCalendar(
            calendar_id=15,
            locale='ru',
            min_date=min_date,
            max_date=min_date + timedelta(days=180)
        ).build()
        self.bot.send_message(call.from_user.id, 'Уточните дату выезда из отеля:')
        bot_message = self.bot.send_message(
            call.from_user.id, f"Выберите {LSTEP[second_step]}:", reply_markup=second_calendar
        )
        user.set_user('bot_message', bot_message)



    def callback_first_calendar(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-календаря. Реагирует только на календарь с id = 0.
        После обработки пользовательской информации, перенаправляет в функцию date_out.

        :param call: CallbackQuery
        :return: None
        """
        result, key, step = CustomCalendar(
            calendar_id=0,
            locale='ru',
            min_date=date.today(),
            max_date=date.today() + timedelta(days=180)
        ).process(call.data)
        if not result and key:
            bot_message = self.bot.edit_message_text(
                f"Выберите {LSTEP[step]}:", call.message.chat.id, call.message.message_id, reply_markup=key
            )
            user.set_user('bot_message', bot_message)
        elif result:
            self.bot.edit_message_text(f"Дата заезда {result}", call.message.chat.id, call.message.message_id)
            user.set_user('date_in', result)
            print('date_in=', user)
            self.date_out(call, result)


    def callback_second_calendar(self, call: CallbackQuery) -> None:
        """
        Функция - обработчик inline-календаря. Реагирует только на календарь с id = 15.
        После обработки пользовательской информации, перенаправляет в функцию set_choice_photo.

        :param call: CallbackQuery
        :return: None
        """
        min_date = user.date_in + timedelta(days=1)
        result, key, step = CustomCalendar(
            calendar_id=15,
            locale='ru',
            min_date=min_date,
            max_date=min_date + timedelta(days=180)
        ).process(call.data)
        if not result and key:
            bot_message = self.bot.edit_message_text(
                f"Выберите {LSTEP[step]}:", call.message.chat.id, call.message.message_id, reply_markup=key
            )
            user.set_user('bot_message', bot_message)
        elif result:
            self.bot.edit_message_text(f"Дата выезда {result}", call.message.chat.id, call.message.message_id)
            day_period = int(str(result - user.date_in).split()[0])
            user.set_user('day_period', day_period)
            user.set_user('date_in', datetime.strftime(user.date_in, '%Y-%m-%d'))
            user.set_user('date_out', datetime.strftime(result, '%Y-%m-%d'))
            print('date_out=', user)
            self.set_choice_photo(call)

    def load_result(self, call: CallbackQuery) -> None:
        """
        Функция - записывающая последний аргумент в экземпляр класса UserHandle.
        Оповещает пользователя о выполнении загрузки. Проверяет, если пользователь выбирал команду 'bestdeal',
        то делает запрос к API (request_bestdeal), в противном случае делает запрос к API (request_property_list).
        Далее с ответом из API осуществляется переход в функцию 'request_hotels'.

        :param call: CallbackQuery
        :return: None
        """
        user.set_user('date_time', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))
        self.bot.send_message(call.from_user.id, 'Пожалуйста, подождите! Ищу информацию по отелям...')
        if user.command == 'bestdeal':
            response_hotels = request_bestdeal()
        else:
            response_hotels = request_property_list()
        self.request_hotels(call, response_hotels)

    def request_hotels(self, call: CallbackQuery, response_hotels: Response) -> None:
        """
        Функция - обрабатывающая ответ с API. Если статус код успешный, то создаётся запись в БД,
        о команде пользователя. Ответ с API десериализуется и проверяется в экземпляре пользователя введённая команда.
        Если команда 'bestdeal результат поиска дополнительно обрабатывается в функции 'bestdeal_logic'.
        И затем осуществляется переход в функцию showing_hotels. Если статус код ответа не успешный,
        то пользователю выдаётся сообщение об ошибке поиска.

        :param call: CallbackQuery
        :param response_hotels: Response
        :return: None
        """
        print(user.get_user())
        user_tuple = user.get_user()
        self.BD.insert_user(user_tuple)
        result_hotels = json.loads(response_hotels.text)['data']['body']['searchResults']['results']
        if user.command == 'bestdeal':
            result_hotels = bestdeal_logic(call, result_hotels, result=[])
            if result_hotels is False:
                bot_message = self.bot.send_message(call.from_user.id,
                                                    'К сожалению, по заданным критериям отели не найдены!'
                                                    '\nПопробуйте расширить диапазоны: цены и расстояния',
                                                    reply_markup=self.keybords.start_menu())
                user.set_user('bot_message', bot_message)
            else:
                self.showing_hotels(call, result_hotels)
        else:
            self.showing_hotels(call, result_hotels)

    def showing_hotels(self, call: CallbackQuery, result_hotels: Any) -> None:
        """
        Функция - выводит пользователю информацию по отелям. Подставляя данные по отелям в шаблон,
        в функции 'hotel_template'. Вывод осуществляется при условии, что пользователь отказался от вывода фото,
        в противном случае осуществляем переход в функцию 'showing_hotels_with_photo'.
        Так же, если вывод осущствлен, происходит запись данных об отеле в БД.

        :param call: CallbackQuery
        :param result_hotels: Any
        :return: None
        """
        if result_hotels:
            index = 0
            for hotel in result_hotels:
                if index == user.count_hotel:
                    self.bot.send_message(call.from_user.id, 'Поиск завершён')
                    bot_message = self.bot.send_message(
                        call.from_user.id, 'Для продолжения работы выберите команду',
                        reply_markup=self.keybords.button_start()
                    )
                    user.set_user('bot_message', bot_message)
                    break
                else:
                    hotel_show = hotel_template(currency=user.currency, days=user.day_period, hotel=hotel)
                    if hotel_show is not None:
                        index += 1
                        user_hotel = Hotel(call.from_user.id, hotel_show)
                        print('showing_hotels() user_hotel=', user_hotel, '  \nend')
                        print()
                        for i_elem in user_hotel.get_hotels():
                            print(i_elem)
                        print()
                        if user.count_photo != 0:
                            self.showing_hotels_with_photo(call, hotel, hotel_show, user_hotel)
                        else:
                            self.BD.insert_hotel(user_hotel.get_hotels())
                            self.bot.send_message(call.from_user.id, hotel_show, parse_mode='Markdown')
        else:
            bot_message = self.bot.send_message(call.from_user.id, 'К сожалению по заданным критериям отели не найдены!'
                                                     '\nПопробуйте расширить диапазоны: цены и расстояния',
                                                     reply_markup=self.keybords.start_menu())
            user.set_user('bot_message', bot_message)


    def showing_hotels_with_photo(self, call: CallbackQuery, hotel: Dict, hotel_show: str, user_hotel: Hotel) -> None:
        """
        Функция - вызываемая в случае, если пользователь указал наличие фотографий к отелям. Делается запрос к API.
        Если ответ с успешным статус-кодом, то дополнительно вызывается функция 'photo_append', из которой получаем список
        медиа-инпутов. Показ информации об отеле осуществляется медиа-группой. Так же в функции происходит
        сохранение инфо по отелю в БД.

        :param call: CallbackQuery
        :param hotel: Dict
        :param hotel_show: str
        :param user_hotel: Hotel
        :return: None
        """
        response_photo = request_get_photo(hotel['id'])
        if check_status_code(response_photo):
            result_photo = json.loads(response_photo.text)['hotelImages']
            media_massive, photo_str = photo_append(result_photo, hotel_show)
            self.bot.send_media_group(call.from_user.id, media=media_massive)
            user_hotel.photo = photo_str
            print('\nshowing_hotels_with_photo() user_hotel=', user_hotel, '  \nконец блока с фото\n')
            self.BD.insert_hotel(user_hotel.get_hotels())


    def handle(self):
        @self.bot.message_handler(func=lambda message: message.text == KEYBOARD['City'])
        def handle_lowprice(message):
            self.choice_city(message)

        # обработчик(декоратор) запросов от нажатия на Inline-кнопки .
        @self.bot.callback_query_handler(func=CustomCalendar.func(calendar_id=0))
        def run_first_calendar(call):
            self.callback_first_calendar(call)

        @self.bot.callback_query_handler(func=CustomCalendar.func(calendar_id=15))
        def run_second_calendar(call):
            self.callback_second_calendar(call)

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_inline(call):
            code = call.data
            if code.isdigit():
                self.callback_city(call)
            if code in CURRENCY_LIST:
                self.callback_currency(call)
            if code in CALLBACK_HOTELS_AND_PHOTOS:
                self.callback_count_hotels_and_photos(call)
            if code in YES_OR_NO_LIST:
                self.count_hotel(call)




