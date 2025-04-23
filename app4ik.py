from datetime import date
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
                            QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
                            QTabWidget, QTableWidget, QTableWidgetItem, QDialog,
                            QDateEdit, QComboBox, QFormLayout, QGroupBox)
from PyQt6.QtCore import Qt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models2 import Base, Goal, Preference, User, WorkType, Workout, ExerciseType, ExerciseName, WorkoutExercise, MealType, Meal, Progress
from sqlalchemy.orm import joinedload

engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/postgres?options=-csearch_path=PR")
Session = sessionmaker(bind=engine)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фитнес-трекер - Вход")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()

        # Поля для ввода
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Введите email")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Введите пароль")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопки
        self.login_btn = QPushButton("Войти")
        self.register_btn = QPushButton("Зарегистрироваться")

        # Группировка элементов
        form_group = QGroupBox("Вход в систему")
        form_layout = QVBoxLayout()
        form_layout.addWidget(QLabel("Email:"))
        form_layout.addWidget(self.email_edit)
        form_layout.addWidget(QLabel("Пароль:"))
        form_layout.addWidget(self.password_edit)
        form_layout.addWidget(self.login_btn)
        form_layout.addWidget(self.register_btn)
        form_group.setLayout(form_layout)

        layout.addWidget(form_group)
        self.setLayout(layout)

        # Подключение сигналов
        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.handle_register)

        # Для админского доступа
        self.admin_email = "admin@fitnesstracker.com"
        self.admin_password = "admin123"

    def handle_login(self):
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        # Проверка на админский доступ
        if email == self.admin_email and password == self.admin_password:
            self.admin_window = AdminWindow()
            self.admin_window.show()
            self.close()
            return

        with Session() as session:
            user = session.query(User).filter_by(email=email, password=password).first()
            if user:
                self.main_window = MainWindow(user)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный email или пароль!")

    def handle_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

class RegisterWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()

        # Поля для ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.height_edit = QLineEdit()
        self.weight_edit = QLineEdit()

        # Кнопка регистрации
        self.register_btn = QPushButton("Зарегистрироваться")

        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Подтвердите пароль:", self.confirm_password_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow(self.register_btn)

        layout.addLayout(form_layout)
        self.setLayout(layout)

        self.register_btn.clicked.connect(self.register_user)

    def register_user(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        confirm_password = self.confirm_password_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"

        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return

        if not all([name, email, password, confirm_password]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        with Session() as session:
            if session.query(User).filter_by(email=email).first():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                return

            new_user = User(
                name=name,
                email=email,
                password=password,
                gender=gender,
                height=height,
                weightgoal=weight,
                goal_id=3,  # Поддержание формы по умолчанию
                preference_id=1  # Стандартное питание по умолчанию
            )

            session.add(new_user)
            session.commit()
            QMessageBox.information(self, "Успех", "Регистрация прошла успешно!")
            self.close()

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Фитнес-трекер - {user.name}")
        self.setGeometry(100, 100, 800, 600)

        # Создаем вкладки
        self.tab_widget = QTabWidget()

        # Личный кабинет
        self.profile_tab = self.create_profile_tab()
        self.tab_widget.addTab(self.profile_tab, "Личный кабинет")

        # Тренировки
        self.workouts_tab = self.create_workouts_tab()
        self.tab_widget.addTab(self.workouts_tab, "Тренировки")

        # Питание
        self.meals_tab = self.create_meals_tab()
        self.tab_widget.addTab(self.meals_tab, "Питание")

        # Прогресс
        self.progress_tab = self.create_progress_tab()
        self.tab_widget.addTab(self.progress_tab, "Прогресс")

        self.setCentralWidget(self.tab_widget)

    def create_profile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Информация о пользователе
        info_group = QGroupBox("Информация о пользователе")
        info_layout = QFormLayout()

        self.name_label = QLabel(self.user.name)
        self.email_label = QLabel(self.user.email)
        self.gender_label = QLabel("Мужской" if self.user.gender else "Женский")
        self.height_label = QLabel(str(self.user.height))
        self.weight_goal_label = QLabel(str(self.user.weightgoal))

        info_layout.addRow("Имя:", self.name_label)
        info_layout.addRow("Email:", self.email_label)
        info_layout.addRow("Пол:", self.gender_label)
        info_layout.addRow("Рост (см):", self.height_label)
        info_layout.addRow("Целевой вес (кг):", self.weight_goal_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Кнопки управления профилем
        btn_layout = QHBoxLayout()
        self.edit_profile_btn = QPushButton("Редактировать профиль")
        self.delete_profile_btn = QPushButton("Удалить профиль")

        btn_layout.addWidget(self.edit_profile_btn)
        btn_layout.addWidget(self.delete_profile_btn)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.edit_profile_btn.clicked.connect(self.edit_profile)
        self.delete_profile_btn.clicked.connect(self.delete_profile)

        tab.setLayout(layout)
        return tab

    def create_workouts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица тренировок
        self.workouts_table = QTableWidget()
        self.workouts_table.setColumnCount(4)
        self.workouts_table.setHorizontalHeaderLabels(["Дата", "Тип тренировки", "Длительность (мин)", "Калории"])
        self.workouts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_workout_btn = QPushButton("Добавить")
        self.edit_workout_btn = QPushButton("Редактировать")
        self.delete_workout_btn = QPushButton("Удалить")
        self.view_exercises_btn = QPushButton("Просмотреть упражнения")

        btn_layout.addWidget(self.add_workout_btn)
        btn_layout.addWidget(self.edit_workout_btn)
        btn_layout.addWidget(self.delete_workout_btn)
        btn_layout.addWidget(self.view_exercises_btn)

        # Поиск
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по типу тренировки...")
        self.search_btn = QPushButton("Найти")

        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)
        layout.addWidget(self.workouts_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_workout_btn.clicked.connect(self.add_workout)
        self.edit_workout_btn.clicked.connect(self.edit_workout)
        self.delete_workout_btn.clicked.connect(self.delete_workout)
        self.view_exercises_btn.clicked.connect(self.view_exercises)
        self.search_btn.clicked.connect(self.search_workouts)

        # Загрузка данных
        self.load_workouts()

        tab.setLayout(layout)
        return tab

    def create_meals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Выбор даты
        date_layout = QHBoxLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setDate(date.today())  
        self.date_edit.setCalendarPopup(True)
        self.load_meals_btn = QPushButton("Загрузить")

        date_layout.addWidget(QLabel("Дата:"))
        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.load_meals_btn)

        # Таблица приемов пищи
        self.meals_table = QTableWidget()
        self.meals_table.setColumnCount(5)
        self.meals_table.setHorizontalHeaderLabels(["Тип", "Название", "Калории", "Белки", "Жиры", "Углеводы"])
        self.meals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_meal_btn = QPushButton("Добавить")
        self.edit_meal_btn = QPushButton("Редактировать")
        self.delete_meal_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_meal_btn)
        btn_layout.addWidget(self.edit_meal_btn)
        btn_layout.addWidget(self.delete_meal_btn)

        layout.addLayout(date_layout)
        layout.addWidget(self.meals_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.load_meals_btn.clicked.connect(self.load_meals)
        self.add_meal_btn.clicked.connect(self.add_meal)
        self.edit_meal_btn.clicked.connect(self.edit_meal)
        self.delete_meal_btn.clicked.connect(self.delete_meal)

        # Загрузка данных
        self.load_meals()

        tab.setLayout(layout)
        return tab

    def create_progress_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Текущий вес
        current_weight_group = QGroupBox("Текущий вес")
        current_weight_layout = QVBoxLayout()

        self.current_weight_label = QLabel()
        self.current_weight_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_weight_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        current_weight_layout.addWidget(self.current_weight_label)
        current_weight_group.setLayout(current_weight_layout)

        # Таблица прогресса
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(3)
        self.progress_table.setHorizontalHeaderLabels(["Дата", "Вес (кг)", "Заметки"])
        self.progress_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_progress_btn = QPushButton("Добавить")
        self.edit_progress_btn = QPushButton("Редактировать")
        self.delete_progress_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_progress_btn)
        btn_layout.addWidget(self.edit_progress_btn)
        btn_layout.addWidget(self.delete_progress_btn)

        layout.addWidget(current_weight_group)
        layout.addWidget(self.progress_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_progress_btn.clicked.connect(self.add_progress)
        self.edit_progress_btn.clicked.connect(self.edit_progress)
        self.delete_progress_btn.clicked.connect(self.delete_progress)

        # Загрузка данных
        self.load_progress()

        tab.setLayout(layout)
        return tab

    def edit_profile(self):
        self.edit_window = EditProfileWindow(self.user)
        if self.edit_window.exec():
            # Обновляем данные в интерфейсе
            with Session() as session:
                updated_user = session.query(User).get(self.user.id)
                self.user = updated_user

                self.name_label.setText(updated_user.name)
                self.email_label.setText(updated_user.email)
                self.gender_label.setText("Мужской" if updated_user.gender else "Женский")
                self.height_label.setText(str(updated_user.height))
                self.weight_goal_label.setText(str(updated_user.weightgoal))

    def delete_profile(self):
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить профиль? Это действие нельзя отменить.",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                user = session.query(User).get(self.user.id)
                session.delete(user)
                session.commit()

            QMessageBox.information(self, "Успех", "Профиль успешно удален!")
            self.close()
            self.login_window = LoginWindow()
            self.login_window.show()

    def load_workouts(self):
        with Session() as session:
            workouts = session.query(Workout).filter_by(user_id=self.user.id).all()
        self.workouts_table.setRowCount(len(workouts))

        for row, workout in enumerate(workouts):
            total_calories = sum(exercise.calories for exercise in workout.exercise_associations)

            self.workouts_table.setItem(row, 0, QTableWidgetItem(str(workout.date)))
            self.workouts_table.setItem(row, 1, QTableWidgetItem(str(workout.time)))
            self.workouts_table.setItem(row, 2, QTableWidgetItem(str(total_calories)))

    def add_workout(self):
        self.workout_window = WorkoutWindow(self.user)
        if self.workout_window.exec():
            self.load_workouts()

    def edit_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для редактирования!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.workout_window = WorkoutWindow(self.user, workout)
            if self.workout_window.exec():
                self.load_workouts()

    def delete_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту тренировку?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                workout = session.query(Workout).get(workout_id)
                session.delete(workout)
                session.commit()

            self.load_workouts()

    def view_exercises(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для просмотра упражнений!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.exercises_window = ExercisesWindow(workout)
            self.exercises_window.exec()

    def search_workouts(self):
        search_text = self.search_edit.text().strip().lower()

        with Session() as session:
            workouts = session.query(Workout).filter_by(user_id=self.user.id).all()

            self.workouts_table.setRowCount(0)
            for i, workout in enumerate(workouts):
                if search_text in workout.worktype.name.lower():
                    row = self.workouts_table.rowCount()
                    self.workouts_table.insertRow(row)
                    self.workouts_table.setItem(row, 0, QTableWidgetItem(workout.date.strftime("%d.%m.%Y")))
                    self.workouts_table.setItem(row, 1, QTableWidgetItem(workout.worktype.name))
                    self.workouts_table.setItem(row, 2, QTableWidgetItem(str(workout.time)))
                    self.workouts_table.setItem(row, 3, QTableWidgetItem(str(workout.calories)))
                    self.workouts_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, workout.id)

    def load_meals(self):
        selected_date = self.date_edit.date().toPyDate()

        with Session() as session:
            meals = session.query(Meal).filter_by(user_id=self.user.id, date=selected_date).all()

            self.meals_table.setRowCount(len(meals))
            for i, meal in enumerate(meals):
                self.meals_table.setItem(i, 0, QTableWidgetItem(meal.meal_type.name))
                self.meals_table.setItem(i, 1, QTableWidgetItem(meal.name))
                self.meals_table.setItem(i, 2, QTableWidgetItem(str(meal.calories)))
                self.meals_table.setItem(i, 3, QTableWidgetItem(str(meal.protein)))
                self.meals_table.setItem(i, 4, QTableWidgetItem(str(meal.fat)))
                self.meals_table.setItem(i, 5, QTableWidgetItem(str(meal.carbs)))
                self.meals_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, meal.id)

    def add_meal(self):
        selected_date = self.date_edit.date().toPyDate()
        self.meal_window = MealWindow(self.user, selected_date)
        if self.meal_window.exec():
            self.load_meals()

    def edit_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для редактирования!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            meal = session.query(Meal).get(meal_id)
            self.meal_window = MealWindow(self.user, meal.date, meal)
            if self.meal_window.exec():
                self.load_meals()

    def delete_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для удаления!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этот прием пищи?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                meal = session.query(Meal).get(meal_id)
                session.delete(meal)
                session.commit()

            self.load_meals()

    def load_progress(self):
        with Session() as session:
            progress_entries = session.query(Progress).filter_by(user_id=self.user.id).order_by(Progress.date.desc()).all()

            # Обновляем текущий вес
            if progress_entries:
                latest_weight = progress_entries[0].weight
                self.current_weight_label.setText(f"{latest_weight} кг")
            else:
                self.current_weight_label.setText("Нет данных")

            # Заполняем таблицу
            self.progress_table.setRowCount(len(progress_entries))
            for i, entry in enumerate(progress_entries):
                self.progress_table.setItem(i, 0, QTableWidgetItem(entry.date.strftime("%d.%m.%Y")))
                self.progress_table.setItem(i, 1, QTableWidgetItem(str(entry.weight)))
                self.progress_table.setItem(i, 2, QTableWidgetItem(entry.notes))
                self.progress_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, entry.id)

    def add_progress(self):
        self.progress_window = ProgressWindow(self.user)
        if self.progress_window.exec():
            self.load_progress()

    def edit_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            progress = session.query(Progress).get(progress_id)
            self.progress_window = ProgressWindow(self.user, progress)
            if self.progress_window.exec():
                self.load_progress()

    def delete_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту запись?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                progress = session.query(Progress).get(progress_id)
                session.delete(progress)
                session.commit()

            self.load_progress()

class EditProfileWindow(QDialog):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Редактирование профиля")
        self.setFixedSize(400, 400)

        layout = QVBoxLayout()

        # Поля для редактирования
        self.name_edit = QLineEdit(user.name)
        self.email_edit = QLineEdit(user.email)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.gender_combo.setCurrentIndex(0 if user.gender else 1)
        self.height_edit = QLineEdit(str(user.height))
        self.weight_edit = QLineEdit(str(user.weightgoal))
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Оставьте пустым, чтобы не менять")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow("Новый пароль:", self.password_edit)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_profile)
        self.cancel_btn.clicked.connect(self.reject)

    def save_profile(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"
        new_password = self.password_edit.text().strip()

        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return

        if not all([name, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        with Session() as session:
            # Проверяем, не занят ли email другим пользователем
            if email != self.user.email and session.query(User).filter_by(email=email).first():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                return

            user = session.query(User).get(self.user.id)
            user.name = name
            user.email = email
            user.gender = gender
            user.height = height
            user.weightgoal = weight

            if new_password:
                user.password = new_password

            session.commit()
            QMessageBox.information(self, "Успех", "Профиль успешно обновлен!")
            self.accept()

class WorkoutWindow(QDialog):
    def __init__(self, user, workout=None):
        super().__init__()
        self.user = user
        self.workout = workout
        self.setWindowTitle("Добавить тренировку" if not workout else "Редактировать тренировку")
        self.setFixedSize(600, 400)  # увеличьте размер окна, чтобы вместить таблицу с упражнениями

        layout = QVBoxLayout()

        # Поля для ввода
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.time_edit = QLineEdit()
        #self.calories_edit = QLineEdit() # Убираем поле для ввода калорий
        self.worktype_combo = QComboBox()

        # Заполняем комбобокс типами тренировок
        with Session() as session:
            work_types = session.query(WorkType).all()
            for wt in work_types:
                self.worktype_combo.addItem(wt.name, wt.id)

        # Если редактируем существующую тренировку, заполняем поля
        if workout:
            self.date_edit.setDate(workout.date)
            self.time_edit.setText(str(workout.time))
            #self.calories_edit.setText(str(workout.calories)) # Не нужно заполнять калории
            index = self.worktype_combo.findData(workout.worktype_id)
            if index >= 0:
                self.worktype_combo.setCurrentIndex(index)

        # Таблица для отображения упражнений
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(5)
        self.exercises_table.setHorizontalHeaderLabels(["Упражнение", "Подходы", "Повторения", "Вес (кг)", "Калории"])
        self.exercises_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Кнопки управления упражнениями
        exercise_btn_layout = QHBoxLayout()
        self.add_exercise_btn = QPushButton("Добавить упражнение")
        self.edit_exercise_btn = QPushButton("Редактировать упражнение")
        self.delete_exercise_btn = QPushButton("Удалить упражнение")
        exercise_btn_layout.addWidget(self.add_exercise_btn)
        exercise_btn_layout.addWidget(self.edit_exercise_btn)
        exercise_btn_layout.addWidget(self.delete_exercise_btn)

        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип тренировки:", self.worktype_combo)
        form_layout.addRow("Длительность (мин):", self.time_edit)
        #form_layout.addRow("Калории:", self.calories_edit) # удаляем возможность ручного ввода

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(form_layout)
        layout.addWidget(self.exercises_table)
        layout.addLayout(exercise_btn_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_workout)
        self.cancel_btn.clicked.connect(self.reject)
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        self.edit_exercise_btn.clicked.connect(self.edit_exercise)
        self.delete_exercise_btn.clicked.connect(self.delete_exercise)

        if workout:
            self.load_exercises()
            
    def add_exercise(self):
        self.exercise_window = ExerciseWindow(self.workout)
        if self.exercise_window.exec():
            self.load_exercises()
        
    def edit_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для редактирования!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            exercise = session.query(WorkoutExercise).get(exercise_id)
            self.exercise_window = ExerciseWindow(self.workout, exercise)
            if self.exercise_window.exec():
                self.load_exercises()

    def delete_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для удаления!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это упражнение?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                exercise = session.query(WorkoutExercise).get(exercise_id)
                session.delete(exercise)
                session.commit()

            self.load_exercises()

    def save_workout(self):
        date = self.date_edit.date().toPyDate()
        worktype_id = self.worktype_combo.currentData()

        try:
            time = int(self.time_edit.text())
            #calories = float(self.calories_edit.text()) # Не нужно считывать калории
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Длительность и калории должны быть числами!")
            return

        if not all([date, worktype_id, time]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
            
        with Session(engine) as session:
            if self.workout:
                # Редактируем существующую тренировку
                workout = session.query(Workout).get(self.workout.id)
                workout.date = date
                workout.time = time
                #workout.calories = calories # Не нужно сохранять калории
                workout.worktype_id = worktype_id
            else:
                # Создаем новую тренировку
                workout = Workout(
                    user_id=self.user.id,
                    date=date,
                    time=time,
                    worktype_id=worktype_id
                )
                session.add(workout)

            session.commit()
            self.workout = workout #Обновляем сессию
            QMessageBox.information(self, "Успех", "Тренировка сохранена!")
            self.accept()
    
    def load_exercises(self):
        with Session(engine) as session:
            if self.workout:
                workout = session.query(Workout).get(self.workout.id)
                exercises = workout.exercise_associations
           
                self.exercises_table.setRowCount(len(exercises))
                for i, exercise in enumerate(exercises):
                    self.exercises_table.setItem(i, 0, QTableWidgetItem(exercise.exercise.name))
                    self.exercises_table.setItem(i, 1, QTableWidgetItem(str(exercise.sets)))
                    self.exercises_table.setItem(i, 2, QTableWidgetItem(str(exercise.reps)))
                    self.exercises_table.setItem(i, 3, QTableWidgetItem(str(exercise.weight) if exercise.weight else "-"))
                    self.exercises_table.setItem(i, 4, QTableWidgetItem(str(exercise.calories) if exercise.calories else "-"))
                    self.exercises_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, exercise.id)

class ExerciseWindow(QDialog):
    def __init__(self, workout, exercise=None):
        super().__init__()
        self.workout = workout
        self.exercise = exercise
        self.setWindowTitle("Добавить упражнение" if not exercise else "Редактировать упражнение")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
   
        # Поля для ввода
        self.exercise_combo = QComboBox()
        self.sets_edit = QLineEdit()
        self.reps_edit = QLineEdit()
        self.weight_edit = QLineEdit()
        self.calories_edit = QLineEdit()
   
        # Заполняем комбобокс упражнениями
        with Session() as session:
            exercises = session.query(ExerciseName).all()
            for ex in exercises:
                self.exercise_combo.addItem(ex.name, ex.id)
   
        # Если редактируем существующее упражнение, заполняем поля
        if exercise:
            index = self.exercise_combo.findData(exercise.exercise_id)
            if index >= 0:
                self.exercise_combo.setCurrentIndex(index)
            self.sets_edit.setText(str(exercise.sets))
            self.reps_edit.setText(str(exercise.reps))
            if exercise.weight:
                self.weight_edit.setText(str(exercise.weight))
            if exercise.calories:
                self.calories_edit.setText(str(exercise.calories))
   
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
   
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Упражнение:", self.exercise_combo)
        form_layout.addRow("Подходы:", self.sets_edit)
        form_layout.addRow("Повторения:", self.reps_edit)
        form_layout.addRow("Вес (кг, опционально):", self.weight_edit)
        form_layout.addRow("Калории:", self.calories_edit)
   
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
   
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
   
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_exercise)
        self.cancel_btn.clicked.connect(self.reject)

    def save_exercise(self):
        exercise_id = self.exercise_combo.currentData()

        try:
            sets = int(self.sets_edit.text())
            reps = int(self.reps_edit.text())
            weight = float(self.weight_edit.text()) if self.weight_edit.text() else None
            calories = float(self.calories_edit.text()) if self.calories_edit.text() else None
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Поля должны содержать числа!")
            return

        if not all([exercise_id, sets, reps]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        if self.workout is None:
            QMessageBox.warning(self, "Ошибка", "Тренировка не выбрана!")
            return # or handle accordingly

        with Session() as session:
            if self.exercise:
                # Редактируем существующее упражнение
                exercise = session.query(WorkoutExercise).get(self.exercise.id)
                exercise.exercise_id = exercise_id
                exercise.sets = sets
                exercise.reps = reps
                exercise.weight = weight
                exercise.calories = calories
            else:
                # Создаем новое упражнение
                exercise = WorkoutExercise(
                    workout_id=self.workout.id,
                    exercise_id=exercise_id,
                    sets=sets,
                    reps=reps,
                    weight=weight,
                    calories=calories
                )
                session.add(exercise)

            session.commit()
            QMessageBox.information(self, "Успех", "Упражнение сохранено!")
            self.accept()

class ExercisesWindow(QDialog):
    def __init__(self, workout):
        super().__init__()
        self.workout = workout
        self.setWindowTitle(f"Упражнения для тренировки от {workout.date.strftime('%d.%m.%Y')}")
        self.setFixedSize(600, 400)

        layout = QVBoxLayout()

        # Таблица упражнений
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(5)
        self.exercises_table.setHorizontalHeaderLabels(["Упражнение", "Подходы", "Повторения", "Вес (кг)", "Калории"])
        self.exercises_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_exercise_btn = QPushButton("Добавить")
        self.edit_exercise_btn = QPushButton("Редактировать")
        self.delete_exercise_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_exercise_btn)
        btn_layout.addWidget(self.edit_exercise_btn)
        btn_layout.addWidget(self.delete_exercise_btn)

        layout.addWidget(self.exercises_table)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        self.edit_exercise_btn.clicked.connect(self.edit_exercise)
        self.delete_exercise_btn.clicked.connect(self.delete_exercise)

        # Загрузка данных
        self.load_exercises()

    def load_exercises(self):
        with Session(
        ) as session:
            workout = session.query(Workout).get(self.workout.id)
            exercises = workout.exercise_associations

            self.exercises_table.setRowCount(len(exercises))
            for i, exercise in enumerate(exercises):
                self.exercises_table.setItem(i, 0, QTableWidgetItem(exercise.exercise.name))
                self.exercises_table.setItem(i, 1, QTableWidgetItem(str(exercise.sets)))
                self.exercises_table.setItem(i, 2, QTableWidgetItem(str(exercise.reps)))
                self.exercises_table.setItem(i, 3, QTableWidgetItem(str(exercise.weight) if exercise.weight else "-"))
                self.exercises_table.setItem(i, 4, QTableWidgetItem(str(exercise.calories) if exercise.calories else "-"))
                self.exercises_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, exercise.id)
                
    def add_exercise(self):
        if not self.workout:
            QMessageBox.warning(self, "Ошибка", "Сначала сохраните тренировку!")
            return
        self.exercise_window = ExerciseWindow(self.workout)
        if self.exercise_window.exec_():
            self.load_exercises()

    def edit_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для редактирования!")
            return

        if not self.workout:
            QMessageBox.warning(self, "Ошибка", "Упражнения нельзя редактировать пока не сохранена тренировка")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session(engine) as session:
            exercise = session.query(WorkoutExercise).get(exercise_id)
            self.exercise_window = ExerciseWindow(self.workout, exercise)
            if self.exercise_window.exec_():
                self.load_exercises()
            
class MealWindow(QDialog):
    def __init__(self, user, meal_date, meal=None):
        super().__init__()
        self.user = user  # Сохраняем пользователя
        self.meal_date = meal_date
        self.meal = meal
        self.setWindowTitle("Добавить прием пищи" if not meal else "Редактировать прием пищи")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout()
   
        # Поля для ввода
        self.mealtype_combo = QComboBox()
        self.name_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.protein_edit = QLineEdit()
        self.fat_edit = QLineEdit()
        self.carbs_edit = QLineEdit()
   
        # Заполняем комбобокс типами приемов пищи
        with Session() as session:
            meal_types = session.query(MealType).all()
            for mt in meal_types:
                self.mealtype_combo.addItem(mt.name, mt.id)
   
        # Если редактируем существующий прием пищи, заполняем поля
        if meal:
            index = self.mealtype_combo.findData(meal.mealtype_id)
            if index >= 0:
                self.mealtype_combo.setCurrentIndex(index)
            self.name_edit.setText(meal.name)
            self.calories_edit.setText(str(meal.calories))
            self.protein_edit.setText(str(meal.protein))
            self.fat_edit.setText(str(meal.fat))
            self.carbs_edit.setText(str(meal.carbs))
   
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
   
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Тип приема пищи:", self.mealtype_combo)
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Калории:", self.calories_edit)
        form_layout.addRow("Белки (г):", self.protein_edit)
        form_layout.addRow("Жиры (г):", self.fat_edit)
        form_layout.addRow("Углеводы (г):", self.carbs_edit)
   
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
   
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
   
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_meal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_meal(self):
        mealtype_id = self.mealtype_combo.currentData()
        name = self.name_edit.text().strip()
   
        try:
            calories = float(self.calories_edit.text())
            protein = float(self.protein_edit.text())
            fat = float(self.fat_edit.text())
            carbs = float(self.carbs_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Все числовые поля должны содержать числа!")
            return
   
        if not all([mealtype_id, name, calories, protein, fat, carbs]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
   
        with Session() as session:
            if self.meal:
                # Редактируем существующий прием пищи
                meal = session.query(Meal).get(self.meal.id)
                meal.mealtype_id = mealtype_id
                meal.name = name
                meal.calories = calories
                meal.protein = protein
                meal.fat = fat
                meal.carbs = carbs
            else:
                # Создаем новый прием пищи
                meal = Meal(
                    user_id=self.user.id,
                    date=self.meal_date,
                    mealtype_id=mealtype_id,
                    name=name,
                    calories=calories,
                    protein=protein,
                    fat=fat,
                    carbs=carbs
                )
                session.add(meal)
            session.commit()
            QMessageBox.information(self, "Успех", "Прием пищи сохранен!")
            self.accept()
            
class ProgressWindow(QDialog):
    def __init__(self, user, progress=None):
        super().__init__()
        self.user = user
        self.progress = progress
        self.setWindowTitle("Добавить запись о прогрессе" if not progress else "Редактировать запись о прогрессе")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
   
        # Поля для ввода
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.weight_edit = QLineEdit()
        self.notes_edit = QLineEdit()
   
        # Если редактируем существующую запись, заполняем поля
        if progress:
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.weight_edit = QLineEdit()
            self.notes_edit = QLineEdit()

        # Если редактируем существующую запись, заполняем поля
        if progress:
            self.date_edit.setDate(progress.date)
            self.weight_edit.setText(str(progress.weight))
            self.notes_edit.setText(progress.notes)

        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Вес (кг):", self.weight_edit)
        form_layout.addRow("Заметки:", self.notes_edit)

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_progress)
        self.cancel_btn.clicked.connect(self.reject)

    def save_progress(self):
        date = self.date_edit.date().toPyDate()

        try:
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вес должен быть числом!")
            return

        notes = self.notes_edit.text().strip()

        if not all([date, weight]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        with Session() as session:
            if self.progress:
                # Редактируем существующую запись
                progress = session.query(Progress).get(self.progress.id)
                progress.date = date
                progress.weight = weight
                progress.notes = notes
            else:
                # Создаем новую запись
                progress = Progress(
                    user_id=self.user.id,
                    date=date,
                    weight=weight,
                    notes=notes
                )
                session.add(progress)

            session.commit()
            QMessageBox.information(self, "Успех", "Запись о прогрессе сохранена!")
            self.accept()

class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фитнес-трекер - Администратор")
        self.setGeometry(100, 100, 800, 600)

        # Создаем вкладки
        self.tab_widget = QTabWidget()

        # Добавляем все вкладки
        self.users_tab = self.create_users_tab()
        self.workouts_tab = self.create_workouts_tab()
        self.exercises_tab = self.create_exercises_tab()
        self.meals_tab = self.create_meals_tab()
        self.progress_tab = self.create_progress_tab()
        self.preferences_tab = self.create_preferences_tab()
        self.goals_tab = self.create_goals_tab()

        self.tab_widget.addTab(self.users_tab, "Пользователи")
        self.tab_widget.addTab(self.workouts_tab, "Тренировки")
        self.tab_widget.addTab(self.exercises_tab, "Упражнения")
        self.tab_widget.addTab(self.meals_tab, "Приемы пищи")
        self.tab_widget.addTab(self.progress_tab, "Прогресс")
        self.tab_widget.addTab(self.preferences_tab, "Предпочтения")
        self.tab_widget.addTab(self.goals_tab, "Цели")

        self.setCentralWidget(self.tab_widget)

        # Загрузка данных
        self.load_users()
        self.load_workouts_admin()
        self.load_exercises_admin()
        self.load_meals_admin()
        self.load_progress_admin()
        self.load_preferences()
        self.load_goals()
    def create_preferences_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Таблица предпочтений
        self.preferences_table = QTableWidget()
        self.preferences_table.setColumnCount(2)
        self.preferences_table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.preferences_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_preference_btn = QPushButton("Добавить")
        self.edit_preference_btn = QPushButton("Редактировать")
        self.delete_preference_btn = QPushButton("Удалить")
        
        btn_layout.addWidget(self.add_preference_btn)
        btn_layout.addWidget(self.edit_preference_btn)
        btn_layout.addWidget(self.delete_preference_btn)
        
        layout.addWidget(self.preferences_table)
        layout.addLayout(btn_layout)
        
        # Подключение сигналов
        self.add_preference_btn.clicked.connect(self.add_preference)
        self.edit_preference_btn.clicked.connect(self.edit_preference)
        self.delete_preference_btn.clicked.connect(self.delete_preference)
        
        tab.setLayout(layout)
        return tab

    def create_goals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Таблица целей
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(2)
        self.goals_table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.goals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_goal_btn = QPushButton("Добавить")
        self.edit_goal_btn = QPushButton("Редактировать")
        self.delete_goal_btn = QPushButton("Удалить")
        
        btn_layout.addWidget(self.add_goal_btn)
        btn_layout.addWidget(self.edit_goal_btn)
        btn_layout.addWidget(self.delete_goal_btn)
        
        layout.addWidget(self.goals_table)
        layout.addLayout(btn_layout)
        
        # Подключение сигналов
        self.add_goal_btn.clicked.connect(self.add_goal)
        self.edit_goal_btn.clicked.connect(self.edit_goal)
        self.delete_goal_btn.clicked.connect(self.delete_goal)
        
        tab.setLayout(layout)
        return tab
    
    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["Имя", "Email", "Пол", "Рост", "Целевой вес", "Цель"])
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Добавить")
        self.edit_user_btn = QPushButton("Редактировать")
        self.delete_user_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.edit_user_btn)
        btn_layout.addWidget(self.delete_user_btn)

        layout.addWidget(self.users_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_user_btn.clicked.connect(self.add_user)
        self.edit_user_btn.clicked.connect(self.edit_user)
        self.delete_user_btn.clicked.connect(self.delete_user)

        tab.setLayout(layout)
        return tab

    def create_workouts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица тренировок
        self.workouts_table = QTableWidget()
        self.workouts_table.setColumnCount(5)
        self.workouts_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Тип тренировки", "Длительность", "Калории"])
        self.workouts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_workout_btn = QPushButton("Добавить")
        self.edit_workout_btn = QPushButton("Редактировать")
        self.delete_workout_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_workout_btn)
        btn_layout.addWidget(self.edit_workout_btn)
        btn_layout.addWidget(self.delete_workout_btn)

        layout.addWidget(self.workouts_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_workout_btn.clicked.connect(self.add_workout)
        self.edit_workout_btn.clicked.connect(self.edit_workout)
        self.delete_workout_btn.clicked.connect(self.delete_workout)

        tab.setLayout(layout)
        return tab

    def create_exercises_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица упражнений
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(2)
        self.exercises_table.setHorizontalHeaderLabels(["Название", "Тип упражнения"])
        self.exercises_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_exercise_btn = QPushButton("Добавить")
        self.edit_exercise_btn = QPushButton("Редактировать")
        self.delete_exercise_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_exercise_btn)
        btn_layout.addWidget(self.edit_exercise_btn)
        btn_layout.addWidget(self.delete_exercise_btn)

        layout.addWidget(self.exercises_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        self.edit_exercise_btn.clicked.connect(self.edit_exercise)
        self.delete_exercise_btn.clicked.connect(self.delete_exercise)

        tab.setLayout(layout)
        return tab

    def create_meals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица приемов пищи
        self.meals_table = QTableWidget()
        self.meals_table.setColumnCount(8)
        self.meals_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Тип", "Название", "Калории", "Белки", "Жиры", "Углеводы"])
        self.meals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_meal_btn = QPushButton("Добавить")
        self.edit_meal_btn = QPushButton("Редактировать")
        self.delete_meal_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_meal_btn)
        btn_layout.addWidget(self.edit_meal_btn)
        btn_layout.addWidget(self.delete_meal_btn)

        layout.addWidget(self.meals_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_meal_btn.clicked.connect(self.add_meal)
        self.edit_meal_btn.clicked.connect(self.edit_meal)
        self.delete_meal_btn.clicked.connect(self.delete_meal)

        tab.setLayout(layout)
        return tab

    def create_progress_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица прогресса
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(4)
        self.progress_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Вес", "Заметки"])
        self.progress_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_progress_btn = QPushButton("Добавить")
        self.edit_progress_btn = QPushButton("Редактировать")
        self.delete_progress_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_progress_btn)
        btn_layout.addWidget(self.edit_progress_btn)
        btn_layout.addWidget(self.delete_progress_btn)

        layout.addWidget(self.progress_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_progress_btn.clicked.connect(self.add_progress)
        self.edit_progress_btn.clicked.connect(self.edit_progress)
        self.delete_progress_btn.clicked.connect(self.delete_progress)

        tab.setLayout(layout)
        return tab

    def load_preferences(self):
        with Session() as session:
            preferences = session.query(Preference).all()
            
            self.preferences_table.setRowCount(len(preferences))
            for i, pref in enumerate(preferences):
                self.preferences_table.setItem(i, 0, QTableWidgetItem(pref.name))
                self.preferences_table.setItem(i, 1, QTableWidgetItem(pref.description))
                self.preferences_table.item(i, 0).setData(Qt.UserRole, pref.id)

    def load_goals(self):
        with Session() as session:
            goals = session.query(Goal).all()
            
            self.goals_table.setRowCount(len(goals))
            for i, goal in enumerate(goals):
                self.goals_table.setItem(i, 0, QTableWidgetItem(goal.name))
                self.goals_table.setItem(i, 1, QTableWidgetItem(goal.description))
                self.goals_table.item(i, 0).setData(Qt.UserRole, goal.id)


    def load_users(self):
        with Session() as session:
            users = session.query(User).options(joinedload(User.goal)).all()
            
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(user.name))
                self.users_table.setItem(i, 1, QTableWidgetItem(user.email))
                self.users_table.setItem(i, 2, QTableWidgetItem("Мужской" if user.gender else "Женский"))
                self.users_table.setItem(i, 3, QTableWidgetItem(str(user.height)))
                self.users_table.setItem(i, 4, QTableWidgetItem(str(user.weightgoal)))
                
                # Safely get goal name
                goal_name = ""
                if hasattr(user, 'goal') and user.goal:
                    goal_name = user.goal.name
                self.users_table.setItem(i, 5, QTableWidgetItem(goal_name))
                
                self.users_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, user.id)

    def load_workouts_admin(self):
        with Session() as session:
            workouts = session.query(Workout).all()
           
            self.workouts_table.setRowCount(len(workouts))
            for i, workout in enumerate(workouts):
                self.workouts_table.setItem(i, 0, QTableWidgetItem(workout.user.name))
                self.workouts_table.setItem(i, 1, QTableWidgetItem(workout.date.strftime("%d.%m.%Y")))
                self.workouts_table.setItem(i, 2, QTableWidgetItem(workout.worktype.name))
                self.workouts_table.setItem(i, 3, QTableWidgetItem(str(workout.time)))
                
                # Суммируем калории из упражнений
                total_calories = sum(ex.calories for ex in workout.exercise_associations if ex.calories)
                self.workouts_table.setItem(i, 4, QTableWidgetItem(str(total_calories)))
                
                self.workouts_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, workout.id)

    def load_exercises_admin(self):
        with Session() as session:
            exercises = session.query(ExerciseName).all()
           
            self.exercises_table.setRowCount(len(exercises))
            for i, exercise in enumerate(exercises):
                self.exercises_table.setItem(i, 0, QTableWidgetItem(exercise.name))
                self.exercises_table.setItem(i, 1, QTableWidgetItem(exercise.exercisetype.name))
                self.exercises_table.item(i, 0).setData(Qt.UserRole, exercise.id)

    def load_meals_admin(self):
        with Session() as session:
            meals = session.query(Meal).all()
           
            self.meals_table.setRowCount(len(meals))
            for i, meal in enumerate(meals):
                self.meals_table.setItem(i, 0, QTableWidgetItem(meal.user.name))
                self.meals_table.setItem(i, 1, QTableWidgetItem(meal.date.strftime("%d.%m.%Y")))
                self.meals_table.setItem(i, 2, QTableWidgetItem(meal.meal_type.name))
                self.meals_table.setItem(i, 3, QTableWidgetItem(meal.name))
                self.meals_table.setItem(i, 4, QTableWidgetItem(str(meal.calories)))
                self.meals_table.setItem(i, 5, QTableWidgetItem(str(meal.protein)))
                self.meals_table.setItem(i, 6, QTableWidgetItem(str(meal.fat)))
                self.meals_table.setItem(i, 7, QTableWidgetItem(str(meal.carbs)))
                self.meals_table.item(i, 0).setData(Qt.UserRole, meal.id)

    def load_progress_admin(self):
        with Session() as session:
            progress_entries = session.query(Progress).all()
           
            self.progress_table.setRowCount(len(progress_entries))
            for i, entry in enumerate(progress_entries):
                self.progress_table.setItem(i, 0, QTableWidgetItem(entry.user.name))
                self.progress_table.setItem(i, 1, QTableWidgetItem(entry.date.strftime("%d.%m.%Y")))
                self.progress_table.setItem(i, 2, QTableWidgetItem(str(entry.weight)))
                self.progress_table.setItem(i, 3, QTableWidgetItem(entry.notes))
                self.progress_table.item(i, 0).setData(Qt.UserRole, entry.id)
                
    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals() 
            
    def add_user(self):
        self.user_window = UserAdminWindow()
        if self.user_window.exec():
            self.load_users()

    def edit_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            user = session.query(User).get(user_id)
            self.user_window = UserAdminWindow(user)
            if self.user_window.exec():
                self.load_users()

    def delete_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этого пользователя?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                user = session.query(User).get(user_id)
                session.delete(user)
                session.commit()
            
            self.load_users()
            
    def add_workout(self):
        self.workout_window = WorkoutWindowAdmin()
        if self.workout_window.exec():
            self.load_workouts_admin()

    def edit_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для редактирования!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.workout_window = WorkoutWindow(self.user, workout) #Удалите калории
            if self.workout_window.exec():
                self.load_workouts()

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.workout_window = WorkoutWindowAdmin(workout)
            if self.workout_window.exec():
                self.load_workouts_admin()

    def delete_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту тренировку?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                workout = session.query(Workout).get(workout_id)
                session.delete(workout)
                session.commit()

            self.load_workouts_admin()
            
    def add_exercise(self):
        self.exercise_window = ExerciseWindowAdmin()
        if self.exercise_window.exec():
            self.load_exercises_admin()

    def edit_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для редактирования!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            exercise = session.query(ExerciseName).get(exercise_id)
            self.exercise_window = ExerciseWindowAdmin(exercise)
            if self.exercise_window.exec():
                self.load_exercises_admin()

    def delete_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для удаления!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это упражнение?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                exercise = session.query(ExerciseName).get(exercise_id)
                session.delete(exercise)
                session.commit()

            self.load_exercises_admin()
            
    def add_meal(self):
        self.meal_window = MealWindowAdmin()
        if self.meal_window.exec():
            self.load_meals_admin()

    def edit_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для редактирования!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            meal = session.query(Meal).get(meal_id)
            self.meal_window = MealWindowAdmin(meal)
            if self.meal_window.exec():
                self.load_meals_admin()

    def delete_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для удаления!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этот прием пищи?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                meal = session.query(Meal).get(meal_id)
                session.delete(meal)
                session.commit()

            self.load_meals_admin()

    def add_progress(self):
        self.progress_window = ProgressWindowAdmin()
        if self.progress_window.exec():
            self.load_progress_admin()

    def edit_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            progress = session.query(Progress).get(progress_id)
            self.progress_window = ProgressWindowAdmin(progress)
            if self.progress_window.exec():
                self.load_progress_admin()

    def delete_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту запись?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                progress = session.query(Progress).get(progress_id)
                session.delete(progress)
                session.commit()

            self.load_progress_admin()

    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()

class UserAdminWindow(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Добавить пользователя" if not user else "Редактировать пользователя")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.height_edit = QLineEdit()
        self.weight_edit = QLineEdit()
        self.goal_combo = QComboBox()
        self.preference_combo = QComboBox()
        
        # Заполняем комбобоксы целей и предпочтений
        with Session() as session:
            goals = session.query(Goal).all()
            for goal in goals:
                self.goal_combo.addItem(goal.name, goal.id)
            
            preferences = session.query(Preference).all()
            for pref in preferences:
                self.preference_combo.addItem(pref.name, pref.id)
        
        # Если редактируем существующего пользователя, заполняем поля
        if user:
            self.name_edit.setText(user.name)
            self.email_edit.setText(user.email)
            self.gender_combo.setCurrentIndex(0 if user.gender else 1)
            self.height_edit.setText(str(user.height))
            self.weight_edit.setText(str(user.weightgoal))
            
            # Устанавливаем текущие цель и предпочтения
            index = self.goal_combo.findData(user.goal_id)
            if index >= 0:
                self.goal_combo.setCurrentIndex(index)
            
            index = self.preference_combo.findData(user.preference_id)
            if index >= 0:
                self.preference_combo.setCurrentIndex(index)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow("Цель:", self.goal_combo)
        form_layout.addRow("Предпочтение:", self.preference_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn.clicked.connect(self.reject)

    def save_user(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"
        goal_id = self.goal_combo.currentData()
        preference_id = self.preference_combo.currentData()
        
        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return
        
        if not all([name, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.user:
                # Редактируем существующего пользователя
                user = session.query(User).get(self.user.id)
                user.name = name
                user.email = email
                if password:
                    user.password = password
                user.gender = gender
                user.height = height
                user.weightgoal = weight
                user.goal_id = goal_id
                user.preference_id = preference_id
            else:
                # Создаем нового пользователя
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
                    return
                
                if session.query(User).filter_by(email=email).first():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                    return
                
                user = User(
                    name=name,
                    email=email,
                    password=password,
                    gender=gender,
                    height=height,
                    weightgoal=weight,
                    goal_id=goal_id,
                    preference_id=preference_id
                )
                session.add(user)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Пользователь сохранен!")
            self.accept()

class PreferenceWindowAdmin(QDialog):
    def __init__(self, preference=None):
        super().__init__()
        self.preference = preference
        self.setWindowTitle("Добавить предпочтение" if not preference else "Редактировать предпочтение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующее предпочтение, заполняем поля
        if preference:
            self.name_edit.setText(preference.name)
            self.description_edit.setText(preference.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_preference)
        self.cancel_btn.clicked.connect(self.reject)

    def save_preference(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.preference:
                # Редактируем существующее предпочтение
                preference = session.query(Preference).get(self.preference.id)
                preference.name = name
                preference.description = description
            else:
                # Создаем новое предпочтение
                preference = Preference(
                    name=name,
                    description=description
                )
                session.add(preference)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Предпочтение сохранено!")
            self.accept()

class GoalWindowAdmin(QDialog):
    def __init__(self, goal=None):
        super().__init__()
        self.goal = goal
        self.setWindowTitle("Добавить цель" if not goal else "Редактировать цель")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующую цель, заполняем поля
        if goal:
            self.name_edit.setText(goal.name)
            self.description_edit.setText(goal.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_goal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_goal(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.goal:
                # Редактируем существующую цель
                goal = session.query(Goal).get(self.goal.id)
                goal.name = name
                goal.description = description
            else:
                # Создаем новую цель
                goal = Goal(
                    name=name,
                    description=description
                )
                session.add(goal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Цель сохранена!")
            self.accept()

class WorkoutWindowAdmin(QDialog):
    def __init__(self, workout=None):
        super().__init__()
        self.workout = workout
        self.setWindowTitle("Добавить тренировку" if not workout else "Редактировать тренировку")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.time_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.worktype_combo = QComboBox()
       
        # Заполняем комбобоксы
        with Session() as session:
            # Пользователи
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
           
            # Типы тренировок
            work_types = session.query(WorkType).all()
            for wt in work_types:
                self.worktype_combo.addItem(wt.name, wt.id)
       
        # Если редактируем существующую тренировку, заполняем поля
        if workout:
            index = self.user_combo.findData(workout.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(workout.date)
            self.time_edit.setText(str(workout.time))
            self.calories_edit.setText(str(workout.calories))
            index = self.worktype_combo.findData(workout.worktype_id)
            if index >= 0:
                self.worktype_combo.setCurrentIndex(index)
       
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
       
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип тренировки:", self.worktype_combo)
        form_layout.addRow("Длительность (мин):", self.time_edit)
        form_layout.addRow("Калории:", self.calories_edit)
       
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
       
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
       
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_workout)
        self.cancel_btn.clicked.connect(self.reject)

    def save_workout(self):
        date = self.date_edit.date().toPyDate()
        worktype_id = self.worktype_combo.currentData()

        try:
            time = int(self.time_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Длительность должна быть числом!")
            return

        if not all([date, worktype_id, time]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        with Session() as session:
            if self.workout:
                # Редактируем существующую тренировку
                workout = session.query(Workout).get(self.workout.id)
                workout.date = date
                workout.time = time
                workout.worktype_id = worktype_id
            else:
                # Создаем новую тренировку
                workout = Workout(
                    user_id=self.user.id,
                    date=date,
                    time=time,
                    worktype_id=worktype_id
                )
                session.add(workout)
            
            session.commit()
            session.refresh(workout)  # Обновляем объект workout
            self.workout = workout  # Сохраняем обновленный объект
            
            QMessageBox.information(self, "Успех", "Тренировка сохранена!")
            self.load_exercises()  # Загружаем упражнения
            self.accept()

class ExerciseWindowAdmin(QDialog):
    def __init__(self, exercise=None):
        super().__init__()
        self.exercise = exercise
        self.setWindowTitle("Добавить упражнение" if not exercise else "Редактировать упражнение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.exercisetype_combo = QComboBox()
       
        # Заполняем комбобокс типами упражнений
        with Session() as session:
            exercisetypes = session.query(ExerciseType).all()
            for et in exercisetypes:
                self.exercisetype_combo.addItem(et.name, et.id)
       
        # Если редактируем существующее упражнение, заполняем поля
        if exercise:
            self.name_edit.setText(exercise.name)
            index = self.exercisetype_combo.findData(exercise.exercisetype_id)
            if index >= 0:
                self.exercisetype_combo.setCurrentIndex(index)
       
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
       
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Тип упражнения:", self.exercisetype_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_exercise)
        self.cancel_btn.clicked.connect(self.reject)

    def save_exercise(self):
        name = self.name_edit.text().strip()
        exercisetype_id = self.exercisetype_combo.currentData()
        
        if not all([name, exercisetype_id]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        with Session() as session:
            if self.exercise:
                # Редактируем существующее упражнение
                exercise = session.query(ExerciseName).get(self.exercise.id)
                exercise.name = name
                exercise.exercisetype_id = exercisetype_id
            else:
                # Создаем новое упражнение
                exercise = ExerciseName(
                    name=name,
                    exercisetype_id=exercisetype_id
                )
                session.add(exercise)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Упражнение сохранено!")
            self.accept()

class MealWindowAdmin(QDialog):
    def __init__(self, meal=None):
        super().__init__()
        self.meal = meal
        self.setWindowTitle("Добавить прием пищи" if not meal else "Редактировать прием пищи")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.mealtype_combo = QComboBox()
        self.name_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.protein_edit = QLineEdit()
        self.fat_edit = QLineEdit()
        self.carbs_edit = QLineEdit()
        
        # Заполняем комбобоксы
        with Session() as session:
            # Пользователи
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
            
            # Типы приемов пищи
            meal_types = session.query(MealType).all()
            for mt in meal_types:
                self.mealtype_combo.addItem(mt.name, mt.id)
        
        # Если редактируем существующий прием пищи, заполняем поля
        if meal:
            index = self.user_combo.findData(meal.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(meal.date)
            index = self.mealtype_combo.findData(meal.mealtype_id)
            if index >= 0:
                self.mealtype_combo.setCurrentIndex(index)
            self.name_edit.setText(meal.name)
            self.calories_edit.setText(str(meal.calories))
            self.protein_edit.setText(str(meal.protein))
            self.fat_edit.setText(str(meal.fat))
            self.carbs_edit.setText(str(meal.carbs))
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип приема пищи:", self.mealtype_combo)
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Калории:", self.calories_edit)
        form_layout.addRow("Белки (г):", self.protein_edit)
        form_layout.addRow("Жиры (г):", self.fat_edit)
        form_layout.addRow("Углеводы (г):", self.carbs_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_meal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_meal(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        mealtype_id = self.mealtype_combo.currentData()
        name = self.name_edit.text().strip()
        
        try:
            calories = float(self.calories_edit.text())
            protein = float(self.protein_edit.text())
            fat = float(self.fat_edit.text())
            carbs = float(self.carbs_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Все числовые поля должны содержать числа!")
            return
        
        if not all([user_id, date, mealtype_id, name, calories, protein, fat, carbs]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        with Session() as session:
            if self.meal:
                # Редактируем существующий прием пищи
                meal = session.query(Meal).get(self.meal.id)
                meal.user_id = user_id
                meal.date = date
                meal.mealtype_id = mealtype_id
                meal.name = name
                meal.calories = calories
                meal.protein = protein
                meal.fat = fat
                meal.carbs = carbs
            else:
                # Создаем новый прием пищи
                meal = Meal(
                    user_id=user_id,
                    date=date,
                    mealtype_id=mealtype_id,
                    name=name,
                    calories=calories,
                    protein=protein,
                    fat=fat,
                    carbs=carbs
                )
                session.add(meal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Прием пищи сохранен!")
            self.accept()

class ProgressWindowAdmin(QDialog):
    def __init__(self, progress=None):
        super().__init__()
        self.progress = progress
        self.setWindowTitle("Добавить запись о прогрессе" if not progress else "Редактировать запись о прогрессе")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.weight_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        
        # Заполняем комбобокс пользователями
        with Session() as session:
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
        
        # Если редактируем существующую запись, заполняем поля
        if progress:
            index = self.user_combo.findData(progress.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(progress.date)
            self.weight_edit.setText(str(progress.weight))
            self.notes_edit.setText(progress.notes)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Вес (кг):", self.weight_edit)
        form_layout.addRow("Заметки:", self.notes_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_progress)
        self.cancel_btn.clicked.connect(self.reject)

    def save_progress(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        
        try:
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вес должен быть числом!")
            return
        
        notes = self.notes_edit.text().strip()
        
        if not all([user_id, date, weight]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.progress:
                # Редактируем существующую запись
                progress = session.query(Progress).get(self.progress.id)
                progress.user_id = user_id
                progress.date = date
                progress.weight = weight
                progress.notes = notes
            else:
                # Создаем новую запись
                progress = Progress(
                    user_id=user_id,
                    date=date,
                    weight=weight,
                    notes=notes
                )
                session.add(progress)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Запись о прогрессе сохранена!")
            self.accept()

    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()
            
    def add_user(self):
        self.user_window = UserAdminWindow()
        if self.user_window.exec():
            self.load_users()

    def edit_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            user = session.query(User).get(user_id)
            self.user_window = UserAdminWindow(user)
            if self.user_window.exec():
                self.load_users()

    def delete_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этого пользователя?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                user = session.query(User).get(user_id)
                session.delete(user)
                session.commit()
            
            self.load_users()

    def add_workout(self):
        self.workout_window = WorkoutWindowAdmin()
        if self.workout_window.exec():
            self.load_workouts_admin()

    def edit_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для редактирования!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.workout_window = WorkoutWindowAdmin(workout)
            if self.workout_window.exec():
                self.load_workouts_admin()

    def delete_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту тренировку?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                workout = session.query(Workout).get(workout_id)
                session.delete(workout)
                session.commit()

            self.load_workouts_admin()
            
    def add_exercise(self):
        self.exercise_window = ExerciseWindowAdmin()
        if self.exercise_window.exec():
            self.load_exercises_admin()

    def edit_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для редактирования!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            exercise = session.query(ExerciseName).get(exercise_id)
            self.exercise_window = ExerciseWindowAdmin(exercise)
            if self.exercise_window.exec():
                self.load_exercises_admin()

    def delete_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для удаления!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это упражнение?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                exercise = session.query(ExerciseName).get(exercise_id)
                session.delete(exercise)
                session.commit()

            self.load_exercises_admin()
            
    def add_meal(self):
        self.meal_window = MealWindowAdmin()
        if self.meal_window.exec():
            self.load_meals_admin()

    def edit_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для редактирования!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            meal = session.query(Meal).get(meal_id)
            self.meal_window = MealWindowAdmin(meal)
            if self.meal_window.exec():
                self.load_meals_admin()

    def delete_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для удаления!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этот прием пищи?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                meal = session.query(Meal).get(meal_id)
                session.delete(meal)
                session.commit()

            self.load_meals_admin()

    def add_progress(self):
        self.progress_window = ProgressWindowAdmin()
        if self.progress_window.exec():
            self.load_progress_admin()

    def edit_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.UserRole)

        with Session() as session:
            progress = session.query(Progress).get(progress_id)
            self.progress_window = ProgressWindowAdmin(progress)
            if self.progress_window.exec():
                self.load_progress_admin()

    def delete_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту запись?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                progress = session.query(Progress).get(progress_id)
                session.delete(progress)
                session.commit()

            self.load_progress_admin()

    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()

class UserAdminWindow(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Добавить пользователя" if not user else "Редактировать пользователя")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.height_edit = QLineEdit()
        self.weight_edit = QLineEdit()
        self.goal_combo = QComboBox()
        self.preference_combo = QComboBox()
        
        # Заполняем комбобоксы целей и предпочтений
        with Session() as session:
            goals = session.query(Goal).all()
            for goal in goals:
                self.goal_combo.addItem(goal.name, goal.id)
            
            preferences = session.query(Preference).all()
            for pref in preferences:
                self.preference_combo.addItem(pref.name, pref.id)
        
        # Если редактируем существующего пользователя, заполняем поля
        if user:
            self.name_edit.setText(user.name)
            self.email_edit.setText(user.email)
            self.gender_combo.setCurrentIndex(0 if user.gender else 1)
            self.height_edit.setText(str(user.height))
            self.weight_edit.setText(str(user.weightgoal))
            
            # Устанавливаем текущие цель и предпочтения
            index = self.goal_combo.findData(user.goal_id)
            if index >= 0:
                self.goal_combo.setCurrentIndex(index)
            
            index = self.preference_combo.findData(user.preference_id)
            if index >= 0:
                self.preference_combo.setCurrentIndex(index)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow("Цель:", self.goal_combo)
        form_layout.addRow("Предпочтение:", self.preference_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn.clicked.connect(self.reject)

    def save_user(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"
        goal_id = self.goal_combo.currentData()
        preference_id = self.preference_combo.currentData()
        
        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return
        
        if not all([name, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.user:
                # Редактируем существующего пользователя
                user = session.query(User).get(self.user.id)
                user.name = name
                user.email = email
                if password:
                    user.password = password
                user.gender = gender
                user.height = height
                user.weightgoal = weight
                user.goal_id = goal_id
                user.preference_id = preference_id
            else:
                # Создаем нового пользователя
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
                    return
                
                if session.query(User).filter_by(email=email).first():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                    return
                
                user = User(
                    name=name,
                    email=email,
                    password=password,
                    gender=gender,
                    height=height,
                    weightgoal=weight,
                    goal_id=goal_id,
                    preference_id=preference_id
                )
                session.add(user)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Пользователь сохранен!")
            self.accept()

class PreferenceWindowAdmin(QDialog):
    def __init__(self, preference=None):
        super().__init__()
        self.preference = preference
        self.setWindowTitle("Добавить предпочтение" if not preference else "Редактировать предпочтение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующее предпочтение, заполняем поля
        if preference:
            self.name_edit.setText(preference.name)
            self.description_edit.setText(preference.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_preference)
        self.cancel_btn.clicked.connect(self.reject)

    def save_preference(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.preference:
                # Редактируем существующее предпочтение
                preference = session.query(Preference).get(self.preference.id)
                preference.name = name
                preference.description = description
            else:
                # Создаем новое предпочтение
                preference = Preference(
                    name=name,
                    description=description
                )
                session.add(preference)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Предпочтение сохранено!")
            self.accept()

class GoalWindowAdmin(QDialog):
    def __init__(self, goal=None):
        super().__init__()
        self.goal = goal
        self.setWindowTitle("Добавить цель" if not goal else "Редактировать цель")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующую цель, заполняем поля
        if goal:
            self.name_edit.setText(goal.name)
            self.description_edit.setText(goal.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_goal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_goal(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.goal:
                # Редактируем существующую цель
                goal = session.query(Goal).get(self.goal.id)
                goal.name = name
                goal.description = description
            else:
                # Создаем новую цель
                goal = Goal(
                    name=name,
                    description=description
                )
                session.add(goal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Цель сохранена!")
            self.accept()

class WorkoutWindowAdmin(QDialog):
    def __init__(self, workout=None):
        super().__init__()
        self.workout = workout
        self.setWindowTitle("Добавить тренировку" if not workout else "Редактировать тренировку")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.time_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.worktype_combo = QComboBox()
       
        # Заполняем комбобоксы
        with Session() as session:
            # Пользователи
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
           
            # Типы тренировок
            work_types = session.query(WorkType).all()
            for wt in work_types:
                self.worktype_combo.addItem(wt.name, wt.id)
       
        # Если редактируем существующую тренировку, заполняем поля
        if workout:
            index = self.user_combo.findData(workout.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(workout.date)
            self.time_edit.setText(str(workout.time))
            self.calories_edit.setText(str(workout.calories))
            index = self.worktype_combo.findData(workout.worktype_id)
            if index >= 0:
                self.worktype_combo.setCurrentIndex(index)
       
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
       
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип тренировки:", self.worktype_combo)
        form_layout.addRow("Длительность (мин):", self.time_edit)
        form_layout.addRow("Калории:", self.calories_edit)
       
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
       
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
       
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_workout)
        self.cancel_btn.clicked.connect(self.reject)

    def save_workout(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        worktype_id = self.worktype_combo.currentData()
       
        try:
            time = int(self.time_edit.text())
            calories = float(self.calories_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Длительность и калории должны быть числами!")
            return
       
        if not all([user_id, date, worktype_id, time, calories]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
       
        with Session() as session:
            if self.workout:
                # Редактируем существующую тренировку
                workout = session.query(Workout).get(self.workout.id)
                workout.user_id = user_id
                workout.date = date
                workout.time = time
                workout.calories = calories
                workout.worktype_id = worktype_id
            else:
                # Создаем новую тренировку
                workout = Workout(
                    user_id=user_id,
                    date=date,
                    time=time,
                    calories=calories,
                    worktype_id=worktype_id
                )
                session.add(workout)
           
            session.commit()
            QMessageBox.information(self, "Успех", "Тренировка сохранена!")
            self.accept()

class ExerciseWindowAdmin(QDialog):
    def __init__(self, exercise=None):
        super().__init__()
        self.exercise = exercise
        self.setWindowTitle("Добавить упражнение" if not exercise else "Редактировать упражнение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.exercisetype_combo = QComboBox()
       
        # Заполняем комбобокс типами упражнений
        with Session() as session:
            exercisetypes = session.query(ExerciseType).all()
            for et in exercisetypes:
                self.exercisetype_combo.addItem(et.name, et.id)
       
        # Если редактируем существующее упражнение, заполняем поля
        if exercise:
            self.name_edit.setText(exercise.name)
            index = self.exercisetype_combo.findData(exercise.exercisetype_id)
            if index >= 0:
                self.exercisetype_combo.setCurrentIndex(index)
class AdminWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Фитнес-трекер - Администратор")
        self.setGeometry(100, 100, 800, 600)

        # Создаем вкладки
        self.tab_widget = QTabWidget()

        # Добавляем все вкладки
        self.users_tab = self.create_users_tab()
        self.workouts_tab = self.create_workouts_tab()
        self.exercises_tab = self.create_exercises_tab()
        self.meals_tab = self.create_meals_tab()
        self.progress_tab = self.create_progress_tab()
        self.preferences_tab = self.create_preferences_tab()
        self.goals_tab = self.create_goals_tab()

        self.tab_widget.addTab(self.users_tab, "Пользователи")
        self.tab_widget.addTab(self.workouts_tab, "Тренировки")
        self.tab_widget.addTab(self.exercises_tab, "Упражнения")
        self.tab_widget.addTab(self.meals_tab, "Приемы пищи")
        self.tab_widget.addTab(self.progress_tab, "Прогресс")
        self.tab_widget.addTab(self.preferences_tab, "Предпочтения")
        self.tab_widget.addTab(self.goals_tab, "Цели")

        self.setCentralWidget(self.tab_widget)

        # Загрузка данных
        self.load_users()
        self.load_workouts_admin()
        self.load_exercises_admin()
        self.load_meals_admin()
        self.load_progress_admin()
        self.load_preferences()
        self.load_goals()
    def create_preferences_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Таблица предпочтений
        self.preferences_table = QTableWidget()
        self.preferences_table.setColumnCount(2)
        self.preferences_table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.preferences_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_preference_btn = QPushButton("Добавить")
        self.edit_preference_btn = QPushButton("Редактировать")
        self.delete_preference_btn = QPushButton("Удалить")
        
        btn_layout.addWidget(self.add_preference_btn)
        btn_layout.addWidget(self.edit_preference_btn)
        btn_layout.addWidget(self.delete_preference_btn)
        
        layout.addWidget(self.preferences_table)
        layout.addLayout(btn_layout)
        
        # Подключение сигналов
        self.add_preference_btn.clicked.connect(self.add_preference)
        self.edit_preference_btn.clicked.connect(self.edit_preference)
        self.delete_preference_btn.clicked.connect(self.delete_preference)
        
        tab.setLayout(layout)
        return tab

    def create_goals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Таблица целей
        self.goals_table = QTableWidget()
        self.goals_table.setColumnCount(2)
        self.goals_table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.goals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_goal_btn = QPushButton("Добавить")
        self.edit_goal_btn = QPushButton("Редактировать")
        self.delete_goal_btn = QPushButton("Удалить")
        
        btn_layout.addWidget(self.add_goal_btn)
        btn_layout.addWidget(self.edit_goal_btn)
        btn_layout.addWidget(self.delete_goal_btn)
        
        layout.addWidget(self.goals_table)
        layout.addLayout(btn_layout)
        
        # Подключение сигналов
        self.add_goal_btn.clicked.connect(self.add_goal)
        self.edit_goal_btn.clicked.connect(self.edit_goal)
        self.delete_goal_btn.clicked.connect(self.delete_goal)
        
        tab.setLayout(layout)
        return tab
    
    def create_users_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица пользователей
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["Имя", "Email", "Пол", "Рост", "Целевой вес", "Цель"])
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Добавить")
        self.edit_user_btn = QPushButton("Редактировать")
        self.delete_user_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_user_btn)
        btn_layout.addWidget(self.edit_user_btn)
        btn_layout.addWidget(self.delete_user_btn)

        layout.addWidget(self.users_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_user_btn.clicked.connect(self.add_user)
        self.edit_user_btn.clicked.connect(self.edit_user)
        self.delete_user_btn.clicked.connect(self.delete_user)

        tab.setLayout(layout)
        return tab

    def create_workouts_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица тренировок
        self.workouts_table = QTableWidget()
        self.workouts_table.setColumnCount(5)
        self.workouts_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Тип тренировки", "Длительность", "Калории"])
        self.workouts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_workout_btn = QPushButton("Добавить")
        self.edit_workout_btn = QPushButton("Редактировать")
        self.delete_workout_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_workout_btn)
        btn_layout.addWidget(self.edit_workout_btn)
        btn_layout.addWidget(self.delete_workout_btn)

        layout.addWidget(self.workouts_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_workout_btn.clicked.connect(self.add_workout)
        self.edit_workout_btn.clicked.connect(self.edit_workout)
        self.delete_workout_btn.clicked.connect(self.delete_workout)

        tab.setLayout(layout)
        return tab

    def create_exercises_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица упражнений
        self.exercises_table = QTableWidget()
        self.exercises_table.setColumnCount(2)
        self.exercises_table.setHorizontalHeaderLabels(["Название", "Тип упражнения"])
        self.exercises_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_exercise_btn = QPushButton("Добавить")
        self.edit_exercise_btn = QPushButton("Редактировать")
        self.delete_exercise_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_exercise_btn)
        btn_layout.addWidget(self.edit_exercise_btn)
        btn_layout.addWidget(self.delete_exercise_btn)

        layout.addWidget(self.exercises_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_exercise_btn.clicked.connect(self.add_exercise)
        self.edit_exercise_btn.clicked.connect(self.edit_exercise)
        self.delete_exercise_btn.clicked.connect(self.delete_exercise)

        tab.setLayout(layout)
        return tab

    def create_meals_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица приемов пищи
        self.meals_table = QTableWidget()
        self.meals_table.setColumnCount(8)
        self.meals_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Тип", "Название", "Калории", "Белки", "Жиры", "Углеводы"])
        self.meals_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_meal_btn = QPushButton("Добавить")
        self.edit_meal_btn = QPushButton("Редактировать")
        self.delete_meal_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_meal_btn)
        btn_layout.addWidget(self.edit_meal_btn)
        btn_layout.addWidget(self.delete_meal_btn)

        layout.addWidget(self.meals_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_meal_btn.clicked.connect(self.add_meal)
        self.edit_meal_btn.clicked.connect(self.edit_meal)
        self.delete_meal_btn.clicked.connect(self.delete_meal)

        tab.setLayout(layout)
        return tab

    def create_progress_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Таблица прогресса
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(4)
        self.progress_table.setHorizontalHeaderLabels(["Пользователь", "Дата", "Вес", "Заметки"])
        self.progress_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.add_progress_btn = QPushButton("Добавить")
        self.edit_progress_btn = QPushButton("Редактировать")
        self.delete_progress_btn = QPushButton("Удалить")

        btn_layout.addWidget(self.add_progress_btn)
        btn_layout.addWidget(self.edit_progress_btn)
        btn_layout.addWidget(self.delete_progress_btn)

        layout.addWidget(self.progress_table)
        layout.addLayout(btn_layout)

        # Подключение сигналов
        self.add_progress_btn.clicked.connect(self.add_progress)
        self.edit_progress_btn.clicked.connect(self.edit_progress)
        self.delete_progress_btn.clicked.connect(self.delete_progress)

        tab.setLayout(layout)
        return tab

    def load_preferences(self):
        with Session() as session:
            preferences = session.query(Preference).all()
            
            self.preferences_table.setRowCount(len(preferences))
            for i, pref in enumerate(preferences):
                self.preferences_table.setItem(i, 0, QTableWidgetItem(pref.name))
                self.preferences_table.setItem(i, 1, QTableWidgetItem(pref.description))
                self.preferences_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, pref.id)

    def load_goals(self):
        with Session() as session:
            goals = session.query(Goal).all()
            
            self.goals_table.setRowCount(len(goals))
            for i, goal in enumerate(goals):
                self.goals_table.setItem(i, 0, QTableWidgetItem(goal.name))
                self.goals_table.setItem(i, 1, QTableWidgetItem(goal.description))
                self.goals_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, goal.id)


    def load_users(self):
        with Session() as session:
            users = session.query(User).all()
           
            self.users_table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(user.name))
                self.users_table.setItem(i, 1, QTableWidgetItem(user.email))
                self.users_table.setItem(i, 2, QTableWidgetItem("Мужской" if user.gender else "Женский"))
                self.users_table.setItem(i, 3, QTableWidgetItem(str(user.height)))
                self.users_table.setItem(i, 4, QTableWidgetItem(str(user.weightgoal)))
                self.users_table.setItem(i, 5, QTableWidgetItem(user.goal.name if user.goal else ""))
                self.users_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, user.id)

    def load_workouts_admin(self):
        with Session() as session:
            workouts = session.query(Workout).all()
           
            self.workouts_table.setRowCount(len(workouts))
            for i, workout in enumerate(workouts):
                self.workouts_table.setItem(i, 0, QTableWidgetItem(workout.user.name))
                self.workouts_table.setItem(i, 1, QTableWidgetItem(workout.date.strftime("%d.%m.%Y")))
                self.workouts_table.setItem(i, 2, QTableWidgetItem(workout.worktype.name))
                self.workouts_table.setItem(i, 3, QTableWidgetItem(str(workout.time)))
                
                # Суммируем калории из упражнений
                total_calories = sum(ex.calories for ex in workout.exercise_associations if ex.calories)
                self.workouts_table.setItem(i, 4, QTableWidgetItem(str(total_calories)))
                
                self.workouts_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, workout.id)

    def load_exercises_admin(self):
        with Session() as session:
            exercises = session.query(ExerciseName).all()
           
            self.exercises_table.setRowCount(len(exercises))
            for i, exercise in enumerate(exercises):
                self.exercises_table.setItem(i, 0, QTableWidgetItem(exercise.name))
                self.exercises_table.setItem(i, 1, QTableWidgetItem(exercise.exercisetype.name))
                self.exercises_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, exercise.id)

    def load_meals(self):
        selected_date = self.date_edit.date().toPyDate()

        with Session() as session:
            meals = session.query(Meal).filter_by(user_id=self.user.id, date=selected_date).all()

            self.meals_table.setRowCount(len(meals))
            for i, meal in enumerate(meals):
                self.meals_table.setItem(i, 0, QTableWidgetItem(meal.meal_type.name))
                self.meals_table.setItem(i, 1, QTableWidgetItem(meal.name))
                self.meals_table.setItem(i, 2, QTableWidgetItem(str(meal.calories)))
                self.meals_table.setItem(i, 3, QTableWidgetItem(str(meal.protein)))
                self.meals_table.setItem(i, 4, QTableWidgetItem(str(meal.fat)))
                self.meals_table.setItem(i, 5, QTableWidgetItem(str(meal.carbs)))
                self.meals_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, meal.id)

    def load_progress_admin(self):
        with Session() as session:
            progress_entries = session.query(Progress).all()
           
            self.progress_table.setRowCount(len(progress_entries))
            for i, entry in enumerate(progress_entries):
                self.progress_table.setItem(i, 0, QTableWidgetItem(entry.user.name))
                self.progress_table.setItem(i, 1, QTableWidgetItem(entry.date.strftime("%d.%m.%Y")))
                self.progress_table.setItem(i, 2, QTableWidgetItem(str(entry.weight)))
                self.progress_table.setItem(i, 3, QTableWidgetItem(entry.notes))
                self.progress_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, entry.id)
                
    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()
            
    def add_user(self):
        self.user_window = UserAdminWindow()
        if self.user_window.exec():
            self.load_users()

    def edit_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для редактирования!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        with Session() as session:
            user = session.query(User).get(user_id)
            self.user_window = UserAdminWindow(user)
            if self.user_window.exec():
                self.load_users()

    def delete_user(self):
        selected_row = self.users_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления!")
            return
        
        user_id = self.users_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этого пользователя?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                user = session.query(User).get(user_id)
                session.delete(user)
                session.commit()
            
            self.load_users()

    def add_workout(self):
        self.workout_window = WorkoutWindowAdmin()
        if self.workout_window.exec():
            self.load_workouts_admin()

    def edit_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для редактирования!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            workout = session.query(Workout).get(workout_id)
            self.workout_window = WorkoutWindowAdmin(workout)
            if self.workout_window.exec():
                self.load_workouts_admin()

    def delete_workout(self):
        selected_row = self.workouts_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите тренировку для удаления!")
            return

        workout_id = self.workouts_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту тренировку?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                workout = session.query(Workout).get(workout_id)
                session.delete(workout)
                session.commit()

            self.load_workouts_admin()
            
    def add_exercise(self):
        self.exercise_window = ExerciseWindowAdmin()
        if self.exercise_window.exec():
            self.load_exercises_admin()

    def edit_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для редактирования!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            exercise = session.query(ExerciseName).get(exercise_id)
            self.exercise_window = ExerciseWindowAdmin(exercise)
            if self.exercise_window.exec():
                self.load_exercises_admin()

    def delete_exercise(self):
        selected_row = self.exercises_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите упражнение для удаления!")
            return

        exercise_id = self.exercises_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это упражнение?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                exercise = session.query(ExerciseName).get(exercise_id)
                session.delete(exercise)
                session.commit()

            self.load_exercises_admin()
            
    def add_meal(self):
        self.meal_window = MealWindowAdmin()
        if self.meal_window.exec():
            self.load_meals_admin()

    def edit_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для редактирования!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            meal = session.query(Meal).get(meal_id)
            self.meal_window = MealWindowAdmin(meal)
            if self.meal_window.exec():
                self.load_meals_admin()

    def delete_meal(self):
        selected_row = self.meals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите прием пищи для удаления!")
            return

        meal_id = self.meals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить этот прием пищи?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                meal = session.query(Meal).get(meal_id)
                session.delete(meal)
                session.commit()

            self.load_meals_admin()

    def add_progress(self):
        self.progress_window = ProgressWindowAdmin()
        if self.progress_window.exec():
            self.load_progress_admin()

    def edit_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        with Session() as session:
            progress = session.query(Progress).get(progress_id)
            self.progress_window = ProgressWindowAdmin(progress)
            if self.progress_window.exec():
                self.load_progress_admin()

    def delete_progress(self):
        selected_row = self.progress_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите запись для удаления!")
            return

        progress_id = self.progress_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту запись?",
                                    QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            with Session() as session:
                progress = session.query(Progress).get(progress_id)
                session.delete(progress)
                session.commit()

            self.load_progress_admin()

    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()

class UserAdminWindow(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Добавить пользователя" if not user else "Редактировать пользователя")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.height_edit = QLineEdit()
        self.weight_edit = QLineEdit()
        self.goal_combo = QComboBox()
        self.preference_combo = QComboBox()
        
        # Заполняем комбобоксы целей и предпочтений
        with Session() as session:
            goals = session.query(Goal).all()
            for goal in goals:
                self.goal_combo.addItem(goal.name, goal.id)
            
            preferences = session.query(Preference).all()
            for pref in preferences:
                self.preference_combo.addItem(pref.name, pref.id)
        
        # Если редактируем существующего пользователя, заполняем поля
        if user:
            self.name_edit.setText(user.name)
            self.email_edit.setText(user.email)
            self.gender_combo.setCurrentIndex(0 if user.gender else 1)
            self.height_edit.setText(str(user.height))
            self.weight_edit.setText(str(user.weightgoal))
            
            # Устанавливаем текущие цель и предпочтения
            index = self.goal_combo.findData(user.goal_id)
            if index >= 0:
                self.goal_combo.setCurrentIndex(index)
            
            index = self.preference_combo.findData(user.preference_id)
            if index >= 0:
                self.preference_combo.setCurrentIndex(index)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow("Цель:", self.goal_combo)
        form_layout.addRow("Предпочтение:", self.preference_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn.clicked.connect(self.reject)

    def save_user(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"
        goal_id = self.goal_combo.currentData()
        preference_id = self.preference_combo.currentData()
        
        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return
        
        if not all([name, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.user:
                # Редактируем существующего пользователя
                user = session.query(User).get(self.user.id)
                user.name = name
                user.email = email
                if password:
                    user.password = password
                user.gender = gender
                user.height = height
                user.weightgoal = weight
                user.goal_id = goal_id
                user.preference_id = preference_id
            else:
                # Создаем нового пользователя
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
                    return
                
                if session.query(User).filter_by(email=email).first():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                    return
                
                user = User(
                    name=name,
                    email=email,
                    password=password,
                    gender=gender,
                    height=height,
                    weightgoal=weight,
                    goal_id=goal_id,
                    preference_id=preference_id
                )
                session.add(user)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Пользователь сохранен!")
            self.accept()

class PreferenceWindowAdmin(QDialog):
    def __init__(self, preference=None):
        super().__init__()
        self.preference = preference
        self.setWindowTitle("Добавить предпочтение" if not preference else "Редактировать предпочтение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующее предпочтение, заполняем поля
        if preference:
            self.name_edit.setText(preference.name)
            self.description_edit.setText(preference.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_preference)
        self.cancel_btn.clicked.connect(self.reject)

    def save_preference(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.preference:
                # Редактируем существующее предпочтение
                preference = session.query(Preference).get(self.preference.id)
                preference.name = name
                preference.description = description
            else:
                # Создаем новое предпочтение
                preference = Preference(
                    name=name,
                    description=description
                )
                session.add(preference)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Предпочтение сохранено!")
            self.accept()

class GoalWindowAdmin(QDialog):
    def __init__(self, goal=None):
        super().__init__()
        self.goal = goal
        self.setWindowTitle("Добавить цель" if not goal else "Редактировать цель")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующую цель, заполняем поля
        if goal:
            self.name_edit.setText(goal.name)
            self.description_edit.setText(goal.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_goal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_goal(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.goal:
                # Редактируем существующую цель
                goal = session.query(Goal).get(self.goal.id)
                goal.name = name
                goal.description = description
            else:
                # Создаем новую цель
                goal = Goal(
                    name=name,
                    description=description
                )
                session.add(goal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Цель сохранена!")
            self.accept()

         

class WorkoutWindowAdmin(QDialog):
    def __init__(self, workout=None):
        super().__init__()
        self.workout = workout
        self.setWindowTitle("Добавить тренировку" if not workout else "Редактировать тренировку")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.time_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.worktype_combo = QComboBox()
       
        # Заполняем комбобоксы
        with Session() as session:
            # Пользователи
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
           
            # Типы тренировок
            work_types = session.query(WorkType).all()
            for wt in work_types:
                self.worktype_combo.addItem(wt.name, wt.id)
       
        # Если редактируем существующую тренировку, заполняем поля
        if workout:
            index = self.user_combo.findData(workout.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(workout.date)
            self.time_edit.setText(str(workout.time))
            self.calories_edit.setText(str(workout.calories))
            index = self.worktype_combo.findData(workout.worktype_id)
            if index >= 0:
                self.worktype_combo.setCurrentIndex(index)
       
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
       
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип тренировки:", self.worktype_combo)
        form_layout.addRow("Длительность (мин):", self.time_edit)
        form_layout.addRow("Калории:", self.calories_edit)
       
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
       
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
       
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_workout)
        self.cancel_btn.clicked.connect(self.reject)

    def save_workout(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        worktype_id = self.worktype_combo.currentData()
       
        try:
            time = int(self.time_edit.text())
            calories = float(self.calories_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Длительность и калории должны быть числами!")
            return
       
        if not all([user_id, date, worktype_id, time, calories]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
       
        with Session() as session:
            if self.workout:
                # Редактируем существующую тренировку
                workout = session.query(Workout).get(self.workout.id)
                workout.user_id = user_id
                workout.date = date
                workout.time = time
                workout.calories = calories
                workout.worktype_id = worktype_id
            else:
                # Создаем новую тренировку
                workout = Workout(
                    user_id=user_id,
                    date=date,
                    time=time,
                    calories=calories,
                    worktype_id=worktype_id
                )
                session.add(workout)
           
            session.commit()
            QMessageBox.information(self, "Успех", "Тренировка сохранена!")
            self.accept()

class ExerciseWindowAdmin(QDialog):
    def __init__(self, exercise=None):
        super().__init__()
        self.exercise = exercise
        self.setWindowTitle("Добавить упражнение" if not exercise else "Редактировать упражнение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
       
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.exercisetype_combo = QComboBox()
       
        # Заполняем комбобокс типами упражнений
        with Session() as session:
            exercisetypes = session.query(ExerciseType).all()
            for et in exercisetypes:
                self.exercisetype_combo.addItem(et.name, et.id)
       
        # Если редактируем существующее упражнение, заполняем поля
        if exercise:
            self.name_edit.setText(exercise.name)
            index = self.exercisetype_combo.findData(exercise.exercisetype_id)
            if index >= 0:
                self.exercisetype_combo.setCurrentIndex(index)
       
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
       
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Тип упражнения:", self.exercisetype_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_exercise)
        self.cancel_btn.clicked.connect(self.reject)

    def save_exercise(self):
        name = self.name_edit.text().strip()
        exercisetype_id = self.exercisetype_combo.currentData()
        
        if not all([name, exercisetype_id]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        with Session() as session:
            if self.exercise:
                # Редактируем существующее упражнение
                exercise = session.query(ExerciseName).get(self.exercise.id)
                exercise.name = name
                exercise.exercisetype_id = exercisetype_id
            else:
                # Создаем новое упражнение
                exercise = ExerciseName(
                    name=name,
                    exercisetype_id=exercisetype_id
                )
                session.add(exercise)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Упражнение сохранено!")
            self.accept()

class MealWindowAdmin(QDialog):
    def __init__(self, meal=None):
        super().__init__()
        self.meal = meal
        self.setWindowTitle("Добавить прием пищи" if not meal else "Редактировать прием пищи")
        self.setFixedSize(400, 400)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.mealtype_combo = QComboBox()
        self.name_edit = QLineEdit()
        self.calories_edit = QLineEdit()
        self.protein_edit = QLineEdit()
        self.fat_edit = QLineEdit()
        self.carbs_edit = QLineEdit()
        
        # Заполняем комбобоксы
        with Session() as session:
            # Пользователи
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
            
            # Типы приемов пищи
            meal_types = session.query(MealType).all()
            for mt in meal_types:
                self.mealtype_combo.addItem(mt.name, mt.id)
        
        # Если редактируем существующий прием пищи, заполняем поля
        if meal:
            index = self.user_combo.findData(meal.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit.setDate(meal.date)
            index = self.mealtype_combo.findData(meal.mealtype_id)
            if index >= 0:
                self.mealtype_combo.setCurrentIndex(index)
            self.name_edit.setText(meal.name)
            self.calories_edit.setText(str(meal.calories))
            self.protein_edit.setText(str(meal.protein))
            self.fat_edit.setText(str(meal.fat))
            self.carbs_edit.setText(str(meal.carbs))
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Тип приема пищи:", self.mealtype_combo)
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Калории:", self.calories_edit)
        form_layout.addRow("Белки (г):", self.protein_edit)
        form_layout.addRow("Жиры (г):", self.fat_edit)
        form_layout.addRow("Углеводы (г):", self.carbs_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_meal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_meal(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        mealtype_id = self.mealtype_combo.currentData()
        name = self.name_edit.text().strip()
        
        try:
            calories = float(self.calories_edit.text())
            protein = float(self.protein_edit.text())
            fat = float(self.fat_edit.text())
            carbs = float(self.carbs_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Все числовые поля должны содержать числа!")
            return
        
        if not all([user_id, date, mealtype_id, name, calories, protein, fat, carbs]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        with Session() as session:
            if self.meal:
                # Редактируем существующий прием пищи
                meal = session.query(Meal).get(self.meal.id)
                meal.user_id = user_id
                meal.date = date
                meal.mealtype_id = mealtype_id
                meal.name = name
                meal.calories = calories
                meal.protein = protein
                meal.fat = fat
                meal.carbs = carbs
            else:
                # Создаем новый прием пищи
                meal = Meal(
                    user_id=user_id,
                    date=date,
                    mealtype_id=mealtype_id,
                    name=name,
                    calories=calories,
                    protein=protein,
                    fat=fat,
                    carbs=carbs
                )
                session.add(meal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Прием пищи сохранен!")
            self.accept()

class ProgressWindowAdmin(QDialog):
    def __init__(self, progress=None):
        super().__init__()
        self.progress = progress
        self.setWindowTitle("Добавить запись о прогрессе" if not progress else "Редактировать запись о прогрессе")
        self.setFixedSize(400, 300)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.user_combo = QComboBox()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.weight_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        
        # Заполняем комбобокс пользователями
        with Session() as session:
            users = session.query(User).all()
            for user in users:
                self.user_combo.addItem(user.name, user.id)
        
        # Если редактируем существующую запись, заполняем поля
        if progress:
            index = self.user_combo.findData(progress.user_id)
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
            self.date_edit = QDateEdit()
            self.date_edit.setCalendarPopup(True)
            self.weight_edit = QLineEdit()
            self.notes_edit = QLineEdit()

        # Если редактируем существующую запись, заполняем поля
        if progress:
            self.date_edit.setDate(progress.date)
            self.weight_edit.setText(str(progress.weight))
            self.notes_edit.setText(progress.notes)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Пользователь:", self.user_combo)
        form_layout.addRow("Дата:", self.date_edit)
        form_layout.addRow("Вес (кг):", self.weight_edit)
        form_layout.addRow("Заметки:", self.notes_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_progress)
        self.cancel_btn.clicked.connect(self.reject)

    def save_progress(self):
        user_id = self.user_combo.currentData()
        date = self.date_edit.date().toPyDate()
        
        try:
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Вес должен быть числом!")
            return
        
        notes = self.notes_edit.text().strip()
        
        if not all([user_id, date, weight]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.progress:
                # Редактируем существующую запись
                progress = session.query(Progress).get(self.progress.id)
                progress.user_id = user_id
                progress.date = date
                progress.weight = weight
                progress.notes = notes
            else:
                # Создаем новую запись
                progress = Progress(
                    user_id=user_id,
                    date=date,
                    weight=weight,
                    notes=notes
                )
                session.add(progress)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Запись о прогрессе сохранена!")
            self.accept()

    def add_preference(self):
        self.preference_window = PreferenceWindowAdmin()
        if self.preference_window.exec():
            self.load_preferences()

    def edit_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для редактирования!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            preference = session.query(Preference).get(pref_id)
            self.preference_window = PreferenceWindowAdmin(preference)
            if self.preference_window.exec():
                self.load_preferences()

    def delete_preference(self):
        selected_row = self.preferences_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите предпочтение для удаления!")
            return
        
        pref_id = self.preferences_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить это предпочтение?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                preference = session.query(Preference).get(pref_id)
                session.delete(preference)
                session.commit()
            
            self.load_preferences()

    def add_goal(self):
        self.goal_window = GoalWindowAdmin()
        if self.goal_window.exec():
            self.load_goals()

    def edit_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для редактирования!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        with Session() as session:
            goal = session.query(Goal).get(goal_id)
            self.goal_window = GoalWindowAdmin(goal)
            if self.goal_window.exec():
                self.load_goals()

    def delete_goal(self):
        selected_row = self.goals_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите цель для удаления!")
            return
        
        goal_id = self.goals_table.item(selected_row, 0).data(Qt.UserRole)
        
        reply = QMessageBox.question(self, "Подтверждение",
                                    "Вы уверены, что хотите удалить эту цель?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with Session() as session:
                goal = session.query(Goal).get(goal_id)
                session.delete(goal)
                session.commit()
            
            self.load_goals()

class UserAdminWindow(QDialog):
    def __init__(self, user=None):
        super().__init__()
        self.user = user
        self.setWindowTitle("Добавить пользователя" if not user else "Редактировать пользователя")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Мужской", "Женский"])
        self.height_edit = QLineEdit()
        self.weight_edit = QLineEdit()
        self.goal_combo = QComboBox()
        self.preference_combo = QComboBox()
        
        # Заполняем комбобоксы целей и предпочтений
        with Session() as session:
            goals = session.query(Goal).all()
            for goal in goals:
                self.goal_combo.addItem(goal.name, goal.id)
            
            preferences = session.query(Preference).all()
            for pref in preferences:
                self.preference_combo.addItem(pref.name, pref.id)
        
        # Если редактируем существующего пользователя, заполняем поля
        if user:
            self.name_edit.setText(user.name)
            self.email_edit.setText(user.email)
            self.gender_combo.setCurrentIndex(0 if user.gender else 1)
            self.height_edit.setText(str(user.height))
            self.weight_edit.setText(str(user.weightgoal))
            
            # Устанавливаем текущие цель и предпочтения
            index = self.goal_combo.findData(user.goal_id)
            if index >= 0:
                self.goal_combo.setCurrentIndex(index)
            
            index = self.preference_combo.findData(user.preference_id)
            if index >= 0:
                self.preference_combo.setCurrentIndex(index)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Имя:", self.name_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Пароль:", self.password_edit)
        form_layout.addRow("Пол:", self.gender_combo)
        form_layout.addRow("Рост (см):", self.height_edit)
        form_layout.addRow("Целевой вес (кг):", self.weight_edit)
        form_layout.addRow("Цель:", self.goal_combo)
        form_layout.addRow("Предпочтение:", self.preference_combo)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_user)
        self.cancel_btn.clicked.connect(self.reject)

    def save_user(self):
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        password = self.password_edit.text().strip()
        gender = self.gender_combo.currentText() == "Мужской"
        goal_id = self.goal_combo.currentData()
        preference_id = self.preference_combo.currentData()
        
        try:
            height = int(self.height_edit.text())
            weight = float(self.weight_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Рост и вес должны быть числами!")
            return
        
        if not all([name, email]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return
        
        with Session() as session:
            if self.user:
                # Редактируем существующего пользователя
                user = session.query(User).get(self.user.id)
                user.name = name
                user.email = email
                if password:
                    user.password = password
                user.gender = gender
                user.height = height
                user.weightgoal = weight
                user.goal_id = goal_id
                user.preference_id = preference_id
            else:
                # Создаем нового пользователя
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
                    return
                
                if session.query(User).filter_by(email=email).first():
                    QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                    return
                
                user = User(
                    name=name,
                    email=email,
                    password=password,
                    gender=gender,
                    height=height,
                    weightgoal=weight,
                    goal_id=goal_id,
                    preference_id=preference_id
                )
                session.add(user)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Пользователь сохранен!")
            self.accept()

class PreferenceWindowAdmin(QDialog):
    def __init__(self, preference=None):
        super().__init__()
        self.preference = preference
        self.setWindowTitle("Добавить предпочтение" if not preference else "Редактировать предпочтение")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующее предпочтение, заполняем поля
        if preference:
            self.name_edit.setText(preference.name)
            self.description_edit.setText(preference.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_preference)
        self.cancel_btn.clicked.connect(self.reject)

    def save_preference(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.preference:
                # Редактируем существующее предпочтение
                preference = session.query(Preference).get(self.preference.id)
                preference.name = name
                preference.description = description
            else:
                # Создаем новое предпочтение
                preference = Preference(
                    name=name,
                    description=description
                )
                session.add(preference)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Предпочтение сохранено!")
            self.accept()

class GoalWindowAdmin(QDialog):
    def __init__(self, goal=None):
        super().__init__()
        self.goal = goal
        self.setWindowTitle("Добавить цель" if not goal else "Редактировать цель")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        
        # Поля для ввода
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        
        # Если редактируем существующую цель, заполняем поля
        if goal:
            self.name_edit.setText(goal.name)
            self.description_edit.setText(goal.description)
        
        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")
        
        # Форма
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Описание:", self.description_edit)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
        # Подключение сигналов
        self.save_btn.clicked.connect(self.save_goal)
        self.cancel_btn.clicked.connect(self.reject)

    def save_goal(self):
        name = self.name_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
            return
        
        with Session() as session:
            if self.goal:
                # Редактируем существующую цель
                goal = session.query(Goal).get(self.goal.id)
                goal.name = name
                goal.description = description
            else:
                # Создаем новую цель
                goal = Goal(
                    name=name,
                    description=description
                )
                session.add(goal)
            
            session.commit()
            QMessageBox.information(self, "Успех", "Цель сохранена!")
            self.accept()

def center_window(window):
    """Центрирует окно на экране."""
    screen = QApplication.primaryScreen()
    rect = screen.availableGeometry()
    size = window.geometry()
    x = (rect.width() - size.width()) // 2
    y = (rect.height() - size.height()) // 2
    window.move(x, y)

if __name__ == "__main__":
    # Создаем таблицы в базе данных, если их нет
    Base.metadata.create_all(engine)
    
    app = QApplication([])
    login_window = LoginWindow()
    center_window(login_window)  # Центрируем окно входа
    login_window.show()
    app.exec()
