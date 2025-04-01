from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication

from db import Session
from models import Student

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(["Фамилия", "Имя", "Отчество", "Пол", "Группа"])
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

        self.load_data()
    
    def load_data(self):
        with Session() as session:
            self.table.setRowCount(0)
            students = session.query(Student).all()
            for i, s in enumerate(students):
                self.table.insertRow(i)
                self.table.setItem(i,0,QTableWidgetItem(s.last_name))
                self.table.setItem(i,1,QTableWidgetItem(s.first_name))
                self.table.setItem(i,2,QTableWidgetItem(s.middle_name))

                if s.gender:
                    self.table.setItem(i,3,QTableWidgetItem("Мужской"))
                else:
                    self.table.setItem(i,3,QTableWidgetItem("Женский"))
                
                self.table.setItem(i,4,QTableWidgetItem(s.group.name))




    

app = QApplication([])
window = MainWindow()
window.show()
app.exec()