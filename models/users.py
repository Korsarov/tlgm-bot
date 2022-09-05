# компоненты библиотеки для описания структуры таблицы
from sqlalchemy import Column, String, Integer, Boolean, Float
# инициализация декларативного стиля
from data_base.dbcore import Base

from telebot.types import Message, CallbackQuery
from typing import Union


class User:

    def __init__(self, user_id=0, command='', currency='', locale='',
                 city='', city_id='', count_hotel=0, date_time='', date_in='', date_out='', day_period=0,
                 photo='', count_photo=0, min_distance=0, max_distance=0,
                 prise_min=0, price_max=0, bot_message: Union[Message, CallbackQuery] = '') -> None:
        self.user_id: int = user_id
        self.command: str = command
        self.currency: str = currency
        self.locale: str = locale
        self.city: str = city
        self.city_id: str = city_id
        self.count_hotel: int = count_hotel
        self.date_time: str = date_time
        self.date_in: str = date_in
        self.date_out: str = date_out
        self.day_period: int = day_period
        self.photo: str = photo
        self.count_photo: int = count_photo
        self.min_distance: float = min_distance
        self.max_distance: float = max_distance
        self.price_min: int = prise_min
        self.price_max: int = price_max
        self.bot_message = bot_message

    def set_user(self, key: str, value: Union[str, int, float]):
        self.__dict__[key] = value

    def get_user(self):
        return (
            self.user_id,
            self.command,
            self.city,
            self.currency,
            self.date_time,
            self.date_in,
            self.date_out,
            self.min_distance,
            self.max_distance,
            self.price_min,
            self.price_max
        )

    def __repr__(self):
        info: str = 'user_id={user_id}, command={command}, city={city}, currency={currency},' \
                     'date_time={date_time}, date_in={date_in}, date_out={date_out}, min_distance={min_distance}, ' \
                    'max_distance={max_distance}, price_min={price_min}, price_max={price_max}'.format(
            user_id=self.user_id,
            command=self.command,
            city=self.city,
            currency=self.currency,
            date_time= self.date_time,
            date_in=self.date_in,
            date_out=self.date_out,
            min_distance=self.min_distance,
            max_distance=self.max_distance,
            price_min=self.price_min,
            price_max=self.price_max
        )
        return info

user = User()

# print('users.get_users(users.py)=', user.get_user())
# print(user)

class User_table(Base):
    """
    Класс-модель для описания таблицы "User_table",
    основан на декларативном стиле SQLAlchemy
    """
    # название таблицы
    __tablename__ = 'users'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    command = Column(String)
    city = Column(String)
    currency = Column(String)
    date_time = Column(String)
    date_in = Column(String)
    date_out = Column(String)
    min_distance = Column(Float)
    max_distance = Column(Float)
    price_min = Column(Integer)
    price_max = Column(Integer)

    def __str__(self):
        """
        Метод возвращает строковое представление объекта класса
        """
        info: str = 'user_id={user_id}, command={command}, city={city}, currency={currency},' \
                    'date_time={date_time}, date_in={date_in}, date_out={date_out}, min_distance={min_distance}, ' \
                    'date_time={date_time}, date_in={date_in}, date_out={date_out}, min_distance={min_distance}, ' \
                    'max_distance={max_distance}, price_min={price_min}, price_max={price_max}'.format(
            user_id=self.user_id,
            command=self.command,
            city=self.city,
            currency=self.currency,
            date_time=self.date_time,
            date_in=self.date_in,
            date_out=self.date_out,
            min_distance=self.min_distance,
            max_distance=self.max_distance,
            price_min=self.price_min,
            price_max=self.price_max
        )
        return info

