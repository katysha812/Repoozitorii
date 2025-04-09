from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Group, Student, Lesson, groups_lessons, Course

DB_URI = "postgresql+psycopg2://postgres@localhost:5432/postgres"

engine = create_engine(DB_URI, connect_args={"options": "-csearch_path=Name"})

try:
    with engine.connect() as connection:
        print("Успех!")
except Exception as e:
    print (f"Ошибка подключения: {e}")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)