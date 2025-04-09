from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean
)

from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()

groups_lessons = Table(
    'groups_lessons',
    Base.metadata,
    Column('id',Integer, autoincrement=True, primary_key=True, unique=True, nullable=False),
    Column('group_id',Integer,ForeignKey('Name.groups.id'),primary_key=True),
    Column('lesson_id',Integer,ForeignKey('Name.lessons.id'),primary_key=True),
    schema='Name'
)

class Course(Base):
    __tablename__ = 'courses'
    __table_args__ = {'schema': 'Name'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)

    number = Column(Integer, unique=True, nullable=False)

    groups = relationship("Group", back_populates="course")

class Group(Base):
    __tablename__ = 'groups'
    __table_args__ = {'schema': 'Name'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)

    name = Column(String(10), unique=True, nullable=False)
    course_id = Column(Integer, ForeignKey("Name.courses.id"), nullable=False)

    course = relationship("Course", back_populates="groups")
    students = relationship("Student", back_populates="group")
    lessons = relationship("Lesson", secondary=groups_lessons, back_populates="groups")

class Student(Base):
    __tablename__ = 'students'
    __table_args__ = {'schema': 'Name'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)

    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    middle_name = Column(String(50))
    gender = Column(Boolean, nullable=False)
    group_id = Column(Integer, ForeignKey("Name.groups.id"), nullable=False)
    group = relationship("Group", back_populates="students")

class Lesson(Base):
    __tablename__ = 'lessons'
    __table_args__ = {'schema': 'Name'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)

    name = Column(String(100), unique=True, nullable=False)

    groups = relationship("Group", secondary=groups_lessons, back_populates="lessons")