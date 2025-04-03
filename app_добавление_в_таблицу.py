from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, 
                            QApplication, QHBoxLayout, QLineEdit, 
                            QCheckBox, QComboBox, QLabel,QTabWidget, QPushButton, QMessageBox)

from db import Session
from models import Student, Group, Course, Lesson, groups_lessons
from sqlalchemy.sql import insert

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учебное заведение")
        self.setGeometry(100, 100, 800, 600)
        
        self.layout = QVBoxLayout()
        
        self.btn_layout = QHBoxLayout()
        
        self.students_btn = QPushButton("Студенты")
        self.students_btn.clicked.connect(self.show_students)
        
        self.groups_btn = QPushButton("Группы")
        self.groups_btn.clicked.connect(self.show_groups)
        
        self.courses_btn = QPushButton("Курсы")
        self.courses_btn.clicked.connect(self.show_courses)
        
        self.lessons_btn = QPushButton("Предметы")
        self.lessons_btn.clicked.connect(self.show_lessons)
        
        self.btn_layout.addWidget(self.students_btn)
        self.btn_layout.addWidget(self.groups_btn)
        self.btn_layout.addWidget(self.courses_btn)
        self.btn_layout.addWidget(self.lessons_btn)
        
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        
        self.tabs = QTabWidget()
        self.groups_lessons_tab = GroupsLessonsTab()
        self.tabs.addTab(self.groups_lessons_tab,"Группы и уроки")
        self.layout.addWidget(self.tabs)
        
        self.show_students()
    
    def show_students(self):
        self.clear_layout()
        self.students_window = StudentsWindow()
        self.layout.addWidget(self.students_window)
        
    def show_groups(self):
        self.clear_layout()
        self.groups_window = GroupsWindow()
        self.layout.addWidget(self.groups_window)
        
    def show_courses(self):
        self.clear_layout()
        self.courses_window = CoursesWindow()
        self.layout.addWidget(self.courses_window)
        
    def show_lessons(self):
        self.clear_layout()
        self.lessons_window = LessonsWindow()
        self.layout.addWidget(self.lessons_window)
        
    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            if self.layout.itemAt(i).widget():
                self.layout.itemAt(i).widget().setParent(None)

class StudentsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Пол", "Группа"])
        self.layout.addWidget(self.table)
        
        self.form_layout = QHBoxLayout()
        
        left_form = QVBoxLayout()
        left_form.addWidget(QLabel("Фамилия:"))
        self.last_name_input = QLineEdit()
        left_form.addWidget(self.last_name_input)
        
        left_form.addWidget(QLabel("Имя:"))
        self.first_name_input = QLineEdit()
        left_form.addWidget(self.first_name_input)
        
        left_form.addWidget(QLabel("Отчество:"))
        self.middle_name_input = QLineEdit()
        left_form.addWidget(self.middle_name_input)
        
        right_form = QVBoxLayout()
        right_form.addWidget(QLabel("Пол:"))
        self.gender_check = QCheckBox("Мужской")
        right_form.addWidget(self.gender_check)
        
        right_form.addWidget(QLabel("Группа:"))
        self.group_combo = QComboBox()
        right_form.addWidget(self.group_combo)
        
        self.form_layout.addLayout(left_form)
        self.form_layout.addLayout(right_form)
        self.layout.addLayout(self.form_layout)
        
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_student)
        self.btn_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        
        self.load_data()
    
    def load_data(self):
        with Session() as session:
            self.table.setRowCount(0)
            students = session.query(Student).all()
            for i, s in enumerate(students):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(s.last_name))
                self.table.setItem(i, 1, QTableWidgetItem(s.first_name))
                self.table.setItem(i, 2, QTableWidgetItem(s.middle_name))

                if s.gender:
                    self.table.setItem(i, 3, QTableWidgetItem("Мужской"))
                else:
                    self.table.setItem(i, 3, QTableWidgetItem("Женский"))
                
                self.table.setItem(i, 4, QTableWidgetItem(s.group.name))
            
            self.group_combo.clear()
            groups = session.query(Group).all()
            for group in groups:
                self.group_combo.addItem(group.name, group.id)
    
    def add_student(self):
        last_name = self.last_name_input.text().strip()
        first_name = self.first_name_input.text().strip()
        middle_name = self.middle_name_input.text().strip()
        gender = self.gender_check.isChecked()
        group_id = self.group_combo.currentData()
        
        if last_name and first_name:
            with Session() as session:
                student = Student(
                    last_name=last_name,
                    first_name=first_name,
                    middle_name=middle_name,
                    gender=gender,
                    group_id=group_id
                )
                session.add(student)
                session.commit()
            
            self.load_data()
            self.last_name_input.clear()
            self.first_name_input.clear()
            self.middle_name_input.clear()
            self.gender_check.setChecked(False)

class GroupsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Название", "Курс"])
        self.layout.addWidget(self.table)
        
        self.form_layout = QHBoxLayout()
        
        left_form = QVBoxLayout()
        left_form.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        left_form.addWidget(self.name_input)
        
        right_form = QVBoxLayout()
        right_form.addWidget(QLabel("Курс:"))
        self.course_combo = QComboBox()
        right_form.addWidget(self.course_combo)
        
        self.form_layout.addLayout(left_form)
        self.form_layout.addLayout(right_form)
        self.layout.addLayout(self.form_layout)
        
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_group)
        self.btn_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        
        self.load_data()
    
    def load_data(self):
        with Session() as session:
            self.table.setRowCount(0)
            groups = session.query(Group).all()
            for i, g in enumerate(groups):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(g.name))
                self.table.setItem(i, 1, QTableWidgetItem(str(g.course.number)))
            
            self.course_combo.clear()
            courses = session.query(Course).all()
            for course in courses:
                self.course_combo.addItem(str(course.number), course.id)
    
    def add_group(self):
        name = self.name_input.text().strip()
        course_id = self.course_combo.currentData()
        
        if name:
            with Session() as session:
                group = Group(name=name, course_id=course_id)
                session.add(group)
                session.commit()
            
            self.load_data()
            self.name_input.clear()

class CoursesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Номер курса"])
        self.layout.addWidget(self.table)
        
        self.form_layout = QHBoxLayout()
        
        self.form_layout.addWidget(QLabel("Номер курса:"))
        self.number_input = QLineEdit()
        self.form_layout.addWidget(self.number_input)
        
        self.layout.addLayout(self.form_layout)
        
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_course)
        self.btn_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        
        self.load_data()
    
    def load_data(self):
        with Session() as session:
            self.table.setRowCount(0)
            courses = session.query(Course).all()
            for i, c in enumerate(courses):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(str(c.number)))
    
    def add_course(self):
        number = self.number_input.text().strip()
        
        if number:
            with Session() as session:
                course = Course(number=int(number))
                session.add(course)
                session.commit()
            
            self.load_data()
            self.number_input.clear()

class LessonsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Название предмета"])
        self.layout.addWidget(self.table)
        
        self.form_layout = QHBoxLayout()
        
        self.form_layout.addWidget(QLabel("Название:"))
        self.name_input = QLineEdit()
        self.form_layout.addWidget(self.name_input)
        
        self.layout.addLayout(self.form_layout)
        
        self.btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_lesson)
        self.btn_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(self.btn_layout)
        self.setLayout(self.layout)
        
        self.load_data()
    
    def load_data(self):
        with Session() as session:
            self.table.setRowCount(0)
            lessons = session.query(Lesson).all()
            for i, l in enumerate(lessons):
                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(l.name))
    
    def add_lesson(self):
        name = self.name_input.text().strip()
        
        if name:
            with Session() as session:
                lesson = Lesson(name=name)
                session.add(lesson)
                session.commit()
            
            self.load_data()
            self.name_input.clear()

class GroupsLessonsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        self.group_cbox = QComboBox()
        self.group_cbox.addItem("Выберите группу", None)
        self.load_groups()
        self.layout.addWidget(QLabel("Выберите группу:"))
        self.layout.addWidget(self.group_cbox)
        
        self.lesson_cbox = QComboBox()
        self.lesson_cbox.addItem("Выберите урок", None)
        self.load_lessons()
        self.layout.addWidget(QLabel("Выберите урок:"))
        self.layout.addWidget(self.lesson_cbox)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add)
        self.layout.addWidget(self.add_btn)
        
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Группа", "Урок"])
        self.layout.addWidget(self.table)
        
        self.setLayout(self.layout)
    
    def load_groups(self):
        with Session() as session:
            groups = session.query(Group).all()
            for group in groups:
                self.group_cbox.addItem(group.name, group.id)
                
    def load_lessons(self):
        with Session() as session:
            lessons = session.query(Lesson).all()
            for lesson in lessons:
                self.lesson_cbox.addItem(lesson.name, lesson.id)
                
    def load_data(self):
        with Session() as session:
            connections = session.execute(groups_lessons.select()).fetchall()
            self.table.setRowCount(0)
            for i, connection in enumerate(connections):
                group_id, lesson_id = connection
                group = session.query(Group).get(group_id)
                lesson = session.query(Lesson).get(lesson_id)
                self.table.insertRow(i)
                self.table.setItem(i,0,QTableWidgetItem(group.name))
                self.table.setItem(i,1,QTableWidgetItem(lesson.name))
                
    def add(self):
        group_id = self.group_cbox.currentData()
        lesson_id = self.lesson_cbox.currentData()
        
        if not group_id or not lesson_id:
            QMessageBox.warning(self,"Ошибка","Выберите группу и урок!")
            return
        
        with Session() as session:
            existing = session.execute(
                groups_lessons.select().where(
                    (groups_lessons.c.group_id == group_id) &
                    (groups_lessons.c.lesson_id == lesson_id)
                )
            ).fetchone()
            if existing:
                QMessageBox.warning(self, "Ошибка","Такая связь уже существует!")
                return
            
            session.execute(
                insert(groups_lessons).values(group_id=group_id, lesson_id=lesson_id)
            )
            
            session.commit()
            QMessageBox.information(self,"Успех","Запись добавлена!")
            self.load_data()
        
app = QApplication([])
window = MainWindow()
window.show()
app.exec()