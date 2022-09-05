# импортируем специальные типы телеграм бота для создания элементов интерфейса
from telebot.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, \
    InlineKeyboardButton, InlineKeyboardMarkup
# импортируем настройки и утилиты
from settings import config
# импортируем класс-менеджер для работы с библиотекой
from data_base.dbalchemy import DBManager
from settings.constants import COUNT_HOTELS_AND_PHOTO, LOOK_OR_CLEAR_LIST, FULL_OR_LAST_LIST


class Keyboards:
    """
    Класс Keyboards предназначен для создания и разметки интерфейса бота
    """
    # инициализация разметки

    def __init__(self):
        self.markup = None
        # инициализируем менеджер для работы с БД
        self.BD = DBManager()

    def set_btn(self, name):
        """
        Создает и возвращает кнопку по входным параметрам
        """
        return KeyboardButton(config.KEYBOARD[name])


    @staticmethod
    def remove_menu():
        """
        Удаляет меню
        """
        return ReplyKeyboardRemove()

    def button_start(self):
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn = self.set_btn('START')
        self.markup.row(itm_btn)
        return self.markup


    def start_menu(self):
        """
        Создает разметку кнопок в основном меню и возвращает разметку
        """
        self.markup = ReplyKeyboardMarkup(True, True)

        itm_btn_1 = self.set_btn('Lowprice')
        itm_btn_2 = self.set_btn('Highprice')
        itm_btn_3 = self.set_btn('Bestdeal')
        itm_btn_4 = self.set_btn('History')
        itm_btn_5 = self.set_btn('HELP')
        itm_btn_6 = self.set_btn('SETTINGS')

        # рассположение кнопок в меню
        self.markup.row(itm_btn_1, itm_btn_2, itm_btn_3)
        self.markup.row(itm_btn_5, itm_btn_4, itm_btn_6)
        return self.markup

    def lowprice_menu(self):
        """
        Создает разметку кнопок в меню 'Lowrice'
        """
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = KeyboardButton(config.KEYBOARD['<<'])
        itm_btn_2 = KeyboardButton(config.KEYBOARD['City'])

        # рассположение кнопок в меню
        self.markup.row(itm_btn_2)
        self.markup.row(itm_btn_1)
        return self.markup

    def highprice_menu(self):
        """
        Создает разметку кнопок в меню 'Highprice'
        """
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = KeyboardButton(config.KEYBOARD['<<'])
        # рассположение кнопок в меню
        self.markup.row(itm_btn_1)
        return self.markup

    def bestdeal_menu(self):
        """
        Создает разметку кнопок в меню 'bestdeal'
        """
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = KeyboardButton(config.KEYBOARD['<<'])
        itm_btn_2 = KeyboardButton(config.KEYBOARD['City'])

        # рассположение кнопок в меню
        self.markup.row(itm_btn_2)
        self.markup.row(itm_btn_1)
        return self.markup

    def history_menu(self):
        """
        Создает разметку кнопок в меню 'History'
        """
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = KeyboardButton(config.KEYBOARD['<<'])
        itm_btn_2 = KeyboardButton(config.KEYBOARD['LOOK'])
        itm_btn_3 = KeyboardButton(config.KEYBOARD['CLEAR'])

        # рассположение кнопок в меню
        self.markup.row(itm_btn_2, itm_btn_3)
        self.markup.row(itm_btn_1)
        return self.markup

    def look_or_clear_history(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру с меню раздела History.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup()

        keyboard_list = LOOK_OR_CLEAR_LIST
        for elem in keyboard_list:
            btm = InlineKeyboardButton(text=elem, callback_data=elem)
            self.markup.add(btm)
        return self.markup

    def full_or_last_history(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру с меню раздела History.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup()

        keyboard_list = FULL_OR_LAST_LIST
        for elem in keyboard_list:
            btm = InlineKeyboardButton(text=elem, callback_data=elem)
            self.markup.add(btm)
        return self.markup

    def help_menu(self):
        """
        Создает разметку кнопок в меню 'Help'
        """
        self.markup = ReplyKeyboardMarkup(True, True)
        itm_btn_1 = self.set_btn('<<')
        # рассположение кнопок в меню
        self.markup.row(itm_btn_1)
        return self.markup

    def settings_menu(self):
        """
        Создает разметку кнопок в меню 'Настройки'
        """
        self.markup = ReplyKeyboardMarkup(True, True)

        itm_btn_1 = self.set_btn('<<')
        itm_btn_2 = self.set_btn('CURRENCY')
        itm_btn_3 = self.set_btn('LANG')

        # рассположение кнопок в меню
        self.markup.row(itm_btn_2, itm_btn_3)
        self.markup.row(itm_btn_1)
        return self.markup


    def set_select_lang(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру со значениями валют.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup(row_width=3)
        btn_list = []
        for currency in ['ru_RU', 'en_EN']:
            btn = InlineKeyboardButton(text=currency, callback_data=currency)
            btn_list.append(btn)
        self.markup.add(btn_list[0], btn_list[1])
        return self.markup

    def set_select_currency(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру со значениями валют.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup(row_width=3)
        btn_list = []
        for currency in ['RUB', 'USD', 'EUR']:
            btn = InlineKeyboardButton(text=currency, callback_data=currency)
            btn_list.append(btn)
        self.markup.add(btn_list[0], btn_list[1], btn_list[2])
        return self.markup

    def set_select_city(self, city_list: list) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру с уточнением города поиска.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup(row_width=1)
        for city in city_list:
            btn = InlineKeyboardButton(text=city[1], callback_data=city[0])
            self.markup.add(btn)
        return self.markup

    def set_count_hotels_and_photos(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру с цифрами на кнопках от 1 до 10.
        Предназначена для запроса информации по количеству: отелей и фотографий

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup(row_width=5)
        btn_list = []

        for number in COUNT_HOTELS_AND_PHOTO:
            btn = InlineKeyboardButton(text=number[0], callback_data=number[1])
            btn_list.append(btn)
        self.markup.add(btn_list[0], btn_list[1], btn_list[2], btn_list[3], btn_list[4],
                     btn_list[5], btn_list[6], btn_list[7], btn_list[8], btn_list[9])
        return self.markup

    def set_choice_photo(self) -> InlineKeyboardMarkup:
        """
        Функция - создаёт inline-клавиатуру с уточнением вывода фото.

        :return: InlineKeyboardMarkup
        """
        self.markup = InlineKeyboardMarkup(row_width=2)
        yes = InlineKeyboardButton(text='Да', callback_data='Да')
        no = InlineKeyboardButton(text='Нет', callback_data='Нет')
        self.markup.add(yes, no)
        return self.markup
