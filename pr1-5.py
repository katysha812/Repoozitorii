import sys
import json
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QComboBox

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
        self.setGeometry(100, 100, 350, 150)

        layout = QVBoxLayout()

        self.temp_selector = QComboBox()
        self.temp_selector.addItems(["Минимальная температура", "Максимальная температура", "Средняя температура"])
        self.temp_selector.currentIndexChanged.connect(self.update_table)
        layout.addWidget(self.temp_selector)

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        self.weather_data = weather_data 
        self.update_table() 

        self.setLayout(layout)

    def update_table(self):
        selected_index = self.temp_selector.currentIndex()
        if selected_index == 0: 
            filtered_data = self.get_min_temperature()
        elif selected_index == 1:  
            filtered_data = self.get_max_temperature()
        else: 
            filtered_data = self.get_average_temperature()

        self.populate_table(filtered_data)

    def populate_table(self, weather_data):
        self.table_widget.setRowCount(len(weather_data))
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(['Город', 'Температура', 'Единицы'])

        for i, weather in enumerate(weather_data):
            self.table_widget.setItem(i, 0, QTableWidgetItem(weather.city()))
            self.table_widget.setItem(i, 1, QTableWidgetItem(str(weather.temperature())))
            self.table_widget.setItem(i, 2, QTableWidgetItem(weather.unit()))

    def get_min_temperature(self):
        min_temp = min(self.weather_data, key=lambda w: w.temperature())
        return [min_temp]

    def get_max_temperature(self):
        max_temp = max(self.weather_data, key=lambda w: w.temperature())
        return [max_temp]

    def get_average_temperature(self):
        avg_temp = sum(w.temperature() for w in self.weather_data) / len(self.weather_data)
        if self.weather_data:
            unit = self.weather_data[0].unit() 
        else:
            unit = ""
        return [Weather("Средняя температура", avg_temp, unit)]

def load_weather_data(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        data = json.load(file)

    weather = []
    for item in data:
        city = item.get('city')
        temperature = item.get('temperature')
        unit = item.get('unit')
        weather.append(Weather(city, temperature, unit))

    return weather

app = QApplication(sys.argv)

file_path = r"/home/KHPK.RU/student/Загрузки/data.json"
weather_data = load_weather_data(file_path)

main_window = WeatherApp(weather_data)
main_window.show()

sys.exit(app.exec())