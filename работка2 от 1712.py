import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit,  QFormLayout, QComboBox


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle('Sign Up Form')

        layout = QFormLayout()
        self.setLayout(layout)
        self.country_combo = QComboBox(self)
        self.country_combo.addItems(['Россия','Россииияя','Россссия', 'Рооооссия'])
        layout.addRow('Логин:', QLineEdit(self))
        layout.addRow('Пароль:', QLineEdit(self, echoMode=QLineEdit.EchoMode.Password))
        layout.addRow('Страна:', self.country_combo)

        layout.addRow(QPushButton('Войти'))
        layout.addRow(QPushButton('Забыли пароль?'))
        # show the window
        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
