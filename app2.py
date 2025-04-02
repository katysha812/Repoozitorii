from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication, QLineEdit, QComboBox, QLabel

from db import Session
from models import Student, Group

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Пол", "Группа"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Поиск по фамилии...")

        self.search_text.textChanged.connect(self.search_students)
        self.layout.addWidget(self.search_text)

        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)
        self.load_groups()

        self.group_filter.currentIndexChanged.connect(self.filter_students)
        self.layout.addWidget(QLabel("Фильтр по группе:"))
        self.layout.addWidget(self.group_filter)

        self.load_data()
    
    def load_data(self):
        with Session() as session:
            students = session.query(Student).all()
            self.display_students(students)

    def display_students(self,students):
        self.table.setRowCount(0)

        with Session():
            for i, student in enumerate(students):
                self.table.insertRow(i)
                self.table.setItem(i,0,QTableWidgetItem(student.last_name))
                self.table.setItem(i,1,QTableWidgetItem(student.first_name))
                self.table.setItem(i,2,QTableWidgetItem(student.middle_name))
                gender = "Мужской" if student.gender else "Женский"
                self.table.setItem(i,3,QTableWidgetItem(gender))
                self.table.setItem(i,4,QTableWidgetItem(student.group.name))

    def search_students(self):
        search_text = self.search_text.text().strip()
        students = []

        with Session() as session:
            if search_text:
                students = session.query(Student).filter(Student.last_name.ilike(f"%{search_text}%")).all()
            else:
                self.load_data()

            self.display_students(students)

    def load_groups(self):
        with Session() as session:
            groups = session.query(Group).all()
            for group in groups:
                self.group_filter.addItem(group.name, group.id)

    def filter_students(self):
        
        with Session() as session:
            students = session.query(Student).all()
            selected_group_id = self.group_filter.currentData()
            if not selected_group_id:
                self.load_data()
                return
            filtered = [
                student for student in students
                if student.group_id == selected_group_id
            ]

            self.display_students(filtered)

app = QApplication([])
window = MainWindow()
window.show()
app.exec()