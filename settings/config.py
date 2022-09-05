import os
from dotenv import load_dotenv, find_dotenv


if not find_dotenv():
    exit('Файл .env отсутствует')
else:
    load_dotenv()


TOKEN = os.environ.get('Token')
API_KEY = os.environ.get('Rapid_API_KEY')


HEADERS = {
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com',
    'X-RapidAPI-Key': API_KEY
}


URL_search = 'https://hotels4.p.rapidapi.com/locations/v2/search'
URL_property_list = 'https://hotels4.p.rapidapi.com/properties/list'
URL_photo = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
URL_hotel = 'https://www.hotels.com/ho{}'


# название БД
NAME_DB = 'hotels.sqlite'
# версия приложения
VERSION = '0.0.1'
# автор приложния
AUTHOR = 'User'

# родительская директория
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# путь до базы данных
DATABASE = os.path.join('sqlite:///'+BASE_DIR, NAME_DB)



# кнопки управления
KEYBOARD = {
    'START': '\u25b6\ufe0f СТАРТ',
    'Lowprice': '\U00002198 Lowprice',
    'Highprice': '\U00002197 Highprice',
    'Bestdeal': '\U00002705 Bestdeal',
    'History': '\U0001F4D3 History',
    'HELP': '\u2753 Help',
    'SETTINGS': '\U0001F527 Settings',
    '<<': '⏪',
    '>>': '⏩',
    'CURRENCY': '\U0001f4b1 Currency',
    'LANG': 'Language',
    'LOOK': 'Просмотреть',
    'CLEAR': 'Очистить',
    'City': 'Выбор города'
}


# названия команд
COMMANDS = {
    'START': "start",
    'HELP': "help",
}


querystring_search_location = {
    'query': 'new_york',
    'locale': 'en_US',
    'currency': 'USD'
}
querystring_property_list = {
    'destinationId': '1509246',
    'pageNumber': '1',
    'pageSize': '25',
    'checkIn': '2022-08-08',
    'checkOut': '2022-08-18',
    'adults1': '1',
    'sortOrder': 'PRICE',
    'locale': 'en_US',
    'currency': 'USD'
}
querystring_for_bestdeal = {
    'destinationId': '1506446',
    'pageNumber': '1',
    'pageSize': '25',
    'checkIn': '2022-08-08',
    'checkOut': '2022-08-18',
    'adults1': '1',
    'priceMin': '50',
    'priceMax': '300',
    'sortOrder': 'DISTANCE_FROM_LANDMARK',
    'locale': 'en_US',
    'currency': 'USD'
}
querystring_photo = {'id': '474803'}

