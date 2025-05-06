from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Date,
    Float
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Проживающий(Base):
    __tablename__ = 'проживающие'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    фамилия = Column(String(100), nullable=False)
    имя = Column(String(100), nullable=False)
    отчество = Column(String(100))
    адрес_проживания = Column(String(255))
    телефон = Column(String(20))
    почта = Column(String(100))
    id_паспорта = Column(Integer, ForeignKey('Проект.паспорта.id'))
    паспорт = relationship("Паспорт", back_populates="проживающий")
    бронирования = relationship("Бронь", back_populates="проживающий")

class Паспорт(Base):
    __tablename__ = 'паспорта'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    серия = Column(String(10), nullable=False)
    номер = Column(String(20), nullable=False)
    выдан = Column(String(255), nullable=False)
    дата_выдачи = Column(Date, nullable=False)
    дата_рожд = Column(Date)
    место_рожд = Column(String(255))
    проживающий = relationship("Проживающий", back_populates="паспорт", uselist=False)

class Бронь(Base):
    __tablename__ = 'брони'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    id_проживающего = Column(Integer, ForeignKey('Проект.проживающие.id'), nullable=False)
    id_номера = Column(Integer, ForeignKey('Проект.номера.id'), nullable=False)
    дата_заезда = Column(Date, nullable=False)
    дата_выезда = Column(Date, nullable=False)
    дат_место = Column(String(100))
    завтрак = Column(Boolean, default=False)
    ужин = Column(Boolean, default=False)
    проживающий = relationship("Проживающий", back_populates="бронирования")
    номер = relationship("Номер", back_populates="бронирования")
    услуги = relationship("УслугаБрони", back_populates="бронь")

class Номер(Base):
    __tablename__ = 'номера'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    id_тип_номера = Column(Integer, ForeignKey('Проект.тип_номера.id'), nullable=False)
    колво_комнат = Column(Integer, nullable=False)
    колво_кроватей = Column(Integer, nullable=False)
    оснащение = Column(String(500))
    описание = Column(String(500))
    стоимость_сутки = Column(String(100))
    id_категории = Column(Integer, ForeignKey('Проект.категории.id'), nullable=False)
    тип_номера = relationship("ТипНомера", back_populates="номера")
    категория = relationship("Категория", back_populates="номера")
    бронирования = relationship("Бронь", back_populates="номер")

class УслугаБрони(Base):
    __tablename__ = 'услуги_брони'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    id_брони = Column(Integer, ForeignKey('Проект.брони.id'), nullable=False)
    id_услуги = Column(Integer, ForeignKey('Проект.услуги.id'), nullable=False)
    колво_услуги = Column(Integer, default=1)
    бронь = relationship("Бронь", back_populates="услуги")
    услуга = relationship("Услуга", back_populates="бронирования")

class Услуга(Base):
    __tablename__ = 'услуги'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    название = Column(String(100), nullable=False)
    описание = Column(String(500))
    цена = Column(String(100), nullable=False)
    бронирования = relationship("УслугаБрони", back_populates="услуга")

class ТипНомера(Base):
    __tablename__ = 'тип_номера'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    название = Column(String(100), nullable=False)
    номера = relationship("Номер", back_populates="тип_номера")

class Категория(Base):
    __tablename__ = 'категории'
    __table_args__ = {'schema': 'Проект'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    название = Column(String(100), nullable=False)
    номера = relationship("Номер", back_populates="категория")
