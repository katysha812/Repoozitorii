import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, 
    QComboBox, QRadioButton, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFormLayout
)

class UserInfoApp(QWidget):
    def __init__(self):
        super().__init__()

        self.MainUser()

    def MainUser(self):
        self.setWindowTitle('Анкетка')
        self.setGeometry(100, 100, 400, 300)

        self.surname_label = QLabel('Фамилия:')
        self.surname_input = QLineEdit()

        self.name_label = QLabel('Имя:')
        self.name_input = QLineEdit()

        self.otchestvo_label = QLabel('Отчество:')
        self.otchestvo_input = QLineEdit()

        self.favgame_label = QLabel('Любимая игра:')
        self.favgame_input = QLineEdit()

        self.city_label = QLabel('Город проживания:')
        self.city_input = QComboBox()
        self.city_input.addItems(['Абакан', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Москва'])

        self.favcolour_label = QLabel('Любимый цвет:')
        self.favcolour_input = QLineEdit()

        self.gender_label = QLabel('Пол:')
        self.male_radio = QRadioButton('Мужской')
        self.female_radio = QRadioButton('Женский')

        self.submit_button = QPushButton('Отправить')
        self.result_label = QLabel('Результаты будут отображены здесь')

        # Подключаем событие нажатия на кнопку
        self.submit_button.clicked.connect(self.display_info)

        # Создаем макеты
        form_layout = QFormLayout()
        form_layout.addRow(self.surname_label, self.surname_input)
        form_layout.addRow(self.name_label, self.name_input)
        form_layout.addRow(self.otchestvo_label, self.otchestvo_input)
        form_layout.addRow(self.favgame_label, self.favgame_input)
        form_layout.addRow(self.favcolour_label, self.favcolour_input)        
        form_layout.addRow(self.city_label, self.city_input)

        gender_layout = QHBoxLayout()
        gender_layout.addWidget(self.male_radio)
        gender_layout.addWidget(self.female_radio)
        form_layout.addRow(self.gender_label, gender_layout)

        form_layout.addRow(self.submit_button, self.result_label)

        self.setLayout(form_layout)

    def display_info(self):
        surname = self.surname_input.text()
        name = self.name_input.text()
        otchestvo = self.otchestvo_input.text()
        colour = self.favcolour_input.text()
        city = self.city_input.currentText()
        gender = 'Мужской' if self.male_radio.isChecked() else 'Женский' if self.female_radio.isChecked() else 'Не указан'
        game = self.favgame_input.text()
        
        result = f'Фамилия: {surname}\nИмя: {name}\nОтчество: {otchestvo}\nГород: {city}\nПол: {gender}\nЛюбимая игра: {game}\nЛЮбимый цвет: {colour}'
        self.result_label.setText(result)


app = QApplication(sys.argv)
user_info_app = UserInfoApp()
user_info_app.show()
sys.exit(app.exec())
