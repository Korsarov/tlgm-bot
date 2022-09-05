import requests
from requests import Response
from settings.config import HEADERS, URL_search, URL_property_list, URL_photo, \
    querystring_search_location, querystring_property_list, querystring_for_bestdeal, querystring_photo
import string
from telebot.types import Message
from models.users import user


def request_location(message: Message) -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/locations/v2/search'
    Проверяет введённые пользователем символы на ASCII кодировку, если так, то ищет с параметром locale en_US,
    в противном случае ищет с парметром locale ru_RU. Возвращает Response, содержащий в себе список городов.

    :param message: Message
    :return: Response
    """
    for sym in message.text:
        if sym not in string.printable:
            querystring_search_location['locale'] = 'ru_RU'
            break
    user.set_user('locale', querystring_search_location['locale'])
    querystring_search_location['query'] = message.text
    querystring_search_location['currency'] = user.currency
    response = requests.request('GET', URL_search, headers=HEADERS, params=querystring_search_location, timeout=15)
    print('querystring_search_location=', querystring_search_location)
    return response


def request_property_list() -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/properties/list'
    Предназначена для команд lowprice и highprice. В зависимости от введенной команды сортирует ответ
    по возврастанию цены, или же по убыванию. Возвращает Response, содержащий в себе список отелей в выбранном городе.

    :param
    :return: Response
    """
    if user.command == 'highprice':
        querystring_property_list['sortOrder'] = '-PRICE'
    querystring_property_list['destinationId'] = user.city_id
    querystring_property_list['checkIn'] = user.date_in
    querystring_property_list['checkOut'] = user.date_out
    querystring_property_list['currency'] = user.currency
    querystring_property_list['locale'] = user.locale
    response = requests.request('GET', URL_property_list, headers=HEADERS, params=querystring_property_list, timeout=15)
    print('querystring_property_list=', querystring_property_list)
    return response


def request_bestdeal() -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/properties/list'. Предназначена для
    команды bestdeal. Исключительность данной функции под функционал одной команды заключается в широкой
    установке параметров для поиска. Возвращает Response, содержащий в себе список отелей в выбранном городе.

    :param:
    :return: Response
    """
    querystring_for_bestdeal['destinationId'] = user.city_id
    querystring_for_bestdeal['checkIn'] = user.date_in
    querystring_for_bestdeal['checkOut'] = user.date_out
    querystring_for_bestdeal['priceMin'] = user.price_min
    querystring_for_bestdeal['priceMax'] = user.price_max
    querystring_for_bestdeal['currency'] = user.currency
    querystring_for_bestdeal['locale'] = user.locale
    response = requests.request('GET', URL_property_list, headers=HEADERS, params=querystring_for_bestdeal, timeout=15)
    print('querystring_for_bestdeal=', querystring_for_bestdeal)
    return response


def request_get_photo(hotel_id: int) -> Response:
    """
    Функция - делающая запрос на API по адресу: 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'.
    Вызывается при необходимости вывода фотографий к отелям. Возвращает Response, содержащий в себе список url
    фотографий отелей.

    :param hotel_id: int
    :return: Response
    """
    querystring_photo['id'] = hotel_id
    response = requests.request('GET', URL_photo, headers=HEADERS, params=querystring_photo, timeout=15)
    print('querystring_photo=', querystring_photo)
    return response
