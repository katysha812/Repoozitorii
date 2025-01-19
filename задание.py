import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Счетчик нажатий")
        
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        self.layout = QVBoxLayout()

        self.counter = 0

        self.button = QPushButton("Тыкать сюда", self)
        self.button.clicked.connect(self.counter_label) 

        self.label = QLabel("0", self)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.button)

        self.widget.setLayout(self.layout)

    def counter_label(self):
        """Увеличивает счетчик и обновляет текст в метке."""
        self.counter += 1
        self.label.setText(str(self.counter))

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
