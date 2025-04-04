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
    QMessageBox
)

from db import Session
from models import Student, Group

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
            for group in groups:
                self.group_cbox.addItem(group.name, group.id)
                
    def add_student(self):
        last_name = self.last_name_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        mid_name = self.mid_name_edit.text().strip()
        
        gender = True if self.gender_male.isChecked() or self.gender_female.isChecked() else False
        
        group_id = self.group_cbox.currentData()
        
        if (not last_name or not first_name or
            not gender or not group_id):
            QMessageBox.warning(self, "Ошибка","Заполните обязательные поля!")
            return
        
        with Session() as session:
            new_student = Student(
            last_name = last_name,
            first_name = first_name,
            middle_name = mid_name,
            gender = gender,
            group_id = group_id
        )
        session.add(new_student)
        session.commit()
        QMessageBox.information(self,"Готово","Студент добавлен!")
        
app = QApplication([])
window = AddStudentWindow()
window.show()
app.exec()