import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QSpinBox, QRadioButton,QHBoxLayout

class Weather:
    def __init__(self, city, temperature, unit):
        self.__city = city
        self.__temperature = temperature
        self.__unit = unit

    def city(self):
        return self.__city

    def temperature(self):
        return self.__temperature

    def unit(self):
        return self.__unit

class WeatherApp(QWidget):
    def __init__(self, weather_data):
        super().__init__()
        self.setWindowTitle("Данные о погоде")
        self.setGeometry(100, 100, 350, 350)
        self.original_data = weather_data

        layout = QVBoxLayout()

        self.threshold_spinbox = QSpinBox()
        self.threshold_spinbox.setRange(-100, 100)
        self.threshold_spinbox.valueChanged.connect(self.filter_data)
        layout.addWidget(self.threshold_spinbox)

        self.radio_layout = QHBoxLayout()
        self.radio_vishe = QRadioButton("Выше")
        self.radio_vishe.setChecked(True)
        self.radio_nize = QRadioButton("Ниже")

        self.radio_vishe.toggled.connect(self.filter_data)
        self.radio_nize.toggled.connect(self.filter_data)

        self.radio_layout.addWidget(self.radio_vishe)
        self.radio_layout.addWidget(self.radio_nize)
        layout.addLayout(self.radio_layout)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        self.setLayout(layout)
        self.filter_data()


    def filter_data(self):
        threshold = self.threshold_spinbox.value()

        if self.radio_vishe.isChecked():
            filtered_data = [w for w in self.original_data if w.temperature() > threshold]
        else:
            filtered_data = [w for w in self.original_data if w.temperature() < threshold]

        self.populate_table(filtered_data)

    def populate_table(self, weather_data):
        self.table_widget.setRowCount(len(weather_data))
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['Город', 'Температура', 'Единицы'])

        for i, weather in enumerate(weather_data):
            self.table_widget.setItem(i, 0, QTableWidgetItem(weather.city()))
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(weather.temperature())))
            self.table_widget.setItem(i, 2, QTableWidgetItem(weather.unit()))
    
    


def load_weather_data(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    weather_list = []
    for item in data:
        city = item.get('city')
        temperature = item.get('temperature')
        unit = item.get('unit')
        weather = Weather(city, temperature, unit)
        weather_list.append(weather)

    return weather_list

app = QApplication(sys.argv)

file_path = r"/home/KHPK.RU/student/Загрузки/data.json" 
weather_data = load_weather_data(file_path)

main_window = WeatherApp(weather_data)
main_window.show()

sys.exit(app.exec())