from os import path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_base.dbcore import Base
from typing import List
from settings import config
from models.users import User_table
from models.hotels import Hotel_table


class Singleton(type):
    """
    Патерн Singleton предоставляет механизм создания одного
    и только одного объекта класса,
    и предоставление к нему глобальной точки доступа.
    """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls.__instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__call__(*args, **kwargs)
        return cls.__instance


class DBManager(metaclass=Singleton):
    """ 
    Класс-менеджер для работы с БД
    """

    def __init__(self):
        """
        Инициализация сесии и подключения к БД
        """
        self.engine = create_engine(config.DATABASE)
        session = sessionmaker(bind=self.engine)
        self._session = session()
        if not path.isfile(config.DATABASE):
            Base.metadata.create_all(self.engine)


    def close(self):
        """ Закрывает сессию """
        self._session.close()


    def insert_user(self, user_tuple: tuple) -> None:
        """
        Класс-метод записывающий данные пользователя в БД

                " command_time, user_id, command, city, currency, date_in, "
                "date_out, min_distance, max_distance, price_min, price_max) "

        :param user_tuple: tuple
        :return: None
        """

        user_table = User_table(
            user_id=user_tuple[0],
            command=user_tuple[1],
            city=user_tuple[2],
            currency=user_tuple[3],
            date_time=user_tuple[4],
            date_in=user_tuple[5],
            date_out=user_tuple[6],
            min_distance=user_tuple[7],
            max_distance=user_tuple[8],
            price_min=user_tuple[9],
            price_max=user_tuple[10]
        )
        self._session.add(user_table)
        self._session.commit()
        self.close()


    def insert_hotel(self, user_hotel) -> None:
        """
        Класс-метод записывающий данные отеля в БД
                "user_id, hotel_info, photo, command_id"

        :param user_hotel: Hotel
        :return: None
        """
        hotel_table = Hotel_table(
            user_id=user_hotel[0],
            hotel_info=user_hotel[1],
            photo=user_hotel[2],
            command_id=user_hotel[3]
        )
        self._session.add(hotel_table)
        self._session.commit()
        self.close()


    def delete_all_user_and_hotel(self, id_user):
        """
        Удаляет данные
        """
        self._session.query(User_table).filter_by(user_id=id_user).delete()
        self._session.query(Hotel_table).filter_by(user_id=id_user).delete()

        self._session.commit()
        self.close()


    def select_history_user_five(self, history_user: int) -> List[tuple]:
        """
        Класс-метод возвращающий из базы данных список кортежей с информацией по пользователю,
        отсортированной в обратном порядке для вывода последних пяти записей.

        :param history_user: int
        :return: List[tuple]
        """
        select_all_id = self._session.query(
            User_table.id,
            User_table.user_id,
            User_table.command,
            User_table.city,
            User_table.date_time,
            User_table.date_in,
            User_table.date_out
        ).filter_by(user_id=history_user).all()

        self._session.commit()
        self.close()
        return select_all_id


    def select_history_hotel(self, history_id: int) -> List[tuple]:
        """
        Класс-метод возвращающий из базы данных список кортежей с информацией по отелям,
        запрошенным ранее пользователем

        :param history_id: int
        :return: List[tuple]
        """
        select_all_id = self._session.query(
            Hotel_table.user_id,
            Hotel_table.hotel_info,
            Hotel_table.photo,
            Hotel_table.command_id
        ).filter_by(user_id=history_id).all()

        self._session.commit()
        self.close()
        return select_all_id

# my_id=193055125
# db_probe = DBManager()
# db_probe.delete_all_user_and_hotel(my_id)




