# компоненты библиотеки для описания структуры таблицы
from sqlalchemy import Column, String, Integer, ForeignKey
# импортируем модуль для связки таблиц
from sqlalchemy.orm import relationship, backref
# импортируем модель продуктов для связки моделей
from models.hotels import Hotel_table
from data_base.dbcore import Base



class Photo_table(Base):
    """
    Класс для создания таблицы "Заказ",
    основан на декларативном стиле SQLAlchemy
    """
    # название таблицы
    __tablename__ = 'photos'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    hotel_id = Column(Integer, ForeignKey('hotels.id'))
    photo = Column(String)

    # для каскадного удаления данных из таблицы
    hotels = relationship(
        Hotel_table,
        backref=backref('photos',
                        uselist=True,
                        cascade='delete,all'))

    def __str__(self):
        return f"{self.photo}"
