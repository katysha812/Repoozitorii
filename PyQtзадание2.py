import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QComboBox, QCheckBox, QRadioButton, QGroupBox

class TextStyleApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Стилечек для текста")
        self.setGeometry(300, 300, 300, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.label = QLabel("Пример текста")
        self.layout.addWidget(self.label)

        self.color_combo = QComboBox(self)
        self.color_combo.addItems(["Черный", "Красный", "Зеленый", "Синий", "Фиолетовый", "Розовый","Коричневый","Вишневый"])
        self.color_combo.currentTextChanged.connect(self.update_text_style)
        self.layout.addWidget(self.color_combo)

        self.bold_checkbox = QCheckBox("Жирный", self)
        self.bold_checkbox.stateChanged.connect(self.update_text_style)
        self.layout.addWidget(self.bold_checkbox)

        self.italic_checkbox = QCheckBox("Курсив", self)
        self.italic_checkbox.stateChanged.connect(self.update_text_style)
        self.layout.addWidget(self.italic_checkbox)

        self.size_group = QGroupBox("Размер текста", self)
        self.size_layout = QVBoxLayout()

        self.small_radio = QRadioButton("Маленький")
        self.small_radio.toggled.connect(self.update_text_style)
        self.size_layout.addWidget(self.small_radio)

        self.medium_radio = QRadioButton("Средний")
        self.medium_radio.setChecked(True) 
        self.medium_radio.toggled.connect(self.update_text_style)
        self.size_layout.addWidget(self.medium_radio)

        self.large_radio = QRadioButton("Большой")
        self.large_radio.toggled.connect(self.update_text_style)
        self.size_layout.addWidget(self.large_radio)

        self.size_group.setLayout(self.size_layout)
        self.layout.addWidget(self.size_group)

        self.central_widget.setLayout(self.layout)
        self.update_text_style()

    def update_text_style(self):
        """Обновляет стиль текста метки на основе выбранных параметров"""
        color = self.color_combo.currentText().lower()
        if color == "черный":
            color = "black"
        elif color == "красный":
            color = "red"
        elif color == "зеленый":
            color = "green"
        elif color == "синий":
            color = "blue"
        elif color == "розовый":
            color = "pink"
        elif color == "коричневый":
            color = "brown"
        elif color == "вишневый":
            color = "crimson"
        elif color == "фиолетовый":
            color = "purple"

        font_style = ""
        if self.bold_checkbox.isChecked():
            font_style += "font-weight: bold; "
        if self.italic_checkbox.isChecked():
            font_style += "font-style: italic; "

        if self.small_radio.isChecked():
            font_size = "12px"
        elif self.medium_radio.isChecked():
            font_size = "16px"
        else:
            font_size = "20px"

        self.label.setStyleSheet(f"color: {color}; {font_style} font-size: {font_size};")

app = QApplication(sys.argv)
window = TextStyleApp()
window.show()
sys.exit(app.exec())
