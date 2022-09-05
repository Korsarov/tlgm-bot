import re
import json
from telebot.types import InputMediaPhoto
from botrequests.request_main import request_bestdeal
from telebot.types import CallbackQuery
from typing import Dict, Optional, List, Tuple, Union
from settings.config import URL_hotel, querystring_for_bestdeal
from settings.constants import HOTEL_TEMPLATE_RU
from requests import Response
from models.users import user
import requests



def check_num(message: str) -> str:
    """
    Функция - Проверяющая на корректность введённой информации пользователем о максимальном расстоянии.
    В качестве корректного ответа от пользователя принимаются целые числа и числа с плавающей точкой
    (так же вместо точки обрабатывается запятая).

    :param message: str
    :return: str
    """
    float_pattern = r'\b[0-9]+[.,]?[0-9]+\b'
    int_pattern = r'\b[0-9]+\b'
    if [message] == re.findall(float_pattern, message) or [message] == re.findall(int_pattern, message):
        if ',' in message:
            dist = re.sub(r'[,]', '.', message)
        else:
            dist = message
        return dist

def bestdeal_logic(call: CallbackQuery, result_hotels: List[Dict], result: List) -> Union[List[Dict], bool]:
    """
    Функция - обрабатывающая десериализованный ответ с API. Проходит циклом по отелям и подбирает
    отель с подходящей удаленностью от центра. В случае, если не набралось необходимое количество отелей
    (Пользовательский выбор + 5 отелей запасных, в случае возникновения ошибок), то обращаемся к функции
    bestdeal_additional_request, для повторного запроса на следующей странице. Чтобы пользователь долго не ожидал
    инофрмацию, к API делается ещё два дополнительных запроса по отелям, если они не набирается необходимое
    количество отелей, то пользователь получает сообщение, что отели не найдены.

    :param call: CallbackQuery
    :param result_hotels: List[Dict]
    :param result: List
    :return: Union [List[Dict], bool]
    """
    for hotel in result_hotels:
        distance = re.sub(r'[\D+]', '', hotel['landmarks'][0]['distance'])
        if user.min_distance <= int(distance) <= user.max_distance:
            result.append(hotel)
    if len(result) < user.count_hotel + 5:
        querystring_for_bestdeal['pageNumber'] = int(querystring_for_bestdeal['pageNumber']) + 1
        if querystring_for_bestdeal['pageNumber'] == 4:
            return False
        else:
            bestdeal_additional_request(call, result)
    elif len(result) >= user.count_hotel + 5:
        querystring_for_bestdeal['pageNumber'] = 1
        return result

def bestdeal_additional_request(call: CallbackQuery, result) -> None:
    """
    Функция - обращается к файлу request_api, функции request_bestdeal.
    Полученный ответ от API, отправляет в bestdeal_logic

    :param call: CallbackQuery
    :param result: List[Dict]
    :return: None
    """
    response_hotels = request_bestdeal()
    result_hotels = json.loads(response_hotels.text)['data']['body']['searchResults']['results']
    bestdeal_logic(call, result_hotels, result)

def check_status_code(response: Response) -> Optional[bool]:
    """
    Функция - проверяет статус-код ответа. Если статус-код начинается на '2', то возвращает True,
    в противном случае пишет лог об ошибке.

    :param response: Response
    :return: Optional[bool]
    """
    if str(response.status_code).startswith('2'):
        return True
    else:
        return False

def hotel_template(currency: str, days: int, hotel: Dict) -> Optional[str]:
    """
    Функция - подставляющая параметры отеля в шаблон. Для выбора русскоязычного шаблона,
    или англоязычного, делается запрос в функцию 'locale_choice', которая и возаращает нужный шаблон.

    :param currency: str
    :param days: int
    :param hotel: Dict
    :return: Optional[str]
    """
    try:
        link = URL_hotel.format(hotel['id'])
        if currency == 'USD':
            price = float(hotel['ratePlan']['price']['current'][1:])
            print('price(usd)', price)
            cur_sym = '$'
            price_per_period = price * days
        elif currency == 'EUR':
            price = float(hotel['ratePlan']['price']['current'][:-2])
            print('price(eur)', price)
            cur_sym = '€'
            price_per_period = price * days
        else:
            price = hotel['ratePlan']['price']['current'][:-4]
            print('price(rub)', price)
            price_ru = re.sub(r'[,]', '', price)
            price_per_period = float(price_ru) * days
            cur_sym = 'RUB'
        name = hotel['name']
        address = hotel['address']['streetAddress']
        distance = hotel['landmarks'][0]['distance']
        star_rating = hotel['starRating']
        return HOTEL_TEMPLATE_RU.format(
            name, address, distance, price,
            cur_sym, price_per_period,
            cur_sym, star_rating, link
        )
    except KeyError:
        return None



def photo_append(result_photo: List, hotel_show: str) -> Tuple[List, str]:
    """
    Функция подготавливающая список с медиа-инпутами для медиа-группы.
    Так же проверяет запросы к фотографиям на наличие ошибки.
    :param result_photo: List
    :param hotel_show: str
    :return: tuple[List, str]
    """
    index = 0
    photo_str = ''
    media_massive = []
    for photo_dict in result_photo:
        if index == user.count_photo:
            return media_massive, photo_str
        else:
            photo_str += photo_dict['baseUrl'].format(size='y') + ' '
            photo = photo_dict['baseUrl'].format(size='y')
            response = requests.get(photo)
            if check_status_code(response):
                index += 1
                media_massive.append(
                    InputMediaPhoto(photo, caption=hotel_show if index == 1 else '', parse_mode='Markdown')
                )

# конвертирует список с p[(5,),(8,),...] к [5,8,...]
def _convert_in_list(list_convert):

    return [itm[0] for itm in list_convert]
