# компоненты библиотеки для описания структуры таблицы
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from data_base.dbcore import Base
from sqlalchemy.orm import relationship, backref
from models.users import User_table



class Hotel:

    def __init__(self, user_id, hotel_info='', photo='', command_id=0) -> None:
        self.user_id: int = user_id
        self.hotel_info: str = hotel_info
        self.photo: str = photo
        self.command_id: int = command_id

    def get_hotels(self):
        return (
            self.user_id,
            self.hotel_info,
            self.photo,
            self.command_id,
        )
    def __repr__(self):
        info: str = 'user_id={user_id}, hotel_info={hotel_info}, photo={photo}, command_id={command_id} '.format(
            user_id=self.user_id,
            hotel_info=self.hotel_info,
            photo=self.photo,
            command_id=self.command_id,
        )
        return info

class Hotel_table(Base):
    """
    Класс-модель для описания таблицы "Hotel",
    основан на декларативном стиле SQLAlchemy
    """
    # название таблицы
    __tablename__ = 'hotels'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    hotel_info = Column(String)
    photo = Column(String)
    command_id = Column(Integer)


    # для каскадного удаления данных из таблицы
    users = relationship(
        User_table,
        backref=backref('hotels',
                        uselist=True,
                        cascade='delete,all'))



    def __str__(self):
        """
        Метод возвращает строковое представление объекта класса
        """
        return self.hotel_info