from PyQt5.QtWidgets import (
    QWidget, 
    QApplication, 
    QPushButton, 
    QMainWindow, 
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget
)
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon("картиночка.png"))
        self.setWindowTitle("Учим стил1")
        self.setGeometry(100, 100, 800, 600)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        label = QLabel("Красивый цвет")
        label.setStyleSheet(
        """
        QLabel {
                color #333333;
                font-size:18px;
                font-weight:bold;
                background-color: #f5f5f5;
                padding:5px;
                border:1px solid #cccccc;
                border-radius:3px;
        }
        """
        )
        layout.addWidget(label)
        
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("введите текст...")
        line_edit.setStyleSheet(
            """
            QLineEdit{
                background-color: white;
                border: 2x solid #2196f3;
                border-radius:5px;
                padding: 5px;
                font-size:14px;
            }
            QLineEdit:focus{
                border: 2px solid #1976d2;
            }
            """
        )
        layout.addWidget(line_edit)
        
        combo_box = QComboBox()
        combo_box.addItems(["Первая", "Вторая", "Третья"])
        combo_box.setStyleSheet(
            """ 
            QComboBox{
                background-color: #ffffff;
                border: 1x solid #cccccc;
                border-radius:5px;
                padding: 5px;
                font-size:14px;
            }
            QComboBox:hover{
                background-color: #f0f0f0
            }
            QComboBox::drop-down{
                border: none;
            }
            QComboBox QAbstractItemView{
                background-color: #ffffff;
                selection-background-color: #2196f3;
                selection-color: white;
            }
            """
        )
        layout.addWidget(combo_box)
        
        table = QTableWidget()
        table.setStyleSheet(
            """ 
            QTableWidget{
                background-color: #ffffff;
                gridline-color: #cccccc;
                border: 1x solid #cccccc;
            }
            QTableWidget::item{
                padding: 5px;
            }
            QTableWidget::item:selected{
                background-color: #2196f3;
                color: white;
            }
            QHeaderView::section{
                background-color: #e0e0e0;
                padding: 5px;
                border: 1px solid #cccccc;
            }
            """
        )
        layout.addWidget(table)
        #self.setStyleSheet("background-color: #E0E0E0;")
        
        # self.setStyleSheet(
        #     """
        #     QMainWindow{
        #      background: qradialgradient(
        #          cx:0.5, cy:0.5, radius:1,
        #          fx:0.5, fy:0.5,
        #          stop:0 #ff9800
        #          stop:1 #00b74d
        #      )
        #  }
        #     """
        # """
        # QMainWindow{
        #     background: qlineargradient(
        #         x1:0, y1:0, x2:1, y2:1,
        #         stop:0 #2196f3
        #         stop:1 #64b5f6
        #     )
        # }
        # """
        # )
        
        # widget = QWidget()
        # self.setCentralWidget(widget)
        # layout = QVBoxLayout(widget)
        
        # first_btn = QPushButton("Первани")
        # second_btn = QPushButton("Вторани")
        # layout.addWidget(first_btn)
        # layout.addWidget(second_btn)
        
        # first_btn.setStyleSheet("""
        #                         QPushButton {
        #                             background-color: #4CAF50;
        #                             color: white;
        #                             padding:10px;
        #                             border-radius:5px;
        #                             font-size:16px;
        #                         }
        #                         QPushButton:hover{
        #                             background-color: #45A049;
        #                         }
        #                         QPushButton:pressed{
        #                             background-color: #3d8b40;
        #                         }    
        #                         """)
        # second_btn.setStyleSheet("""
        #                         QPushButton {
        #                             background-color: #F44336;
        #                             color: white;
        #                             padding:10px;
        #                             border-radius:5px;
        #                             font-size:16px;
        #                         }
        #                         QPushButton:hover{
        #                             background-color: #Da190b;
        #                         }
        #                         QPushButton:pressed{
        #                             background-color: #C11300;
        #                         }    
        #                         """)
        
app = QApplication([])
app.setStyleSheet("""
                  QPushButton {
                      background-color: #2196F3;
                      color: white;
                      padding:8px;
                      border-radius:4px;
                  }
                  QPushButton:hover{
                      background-color: #1976d2;
                  }
                  """)
window = MainWindow()
window.show()
app.exec()
