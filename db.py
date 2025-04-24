from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models2 import Base, Goal, Preference, User, WorkType, Workout, ExerciseType, ExerciseName, WorkoutExercise, MealType, Meal, Progress

DB_URI = "postgresql+psycopg2://postgres@localhost:5432/postgres?options=-csearch_path=PR"

engine = create_engine(DB_URI)

try:
    with engine.connect() as connection:
        print("Успешное подключение к базе данных!")
except Exception as e:
    print(f"Ошибка подключения: {e}")

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)