import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableView, QVBoxLayout, QWidget, QLabel,
    QLineEdit, QPushButton, QComboBox, QDateEdit, QMessageBox,
    QHBoxLayout, QCheckBox, QSpinBox, QDialog, QFormLayout,
    QStackedWidget, QSplitter, QTabWidget
)
from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from models import Base, Проживающий, Паспорт, Бронь, Номер, Услуга, УслугаБрони, ТипНомера, Категория
from db import Session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphsDialog(QDialog):
    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setWindowTitle("Аналитика гостиницы")
        self.setGeometry(200, 200, 1000, 700)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.create_occupancy_tab()
        self.create_custom_tab()

    def create_occupancy_tab(self):
        occupancy_tab = QWidget()
        occupancy_layout = QVBoxLayout(occupancy_tab)
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Начальная дата:"))
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("Конечная дата:"))
        self.end_date = QDateEdit(QDate.currentDate())
        date_layout.addWidget(self.end_date)
        occupancy_layout.addLayout(date_layout)

        self.graph_type = QComboBox()
        self.graph_type.addItems(["Гистограмма", "Линейный график", "Круговая диаграмма"])
        occupancy_layout.addWidget(self.graph_type)

        self.plot_button = QPushButton("Построить график")
        self.plot_button.clicked.connect(self.plot_occupancy_graph)
        occupancy_layout.addWidget(self.plot_button)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        occupancy_layout.addWidget(self.canvas)

        self.tabs.addTab(occupancy_tab, "Заселяемость")

    def create_custom_tab(self):
        custom_tab = QWidget()
        custom_layout = QVBoxLayout(custom_tab)
        self.custom_graph_type = QComboBox()
        self.custom_graph_type.addItem("Гистограмма")
        custom_layout.addWidget(self.custom_graph_type)

        self.plot_button_custom = QPushButton("Построить график")
        self.plot_button_custom.clicked.connect(self.plot_custom_graph)
        custom_layout.addWidget(self.plot_button_custom)

        self.custom_figure = Figure()
        self.custom_canvas = FigureCanvas(self.custom_figure)
        custom_layout.addWidget(self.custom_canvas)

        self.tabs.addTab(custom_tab, "Распределение стоимости номеров")

    def plot_occupancy_graph(self):
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        graph_type = self.graph_type.currentText()
        bookings = self.session.query(Бронь).filter(
            Бронь.дата_заезда >= start_date,
            Бронь.дата_заезда <= end_date
        ).all()
        room_ids = [booking.id_номера for booking in bookings]
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if graph_type == "Гистограмма":
            ax.hist(room_ids, bins=len(set(room_ids)), rwidth=0.8)
            ax.set_xlabel("Номер комнаты")
            ax.set_ylabel("Количество бронирований")
            ax.set_title(f"Гистограмма заселяемости ({start_date} - {end_date})")
        elif graph_type == "Линейный график":
            room_counts = {}
            for room_id in room_ids:
                room_counts[room_id] = room_counts.get(room_id, 0) + 1
            sorted_rooms = sorted(room_counts.items())
            x = [room[0] for room in sorted_rooms]
            y = [room[1] for room in sorted_rooms]
            ax.plot(x, y, marker='o')
            ax.set_xlabel("Номер комнаты")
            ax.set_ylabel("Количество бронирований")
            ax.set_title(f"Линейный график заселяемости ({start_date} - {end_date})")
        elif graph_type == "Круговая диаграмма":
            room_counts = {}
            for room_id in room_ids:
                room_counts[room_id] = room_counts.get(room_id, 0) + 1
            labels = room_counts.keys()
            sizes = room_counts.values()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            ax.set_title(f"Круговая диаграмма заселяемости ({start_date} - {end_date})")
        self.canvas.draw()

    def plot_custom_graph(self):
        self.custom_figure.clear()
        ax = self.custom_figure.add_subplot(111)
        rooms = self.session.query(Номер).all()
        prices = [room.стоимость_сутки for room in rooms]
        ax.hist(prices, bins=10, color='skyblue', edgecolor='black')
        ax.set_xlabel("Стоимость номера за сутки")
        ax.set_ylabel("Количество номеров")
        ax.set_title("Распределение стоимости номеров")
        ax.grid(True)
        self.custom_canvas.draw()


class HotelApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("star4.png"))
        self.setWindowTitle("Гостиница")
        self.setGeometry(100, 100, 1000, 700)
        self.session = Session()
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        button_panel = QWidget()
        button_layout = QVBoxLayout(button_panel)
        button_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_clients = QPushButton("Клиенты")
        self.btn_rooms = QPushButton("Номерной фонд")
        self.btn_services = QPushButton("Доп. услуги")
        self.btn_bookings = QPushButton("Бронирования")
        self.btn_graphs = QPushButton("Графики")

        button_layout.addWidget(self.btn_clients)
        button_layout.addWidget(self.btn_rooms)
        button_layout.addWidget(self.btn_services)
        button_layout.addWidget(self.btn_bookings)
        button_layout.addWidget(self.btn_graphs)
        button_layout.addStretch()

        self.stacked_widget = QStackedWidget()
        splitter = QSplitter()
        splitter.addWidget(button_panel)
        splitter.addWidget(self.stacked_widget)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        splitter.setHandleWidth(1)

        main_layout.addWidget(splitter)

        self.create_clients_widget()
        self.create_rooms_widget()
        self.create_services_widget()
        self.create_bookings_widget()

        self.stacked_widget.addWidget(self.clients_widget)
        self.stacked_widget.addWidget(self.rooms_widget)
        self.stacked_widget.addWidget(self.services_widget)
        self.stacked_widget.addWidget(self.bookings_widget)

        self.btn_clients.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.clients_widget))
        self.btn_rooms.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.rooms_widget))
        self.btn_services.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.services_widget))
        self.btn_bookings.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.bookings_widget))
        self.btn_graphs.clicked.connect(self.open_graphs_dialog)

        self.stacked_widget.setCurrentIndex(0)
        self.load_clients()
        self.load_rooms()
        self.load_services()
        self.load_bookings()

    def create_clients_widget(self):
        self.clients_widget = QWidget()
        layout = QVBoxLayout(self.clients_widget)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Поиск:"))
        self.client_search = QLineEdit()
        self.client_search.setPlaceholderText("Фамилия, имя или телефон")
        filter_layout.addWidget(self.client_search)
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.filter_clients)
        filter_layout.addWidget(search_btn)
        add_btn = QPushButton("Добавить клиента")
        add_btn.clicked.connect(self.add_client_dialog)
        filter_layout.addWidget(add_btn)
        layout.addLayout(filter_layout)

        self.clients_model = QStandardItemModel()
        self.clients_model.setHorizontalHeaderLabels([
            "Фамилия", "Имя", "Отчество", "Адрес", "Телефон", "Почта", "Паспорт"
        ])
        self.clients_table = QTableView()
        self.clients_table.setModel(self.clients_model)
        self.clients_table.doubleClicked.connect(self.edit_client)
        layout.addWidget(self.clients_table)

    def filter_clients(self):
        filter_text = self.client_search.text().strip()
        self.load_clients(filter_text if filter_text else None)

    def load_clients(self, filter_text=None):
        query = self.session.query(Проживающий)
        if filter_text:
            query = query.filter(
                Проживающий.фамилия.ilike(f"%{filter_text}%") |
                Проживающий.имя.ilike(f"%{filter_text}%") |
                Проживающий.телефон.ilike(f"%{filter_text}%")
            )
        clients = query.order_by(Проживающий.фамилия).all()
        self.clients_model.setRowCount(0)
        for client in clients:
            passport_info = f"{client.паспорт.серия} {client.паспорт.номер}" if client.паспорт else ""
            row = [
                QStandardItem(client.фамилия),
                QStandardItem(client.имя),
                QStandardItem(client.отчество or ""),
                QStandardItem(client.адрес_проживания or ""),
                QStandardItem(client.телефон or ""),
                QStandardItem(client.почта or ""),
                QStandardItem(passport_info)
            ]
            self.clients_model.appendRow(row)

    def add_client_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить клиента")
        layout = QFormLayout(dialog)

        self.client_lastname = QLineEdit()
        self.client_firstname = QLineEdit()
        self.client_middlename = QLineEdit()
        self.client_address = QLineEdit()
        self.client_phone = QLineEdit()
        self.client_email = QLineEdit()

        self.passport_series = QLineEdit()
        self.passport_number = QLineEdit()
        self.passport_issued_by = QLineEdit()
        self.passport_issue_date = QDateEdit()
        self.passport_issue_date.setDate(QDate.currentDate())
        self.passport_birth_place = QLineEdit()

        layout.addRow("Фамилия:", self.client_lastname)
        layout.addRow("Имя:", self.client_firstname)
        layout.addRow("Отчество:", self.client_middlename)
        layout.addRow("Адрес:", self.client_address)
        layout.addRow("Телефон:", self.client_phone)
        layout.addRow("Email:", self.client_email)
        layout.addRow(QLabel("<b>Паспортные данные:</b>"))
        layout.addRow("Серия:", self.passport_series)
        layout.addRow("Номер:", self.passport_number)
        layout.addRow("Кем выдан:", self.passport_issued_by)
        layout.addRow("Дата выдачи:", self.passport_issue_date)
        layout.addRow("Место рождения:", self.passport_birth_place)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_client(dialog))
        btn_box.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.exec()

    def edit_client(self, index):
        surname_item = self.clients_model.item(index.row(), 0)
        name_item = self.clients_model.item(index.row(), 1)
        if not surname_item or not name_item:
            return
        surname = surname_item.text()
        name = name_item.text()
        client = self.session.query(Проживающий).filter_by(фамилия=surname, имя=name).first()

        if not client:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать клиента")
        layout = QFormLayout(dialog)

        self.client_lastname = QLineEdit(client.фамилия)
        self.client_firstname = QLineEdit(client.имя)
        self.client_middlename = QLineEdit(client.отчество or "")
        self.client_address = QLineEdit(client.адрес_проживания or "")
        self.client_phone = QLineEdit(client.телефон or "")
        self.client_email = QLineEdit(client.почта or "")

        passport = client.паспорт
        self.passport_series = QLineEdit(passport.серия if passport else "")
        self.passport_number = QLineEdit(passport.номер if passport else "")
        self.passport_issued_by = QLineEdit(passport.выдан if passport else "")
        self.passport_issue_date = QDateEdit()
        self.passport_issue_date.setDate(
            QDate.fromString(passport.дата_выдачи.strftime("%Y-%m-%d"), "yyyy-MM-dd") if passport else QDate.currentDate()
        )
        self.passport_birth_place = QLineEdit(passport.место_рожд if passport else "")

        layout.addRow("Фамилия:", self.client_lastname)
        layout.addRow("Имя:", self.client_firstname)
        layout.addRow("Отчество:", self.client_middlename)
        layout.addRow("Адрес:", self.client_address)
        layout.addRow("Телефон:", self.client_phone)
        layout.addRow("Email:", self.client_email)
        layout.addRow(QLabel("<b>Паспортные данные:</b>"))
        layout.addRow("Серия:", self.passport_series)
        layout.addRow("Номер:", self.passport_number)
        layout.addRow("Кем выдан:", self.passport_issued_by)
        layout.addRow("Дата выдачи:", self.passport_issue_date)
        layout.addRow("Место рождения:", self.passport_birth_place)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_client(dialog, client))
        btn_box.addWidget(save_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.delete_client(dialog, client))
        btn_box.addWidget(delete_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.exec()

    def save_client(self, dialog, client=None):
        try:
            if not self.client_lastname.text() or not self.client_firstname.text():
                raise ValueError("Фамилия и имя обязательны для заполнения")

            if client is None:
                client = Проживающий(
                    фамилия=self.client_lastname.text(),
                    имя=self.client_firstname.text(),
                    отчество=self.client_middlename.text() or None,
                    адрес_проживания=self.client_address.text() or None,
                    телефон=self.client_phone.text() or None,
                    почта=self.client_email.text() or None
                )
                self.session.add(client)
                self.session.flush()
            else:
                client.фамилия = self.client_lastname.text()
                client.имя = self.client_firstname.text()
                client.отчество = self.client_middlename.text() or None
                client.адрес_проживания = self.client_address.text() or None
                client.телефон = self.client_phone.text() or None
                client.почта = self.client_email.text() or None

            series = self.passport_series.text()
            number = self.passport_number.text()
            issued_by = self.passport_issued_by.text()
            issue_date = self.passport_issue_date.date().toPyDate()
            birth_place = self.passport_birth_place.text()

            if series and number and issued_by:
                if client.паспорт:
                    client.паспорт.серия = series
                    client.паспорт.номер = number
                    client.паспорт.выдан = issued_by
                    client.паспорт.дата_выдачи = issue_date
                    client.паспорт.место_рожд = birth_place
                else:
                    passport = Паспорт(
                        серия=series,
                        номер=number,
                        выдан=issued_by,
                        дата_выдачи=issue_date,
                        место_рожд=birth_place
                    )
                    client.паспорт = passport
                    self.session.add(passport)
            elif any([series, number, issued_by]):
                raise ValueError("Все поля паспорта должны быть заполнены.")

            self.session.commit()
            self.load_clients()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")
            self.session.rollback()

    def delete_client(self, dialog, client):
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить клиента {client.фамилия} {client.имя}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if client.паспорт:
                    self.session.delete(client.паспорт)
                self.session.delete(client)
                self.session.commit()
                self.load_clients()
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить клиента: {str(e)}")
                self.session.rollback()

    def create_rooms_widget(self):
        self.rooms_widget = QWidget()
        layout = QVBoxLayout(self.rooms_widget)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Тип номера:"))
        self.room_type_filter = QComboBox()
        self.room_type_filter.addItem("Все", None)
        types = self.session.query(ТипНомера).all()
        for t in types:
            self.room_type_filter.addItem(t.название, t.id)
        filter_layout.addWidget(self.room_type_filter)
        filter_layout.addWidget(QLabel("Категория:"))
        self.room_category_filter = QComboBox()
        self.room_category_filter.addItem("Все", None)
        categories = self.session.query(Категория).all()
        for c in categories:
            self.room_category_filter.addItem(c.название, c.id)
        filter_layout.addWidget(self.room_category_filter)
        search_btn = QPushButton("Фильтровать")
        search_btn.clicked.connect(self.filter_rooms)
        filter_layout.addWidget(search_btn)
        layout.addLayout(filter_layout)
        self.rooms_model = QStandardItemModel()
        self.rooms_model.setHorizontalHeaderLabels([
            "Тип", "Категория", "Комнаты", "Кровати", "Оснащение", "Цена/сутки"
        ])
        self.rooms_table = QTableView()
        self.rooms_table.setModel(self.rooms_model)
        layout.addWidget(self.rooms_table)

    def load_rooms(self, type_id=None, category_id=None):
        query = self.session.query(Номер)
        if type_id:
            query = query.filter(Номер.id_тип_номера == type_id)
        if category_id:
            query = query.filter(Номер.id_категории == category_id)
        rooms = query.all()
        self.rooms_model.setRowCount(0)
        for room in rooms:
            row = [
                QStandardItem(room.тип_номера.название),
                QStandardItem(room.категория.название),
                QStandardItem(str(room.колво_комнат)),
                QStandardItem(str(room.колво_кроватей)),
                QStandardItem(room.оснащение or ""),
                QStandardItem(str(room.стоимость_сутки))
            ]
            self.rooms_model.appendRow(row)

    def filter_rooms(self):
        type_id = self.room_type_filter.currentData()
        category_id = self.room_category_filter.currentData()
        self.load_rooms(type_id, category_id)
    
    def add_service_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить услугу")
        layout = QFormLayout(dialog)

        self.service_name = QLineEdit()
        self.service_description = QLineEdit()
        self.service_price = QSpinBox()
        self.service_price.setRange(0, 100000)
        self.service_price.setValue(100)

        layout.addRow("Название:", self.service_name)
        layout.addRow("Описание:", self.service_description)
        layout.addRow("Цена:", self.service_price)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_service(dialog))
        btn_box.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.exec()

    def save_service(self, dialog, service=None):
        try:
            name = self.service_name.text().strip()
            if not name:
                raise ValueError("Название услуги обязательно")

            price = self.service_price.value()
            
            if service is None:
                service = Услуга(
                    название=name,
                    описание=self.service_description.text().strip() or None,
                    цена=price
                )
                self.session.add(service)
            else:
                service.название = name
                service.описание = self.service_description.text().strip() or None
                service.цена = price

            self.session.commit()
            self.load_services()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить услугу: {str(e)}")
            self.session.rollback()
    
    def create_services_widget(self):
        self.services_widget = QWidget()
        layout = QVBoxLayout(self.services_widget)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Поиск:"))
        self.service_search = QLineEdit()
        self.service_search.setPlaceholderText("Название услуги")
        filter_layout.addWidget(self.service_search)
        search_btn = QPushButton("Найти")
        search_btn.clicked.connect(self.filter_services)
        filter_layout.addWidget(search_btn)
        add_btn = QPushButton("Добавить услугу")
        add_btn.clicked.connect(self.add_service_dialog)
        filter_layout.addWidget(add_btn)
        layout.addLayout(filter_layout)
        self.services_model = QStandardItemModel()
        self.services_model.setHorizontalHeaderLabels([
            "Название", "Описание", "Цена"
        ])
        self.services_table = QTableView()
        self.services_table.setModel(self.services_model)
        self.services_table.doubleClicked.connect(self.edit_service)
        layout.addWidget(self.services_table)

    def edit_service(self, index):
        name_item = self.services_model.item(index.row(), 0)
        if not name_item:
            return
        
        name = name_item.text()
        service = self.session.query(Услуга).filter_by(название=name).first()

        if not service:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать услугу")
        layout = QFormLayout(dialog)

        self.service_name = QLineEdit(service.название)
        self.service_description = QLineEdit(service.описание or "")
        self.service_price = QSpinBox()
        self.service_price.setRange(0, 100000)
        self.service_price.setValue(service.цена)

        layout.addRow("Название:", self.service_name)
        layout.addRow("Описание:", self.service_description)
        layout.addRow("Цена:", self.service_price)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_service(dialog, service))
        btn_box.addWidget(save_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.delete_service(dialog, service))
        btn_box.addWidget(delete_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.exec()

    def delete_service(self, dialog, service):
        reply = QMessageBox.question(
            self, "Подтверждение",
            f"Удалить услугу '{service.название}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.session.delete(service)
                self.session.commit()
                self.load_services()
                dialog.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить услугу: {str(e)}")
                self.session.rollback()
    
    def load_services(self, filter_text=None):
        query = self.session.query(Услуга)
        if filter_text:
            query = query.filter(Услуга.название.ilike(f"%{filter_text}%"))
        services = query.all()
        self.services_model.setRowCount(0)
        for service in services:
            row = [
                QStandardItem(service.название),
                QStandardItem(service.описание or ""),
                QStandardItem(str(service.цена))
            ]
            self.services_model.appendRow(row)

    def filter_services(self):
        filter_text = self.service_search.text().strip()
        self.load_services(filter_text if filter_text else None)

    def create_bookings_widget(self):
        self.bookings_widget = QWidget()
        layout = QVBoxLayout(self.bookings_widget)
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("С:"))
        self.booking_date_from = QDateEdit()
        self.booking_date_from.setDate(QDate.currentDate())
        filter_layout.addWidget(self.booking_date_from)
        filter_layout.addWidget(QLabel("По:"))
        self.booking_date_to = QDateEdit()
        self.booking_date_to.setDate(QDate.currentDate().addDays(30))
        filter_layout.addWidget(self.booking_date_to)
        filter_layout.addWidget(QLabel("Клиент:"))
        self.booking_client_filter = QComboBox()
        self.booking_client_filter.addItem("Все", None)
        clients = self.session.query(Проживающий).order_by(Проживающий.фамилия).all()
        for c in clients:
            self.booking_client_filter.addItem(f"{c.фамилия} {c.имя}", c.id)
        filter_layout.addWidget(self.booking_client_filter)
        search_btn = QPushButton("Фильтровать")
        search_btn.clicked.connect(self.filter_bookings)
        filter_layout.addWidget(search_btn)
        add_btn = QPushButton("Новое бронирование")
        add_btn.clicked.connect(self.add_booking_dialog)
        filter_layout.addWidget(add_btn)
        layout.addLayout(filter_layout)
        self.bookings_model = QStandardItemModel()
        self.bookings_model.setHorizontalHeaderLabels([
            "Клиент", "Номер", "Заезд", "Выезд", "Завтрак", "Ужин", "Услуги"
        ])
        self.bookings_table = QTableView()
        self.bookings_table.setModel(self.bookings_model)
        self.bookings_table.doubleClicked.connect(self.edit_booking)
        layout.addWidget(self.bookings_table)
     
    def edit_booking(self, index):
        # Получаем ID бронирования из первой колонки
        booking_id = int(self.bookings_model.item(index.row(), 0).text())
        booking = self.session.query(Бронь).get(booking_id)
        
        if not booking:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать бронирование")
        layout = QFormLayout()

        # Выбор клиента
        self.booking_client = QComboBox()
        clients = self.session.query(Проживающий).order_by(Проживающий.фамилия).all()
        current_client_index = 0
        for i, client in enumerate(clients):
            self.booking_client.addItem(f"{client.фамилия} {client.имя}", client.id)
            if client.id == booking.id_проживающего:
                current_client_index = i
        self.booking_client.setCurrentIndex(current_client_index)
        layout.addRow("Клиент:", self.booking_client)

        # Выбор номера
        self.booking_room = QComboBox()
        rooms = self.session.query(Номер).order_by(Номер.id).all()
        current_room_index = 0
        for i, room in enumerate(rooms):
            self.booking_room.addItem(f"№{room.id} ({room.тип_номера.название}, {room.стоимость_сутки} руб.)", room.id)
            if room.id == booking.id_номера:
                current_room_index = i
        self.booking_room.setCurrentIndex(current_room_index)
        layout.addRow("Номер:", self.booking_room)

        # Даты заезда и выезда
        self.booking_checkin = QDateEdit()
        self.booking_checkin.setDate(QDate.fromString(booking.дата_заезда.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        layout.addRow("Дата заезда:", self.booking_checkin)

        self.booking_checkout = QDateEdit()
        self.booking_checkout.setDate(QDate.fromString(booking.дата_выезда.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
        layout.addRow("Дата выезда:", self.booking_checkout)

        # Завтрак и ужин
        self.booking_breakfast = QCheckBox("Завтрак")
        self.booking_breakfast.setChecked(booking.завтрак)
        layout.addRow(self.booking_breakfast)

        self.booking_dinner = QCheckBox("Ужин")
        self.booking_dinner.setChecked(booking.ужин)
        layout.addRow(self.booking_dinner)

        # Дополнительные услуги
        layout.addRow(QLabel("<b>Дополнительные услуги:</b>"))

        services = self.session.query(Услуга).all()
        self.service_checkboxes = []
        self.service_counts = []

        existing_services = {ub.id_услуги: ub.колво_услуги for ub in booking.услуги}

        for service in services:
            cb = QCheckBox(service.название)
            cb.service_id = service.id
            self.service_checkboxes.append(cb)

            count = QSpinBox()
            count.setMinimum(1)
            count.setMaximum(10)
            count.setEnabled(False)
            self.service_counts.append(count)

            if service.id in existing_services:
                cb.setChecked(True)
                count.setValue(existing_services[service.id])
                count.setEnabled(True)

            # Включение/отключение спинбокса при изменении состояния чекбокса
            cb.toggled.connect(lambda checked, idx=len(self.service_checkboxes) - 1:
                            self.service_counts[idx].setEnabled(checked))

            service_layout = QHBoxLayout()
            service_layout.addWidget(cb)
            service_layout.addWidget(QLabel("Количество:"))
            service_layout.addWidget(count)
            layout.addRow(service_layout)

        # Кнопки
        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_booking(dialog, booking))
        btn_box.addWidget(save_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.clicked.connect(lambda: self.delete_booking(dialog, booking))
        btn_box.addWidget(delete_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.setLayout(layout)
        dialog.exec()
        
    def save_booking(self, dialog, booking=None):
        try:
            checkin = self.booking_checkin.date().toPyDate()
            checkout = self.booking_checkout.date().toPyDate()
            if checkin >= checkout:
                raise ValueError("Дата выезда должна быть позже даты заезда")

            client_id = self.booking_client.currentData()
            room_id = self.booking_room.currentData()

            if booking is None:
                booking = Бронь(
                    id_проживающего=client_id,
                    id_номера=room_id,
                    дата_заезда=checkin,
                    дата_выезда=checkout,
                    завтрак=self.booking_breakfast.isChecked(),
                    ужин=self.booking_dinner.isChecked()
                )
                self.session.add(booking)
                self.session.flush()
            else:
                booking.id_проживающего = client_id
                booking.id_номера = room_id
                booking.дата_заезда = checkin
                booking.дата_выезда = checkout
                booking.завтрак = self.booking_breakfast.isChecked()
                booking.ужин = self.booking_dinner.isChecked()

            # Удаление старых услуг
            self.session.query(УслугаБрони).filter_by(id_брони=booking.id).delete()

            # Добавление новых
            for i, cb in enumerate(self.service_checkboxes):
                if cb.isChecked():
                    service = УслугаБрони(
                        id_брони=booking.id,
                        id_услуги=cb.service_id,
                        колво_услуги=self.service_counts[i].value()
                    )
                    self.session.add(service)

            self.session.commit()
            self.load_bookings()
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить данные: {str(e)}")
            self.session.rollback()
        
    def add_booking_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Новое бронирование")
        layout = QFormLayout()

        self.booking_client = QComboBox()
        clients = self.session.query(Проживающий).order_by(Проживающий.фамилия).all()
        for c in clients:
            self.booking_client.addItem(f"{c.фамилия} {c.имя}", c.id)
        layout.addRow("Клиент:", self.booking_client)

        self.booking_room = QComboBox()
        rooms = self.session.query(Номер).order_by(Номер.id).all()
        for r in rooms:
            self.booking_room.addItem(f"№{r.id} ({r.тип_номера.название}, {r.стоимость_сутки} руб.)", r.id)
        layout.addRow("Номер:", self.booking_room)

        self.booking_checkin = QDateEdit()
        self.booking_checkin.setDate(QDate.currentDate())
        layout.addRow("Дата заезда:", self.booking_checkin)

        self.booking_checkout = QDateEdit()
        self.booking_checkout.setDate(QDate.currentDate().addDays(1))
        layout.addRow("Дата выезда:", self.booking_checkout)

        self.booking_breakfast = QCheckBox("Завтрак")
        layout.addRow(self.booking_breakfast)

        self.booking_dinner = QCheckBox("Ужин")
        layout.addRow(self.booking_dinner)

        layout.addRow(QLabel("<b>Дополнительные услуги:</b>"))
        services = self.session.query(Услуга).all()
        self.service_checkboxes = []
        self.service_counts = []

        for service in services:
            cb = QCheckBox(service.название)
            cb.service_id = service.id
            self.service_checkboxes.append(cb)
            count = QSpinBox()
            count.setMinimum(1)
            count.setMaximum(10)
            count.setEnabled(False)
            self.service_counts.append(count)

            # Включение/выключение спинбокса при изменении состояния чекбокса
            cb.toggled.connect(lambda checked, idx=len(self.service_checkboxes)-1:
                            self.service_counts[idx].setEnabled(checked))

            service_layout = QHBoxLayout()
            service_layout.addWidget(cb)
            service_layout.addWidget(QLabel("Количество:"))
            service_layout.addWidget(count)
            layout.addRow(service_layout)

        btn_box = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(lambda: self.save_booking(dialog))
        btn_box.addWidget(save_btn)

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(dialog.reject)
        btn_box.addWidget(cancel_btn)

        layout.addRow(btn_box)
        dialog.setLayout(layout)
        dialog.exec()
    def load_bookings(self, date_from=None, date_to=None, client_id=None):
        query = self.session.query(Бронь)
        if date_from and date_to:
            query = query.filter(
                (Бронь.дата_заезда >= date_from) &
                (Бронь.дата_выезда <= date_to)
            )
        if client_id:
            query = query.filter(Бронь.id_проживающего == client_id)
        bookings = query.order_by(Бронь.дата_заезда).all()
        self.bookings_model.setRowCount(0)
        for booking in bookings:
            services = ", ".join([ub.услуга.название for ub in booking.услуги])
            row = [
                QStandardItem(f"{booking.проживающий.фамилия} {booking.проживающий.имя}"),
                QStandardItem(str(booking.номер.id)),
                QStandardItem(booking.дата_заезда.strftime("%d.%m.%Y")),
                QStandardItem(booking.дата_выезда.strftime("%d.%m.%Y")),
                QStandardItem("Да" if booking.завтрак else "Нет"),
                QStandardItem("Да" if booking.ужин else "Нет"),
                QStandardItem(services)
            ]
            self.bookings_model.appendRow(row)

    def filter_bookings(self):
        date_from = self.booking_date_from.date().toPyDate()
        date_to = self.booking_date_to.date().toPyDate()
        client_id = self.booking_client_filter.currentData()
        self.load_bookings(date_from, date_to, client_id)

    def open_graphs_dialog(self):
        dialog = GraphsDialog(self.session, self)
        dialog.exec()


def load_styles():
    try:
        with open('styles.qss', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print("Файл стилей не найден, используются стандартные стили")
        return ""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    style = load_styles()
    if style:
        app.setStyleSheet(style)
    window = HotelApp()
    window.show()
    sys.exit(app.exec())