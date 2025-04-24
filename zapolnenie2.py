from datetime import date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models2 import Base, Goal, Preference, User, WorkType, Workout, ExerciseType, ExerciseName, WorkoutExercise, MealType, Meal, Progress

# Подключение к базе данных
engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres?options=-csearch_path=PR")
Session = sessionmaker(bind=engine)
session = Session()

try:
    # 1. Сначала создаем все таблицы
    Base.metadata.create_all(engine)
    print("Таблицы успешно созданы")

    # 2. Только потом очищаем их (если нужно)
    session.query(WorkoutExercise).delete()
    session.query(Workout).delete()
    session.query(ExerciseName).delete()
    session.query(ExerciseType).delete()
    session.query(WorkType).delete()
    session.query(Meal).delete()
    session.query(MealType).delete()
    session.query(Progress).delete()
    session.query(User).delete()
    session.query(Goal).delete()
    session.query(Preference).delete()
    session.commit()
    print("Таблицы очищены")

    # Заполнение таблицы целей (Goal)
    goals = [
        Goal(name="Похудение"),
        Goal(name="Набор мышечной массы"),
        Goal(name="Поддержание формы"),
        Goal(name="Подготовка к соревнованиям")
    ]
    session.add_all(goals)
    session.commit()

    # Заполнение таблицы предпочтений в питании (Preference)
    preferences = [
        Preference(name="Стандартное"),
        Preference(name="Вегетарианское"),
        Preference(name="Кето"),
        Preference(name="Палео"),
        Preference(name="Низкоуглеводное")
    ]
    session.add_all(preferences)
    session.commit()

    # Заполнение таблицы пользователей (User)
    users = [
        User(
            name="Иван Иванов",
            email="ivan@example.com",
            password="password123",
            gender=True,
            height=180,
            weightgoal=80.0,
            goal_id=2,  # Набор мышечной массы
            preference_id=1  # Стандартное
        ),
        User(
            name="Анна Петрова",
            email="anna@example.com",
            password="password456",
            gender=False,
            height=165,
            weightgoal=60.0,
            goal_id=1,  # Похудение
            preference_id=2  # Вегетарианское
        ),
        User(
            name="Сергей Сидоров",
            email="sergey@example.com",
            password="password789",
            gender=True,
            height=175,
            weightgoal=75.0,
            goal_id=3,  # Поддержание формы
            preference_id=3  # Кето
        )
    ]
    session.add_all(users)
    session.commit()

    # Заполнение таблицы типов тренировок (WorkType)
    work_types = [
        WorkType(name="Силовая тренировка"),
        WorkType(name="Кардио"),
        WorkType(name="Кроссфит"),
        WorkType(name="Йога"),
        WorkType(name="Плавание")
    ]
    session.add_all(work_types)
    session.commit()

    # Заполнение таблицы типов упражнений (ExerciseType)
    exercise_types = [
        ExerciseType(name="Грудь"),
        ExerciseType(name="Спина"),
        ExerciseType(name="Ноги"),
        ExerciseType(name="Плечи"),
        ExerciseType(name="Руки"),
        ExerciseType(name="Пресс"),
        ExerciseType(name="Кардио")
    ]
    session.add_all(exercise_types)
    session.commit()

    # Заполнение таблицы названий упражнений (ExerciseName)
    exercises = [
        ExerciseName(name="Жим штанги лежа", exercisetype_id=1),
        ExerciseName(name="Отжимания", exercisetype_id=1),
        ExerciseName(name="Подтягивания", exercisetype_id=2),
        ExerciseName(name="Тяга штанги в наклоне", exercisetype_id=2),
        ExerciseName(name="Приседания со штангой", exercisetype_id=3),
        ExerciseName(name="Выпады", exercisetype_id=3),
        ExerciseName(name="Жим гантелей сидя", exercisetype_id=4),
        ExerciseName(name="Подъем гантелей в стороны", exercisetype_id=4),
        ExerciseName(name="Подъем штанги на бицепс", exercisetype_id=5),
        ExerciseName(name="Отжимания на брусьях", exercisetype_id=5),
        ExerciseName(name="Скручивания", exercisetype_id=6),
        ExerciseName(name="Планка", exercisetype_id=6),
        ExerciseName(name="Бег на дорожке", exercisetype_id=7),
        ExerciseName(name="Велотренажер", exercisetype_id=7)
    ]
    session.add_all(exercises)
    session.commit()

    # Заполнение таблицы типов приема пищи (MealType)
    meal_types = [
        MealType(name="Завтрак"),
        MealType(name="Обед"),
        MealType(name="Ужин"),
        MealType(name="Перекус")
    ]
    session.add_all(meal_types)
    session.commit()

    # Заполнение таблицы тренировок (Workout)
    today = date.today()
    workouts = []
    for i in range(10):
        workout_date = today - timedelta(days=i)
        workouts.append(
            Workout(
                user_id=1 if i % 3 == 0 else 2 if i % 3 == 1 else 3,
                date=workout_date,
                time=45 + i*5,
                worktype_id=1 if i % 5 == 0 else 2 if i % 5 == 1 else 3 if i % 5 == 2 else 4,
            )
        )
    session.add_all(workouts)
    session.commit()

    # Заполнение таблицы связей тренировок и упражнений (WorkoutExercise)
    workout_exercises = []
    for i, workout in enumerate(session.query(Workout).all()):
        exercise_count = 3 + i % 4  # От 3 до 6 упражнений на тренировку
        for j in range(exercise_count):
            workout_exercises.append(
                WorkoutExercise(
                    workout_id=workout.id,
                    exercise_id=1 + (i + j) % 14,  # Всего 14 упражнений
                    sets=3 + j % 3,
                    reps=8 + j % 6,
                    weight=20 + j*5,
                    calories=300 + i*20
                )
            )
    session.add_all(workout_exercises)
    session.commit()

    # Заполнение таблицы приемов пищи (Meal)
    meals = []
    for i in range(15):
        meal_date = today - timedelta(days=i//3)
        meals.append(
            Meal(
                user_id=1 if i % 3 == 0 else 2 if i % 3 == 1 else 3,
                date=meal_date,
                mealtype_id=1 if i % 4 == 0 else 2 if i % 4 == 1 else 3,
                name=f"Прием пищи {i+1}",
                calories=400 + i*30,
                protein=30 + i*2,
                fat=15 + i,
                carbs=50 + i*3
            )
        )
    session.add_all(meals)
    session.commit()

    # Заполнение таблицы прогресса (Progress)
    progress_entries = []
    for i in range(10):
        progress_date = today - timedelta(days=i*3)
        progress_entries.append(
            Progress(
                user_id=1 if i % 3 == 0 else 2 if i % 3 == 1 else 3,
                weight=75.0 - i*0.5 if i % 3 == 0 else 60.0 - i*0.3 if i % 3 == 1 else 70.0 - i*0.4,
                date=progress_date,
                notes=f"Замеры за {progress_date.strftime('%d.%m.%Y')}"
            )
        )
    session.add_all(progress_entries)
    session.commit()

    print("Тестовые данные успешно добавлены!")

except Exception as e:
    session.rollback()
    print(f"Ошибка при добавлении тестовых данных: {e}")
finally:
    session.close() 