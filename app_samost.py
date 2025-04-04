from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QLineEdit, 
    QLabel, 
    QComboBox, 
    QPushButton, 
    QRadioButton, 
    QButtonGroup, 
    QVBoxLayout, 
    QHBoxLayout, 
    QMessageBox, 
    QMainWindow, 
    QTableWidget, 
    QTableWidgetItem, 
    QTabWidget
)
from db import Session
from models import Student, Group, Course, Lesson

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учебное заведение")
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        self.create_students_tab()
        self.create_groups_tab()
        self.create_courses_tab()
        self.create_lessons_tab()
        
        self.setLayout(layout)
    
    def create_students_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Пол", "Группа"])
        layout.addWidget(self.students_table)
        
        self.add_student_btn = QPushButton("Добавить студента")
        self.add_student_btn.clicked.connect(self.open_add_student_window)
        layout.addWidget(self.add_student_btn)
        
        self.tab_widget.addTab(tab, "Студенты")
        self.load_students_data()
    
    def create_groups_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.groups_table = QTableWidget()
        self.groups_table.setColumnCount(2)
        self.groups_table.setHorizontalHeaderLabels(["Название", "Курс"])
        layout.addWidget(self.groups_table)
        
        self.add_group_btn = QPushButton("Добавить группу")
        self.add_group_btn.clicked.connect(self.open_add_group_window)
        layout.addWidget(self.add_group_btn)
        
        self.tab_widget.addTab(tab, "Группы")
        self.load_groups_data()
    
    def create_courses_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.courses_table = QTableWidget()
        self.courses_table.setColumnCount(1)
        self.courses_table.setHorizontalHeaderLabels(["Номер курса"])
        layout.addWidget(self.courses_table)
        
        self.add_course_btn = QPushButton("Добавить курс")
        self.add_course_btn.clicked.connect(self.open_add_course_window)
        layout.addWidget(self.add_course_btn)
        
        self.tab_widget.addTab(tab, "Курсы")
        self.load_courses_data()
    
    def create_lessons_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.lessons_table = QTableWidget()
        self.lessons_table.setColumnCount(1)
        self.lessons_table.setHorizontalHeaderLabels(["Название предмета"])
        layout.addWidget(self.lessons_table)
        
        self.add_lesson_btn = QPushButton("Добавить предмет")
        self.add_lesson_btn.clicked.connect(self.open_add_lesson_window)
        layout.addWidget(self.add_lesson_btn)
        
        self.tab_widget.addTab(tab, "Предметы")
        self.load_lessons_data()
    
    def load_students_data(self):
        with Session() as session:
            self.students_table.setRowCount(0)
            students = session.query(Student).join(Group).all()
            for i, student in enumerate(students):
                self.students_table.insertRow(i)
                self.students_table.setItem(i, 0, QTableWidgetItem(student.last_name))
                self.students_table.setItem(i, 1, QTableWidgetItem(student.first_name))
                self.students_table.setItem(i, 2, QTableWidgetItem(student.middle_name))
                
                if student.gender:
                    self.students_table.setItem(i, 3, QTableWidgetItem("Мужской"))
                else:
                    self.students_table.setItem(i, 3, QTableWidgetItem("Женский"))
                
                self.students_table.setItem(i, 4, QTableWidgetItem(student.group.name))
            
    
    def load_groups_data(self):
        with Session() as session:
            self.groups_table.setRowCount(0)
            groups = session.query(Group).join(Course).all()
            for i, group in enumerate(groups):
                self.groups_table.insertRow(i)
                self.groups_table.setItem(i, 0, QTableWidgetItem(group.name))
                self.groups_table.setItem(i, 1, QTableWidgetItem(str(group.course.number)))
    
    def load_courses_data(self):
        with Session() as session:
            self.courses_table.setRowCount(0)
            courses = session.query(Course).all()
            for i, course in enumerate(courses):
                self.courses_table.insertRow(i)
                self.courses_table.setItem(i, 0, QTableWidgetItem(str(course.number)))
    
    def load_lessons_data(self):
        with Session() as session:
            self.lessons_table.setRowCount(0)
            lessons = session.query(Lesson).all()
            for i, lesson in enumerate(lessons):
                self.lessons_table.insertRow(i)
                self.lessons_table.setItem(i, 0, QTableWidgetItem(lesson.name))
    
    def open_add_student_window(self):
        self.add_student_window = AddStudentWindow()
        self.add_student_window.show()
        self.add_student_window.destroyed.connect(self.load_students_data)
    
    def open_add_group_window(self):
        self.add_group_window = AddGroupWindow()
        self.add_group_window.show()
        self.add_group_window.destroyed.connect(self.load_groups_data)
    
    def open_add_course_window(self):
        self.add_course_window = AddCourseWindow()
        self.add_course_window.show()
        self.add_course_window.destroyed.connect(self.load_courses_data)
    
    def open_add_lesson_window(self):
        self.add_lesson_window = AddLessonWindow()
        self.add_lesson_window.show()
        self.add_lesson_window.destroyed.connect(self.load_lessons_data)

class AddStudentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowTitle("Добавление нового студента")
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Введите фамилию")
        self.layout.addWidget(QLabel("Фамилия:"))
        self.layout.addWidget(self.last_name_edit)
        
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("Введите имя")
        self.layout.addWidget(QLabel("Имя:"))
        self.layout.addWidget(self.first_name_edit)
        
        self.mid_name_edit = QLineEdit()
        self.mid_name_edit.setPlaceholderText("Введите отчество")
        self.layout.addWidget(QLabel("Отчество:"))
        self.layout.addWidget(self.mid_name_edit)
        
        self.layout.addWidget(QLabel("Пол:"))
        
        self.gender_group = QButtonGroup()
        self.gender_male = QRadioButton("М")
        self.gender_female = QRadioButton("Ж")
        self.gender_group.addButton(self.gender_male)
        self.gender_group.addButton(self.gender_female)
        
        self.gender_male.setChecked(True)
        
        gender_layout = QHBoxLayout()
        gender_layout.addWidget(self.gender_male)
        gender_layout.addWidget(self.gender_female)
        self.layout.addLayout(gender_layout)
        
        self.group_cbox = QComboBox()
        self.group_cbox.addItem("Выберите группу", None)
        
        self.load_groups()
        self.layout.addWidget(QLabel("Группа:"))
        self.layout.addWidget(self.group_cbox)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_student)
        self.layout.addWidget(self.add_btn)
        
        self.setLayout(self.layout)
        
    def load_groups(self):
        with Session() as session:
            groups = session.query(Group).all()
            self.group_cbox.clear()
            self.group_cbox.addItem("Выберите группу", None)
            for group in groups:
                self.group_cbox.addItem(group.name, group.id)
                
    def add_student(self):
        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        mid_name = self.mid_name_edit.text().strip()
        
        gender = True if self.gender_male.isChecked() else False
        
        group_id = self.group_cbox.currentData()
        
        if not last_name or not first_name or not group_id:
            QMessageBox.warning(self, "Ошибка", "Заполните обязательные поля!")
            return
        
        with Session() as session:
            new_student = Student(
                last_name=last_name,
                first_name=first_name,
                middle_name=mid_name if mid_name else None,
                gender=gender,
                group_id=group_id
            )
            session.add(new_student)
            session.commit()
            QMessageBox.information(self, "Готово", "Студент добавлен!")
            self.close()

class AddGroupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowTitle("Добавление новой группы")
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название группы")
        self.layout.addWidget(QLabel("Название группы:"))
        self.layout.addWidget(self.name_edit)
        
        self.course_cbox = QComboBox()
        self.course_cbox.addItem("Выберите курс", None)
        
        self.load_courses()
        self.layout.addWidget(QLabel("Курс:"))
        self.layout.addWidget(self.course_cbox)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_group)
        self.layout.addWidget(self.add_btn)
        
        self.setLayout(self.layout)
        
    def load_courses(self):
        with Session() as session:
            courses = session.query(Course).all()
            self.course_cbox.clear()
            self.course_cbox.addItem("Выберите курс", None)
            for course in courses:
                self.course_cbox.addItem(str(course.number), course.id)
                
    def add_group(self):
        name = self.name_edit.text().strip()
        course_id = self.course_cbox.currentData()
        
        if not name or not course_id:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        
        with Session() as session:
            new_group = Group(
                name=name,
                course_id=course_id
            )
            session.add(new_group)
            session.commit()
            QMessageBox.information(self, "Готово", "Группа добавлена!")
            self.close()

class AddCourseWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowTitle("Добавление нового курса")
        
        self.number_edit = QLineEdit()
        self.number_edit.setPlaceholderText("Введите номер курса")
        self.layout.addWidget(QLabel("Номер курса:"))
        self.layout.addWidget(self.number_edit)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_course)
        self.layout.addWidget(self.add_btn)
        
        self.setLayout(self.layout)
        
    def add_course(self):
        number = self.number_edit.text().strip()
        
        if not number:
            QMessageBox.warning(self, "Ошибка", "Введите номер курса!")
            return
        
        try:
            number = int(number)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Номер курса должен быть числом!")
            return
        
        with Session() as session:
            new_course = Course(
                number=number
            )
            session.add(new_course)
            session.commit()
            QMessageBox.information(self, "Готово", "Курс добавлен!")
            self.close()

class AddLessonWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowTitle("Добавление нового предмета")
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название предмета")
        self.layout.addWidget(QLabel("Название предмета:"))
        self.layout.addWidget(self.name_edit)
        
        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_lesson)
        self.layout.addWidget(self.add_btn)
        
        self.setLayout(self.layout)
        
    def add_lesson(self):
        name = self.name_edit.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название предмета!")
            return
        
        with Session() as session:
            new_lesson = Lesson(
                name=name
            )
            session.add(new_lesson)
            session.commit()
            QMessageBox.information(self, "Готово", "Предмет добавлен!")
            self.close()

app = QApplication([])
window = MainWindow()
window.show()
app.exec()