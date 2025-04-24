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

# Данные для личного кабинета

class Goal(Base):  # Цели пользователей
    __tablename__ = 'goal'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)


class Preference(Base):  # Предпочтения в питании
    __tablename__ = 'preference'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)


class User(Base):  # Пользователи или основная информация для личного кабинета
    __tablename__ = 'user'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), unique=True, nullable=False)
    gender = Column(Boolean, nullable=False)
    height = Column(Integer, nullable=False)
    weightgoal = Column(Float, nullable=False)
    goal_id = Column(Integer, ForeignKey("PR.goal.id"), nullable=False)
    preference_id = Column(Integer, ForeignKey("PR.preference.id"), nullable=False)
    workouts = relationship("Workout", back_populates="user") 
    meals = relationship("Meal", back_populates="user")
    progress_entries = relationship("Progress", back_populates="user") 

# Отслеживание тренировок


class WorkType(Base):  # Типы тренировок
    __tablename__ = 'worktype'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    workouts = relationship("Workout", back_populates="worktype") 


class Workout(Base):  # Тренировки
    __tablename__ = 'workout'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("PR.user.id"), nullable=False)
    date = Column(Date, nullable=False)
    time = Column(Integer, nullable=False)
    worktype_id = Column(Integer, ForeignKey("PR.worktype.id"), nullable=False)

    exercise_associations = relationship("WorkoutExercise", back_populates="workout")
    user = relationship("User", back_populates="workouts") 
    worktype = relationship("WorkType", back_populates="workouts") 


class ExerciseType(Base):  # Типы упражнений
    __tablename__ = 'exercisetype'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False) 
    name = Column(String(100), unique=True, nullable=False)
    exercises = relationship("ExerciseName", back_populates="exercise_type") 


class ExerciseName(Base): #Название упражнений
    __tablename__ = 'exercisename'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    exercisetype_id = Column(Integer, ForeignKey('PR.exercisetype.id'), nullable=False)
    workout_associations = relationship("WorkoutExercise", back_populates="exercise")
    exercise_type = relationship("ExerciseType", back_populates="exercises") 


class WorkoutExercise(Base): #Упражнения тренировок
    __tablename__ = 'workout_exercise'
    __table_args__ = {'schema': 'PR'} 
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    workout_id = Column(Integer, ForeignKey('PR.workout.id'), nullable=False) 
    exercise_id = Column(Integer, ForeignKey('PR.exercisename.id'), nullable=False) 
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Integer)
    calories = Column(Float, nullable=False)
    workout = relationship("Workout", back_populates="exercise_associations")
    exercise = relationship("ExerciseName", back_populates="workout_associations")


class MealType(Base):  # Тип приема пищи
    __tablename__ = 'mealtype'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    name = Column(String(100), unique=True, nullable=False)
    meals = relationship("Meal", back_populates="meal_type") 

class Meal(Base):  # Приемы пищи
    __tablename__ = 'meal'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("PR.user.id"), nullable=False)
    date = Column(Date, nullable=False)
    mealtype_id = Column(Integer, ForeignKey("PR.mealtype.id"), nullable=False)
    name = Column(String(100), nullable=False) 
    calories = Column(Float, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbs = Column(Float, nullable=False)
    user = relationship("User", back_populates="meals")
    meal_type = relationship("MealType", back_populates="meals") 


class Progress(Base): #Прогресс
    __tablename__ = 'progress'
    __table_args__ = {'schema': 'PR'}
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("PR.user.id"), nullable=False)
    weight = Column(Float, nullable=False)
    date = Column(Date, nullable=False)
    notes = Column(String(100), nullable=False)
    user = relationship("User", back_populates="progress_entries")