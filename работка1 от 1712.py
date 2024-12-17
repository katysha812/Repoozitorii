from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QWidget

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)

import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (QApplication, QMainWindow,QVBoxLayout, QGridLayout) 

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        layout5 = QGridLayout()
        #layout2.addWidget(Color("thistle"))
        layout1.addWidget(Color("powderblue"))
        layout3.addLayout(layout5)
        layout1.addLayout(layout2)
        layout2.addLayout(layout3)
        
        layout5.setContentsMargins(10,10,10,10)
        layout5.setSpacing(10)
        
        layout5.addWidget(Color("lightsteelblue"),0,0)
        layout5.addWidget(Color("powderblue"),1,0)
        layout5.addWidget(Color("slateblue"),2,0)
        layout5.addWidget(Color("thistle"),0,1)
        layout5.addWidget(Color("hotpink"),0,2)
        layout5.addWidget(Color("orchid"),1,1)
        layout5.addWidget(Color("powderblue"),1,2)
        layout5.addWidget(Color("lightsteelblue"),2,1)
        layout5.addWidget(Color("hotpink"),2,2)
        layout5.addWidget(Color("orchid"),0,3)
        layout5.addWidget(Color("powderblue"),1,3)
        layout5.addWidget(Color("lightsteelblue"),2,3)
        layout5.addWidget(Color("hotpink"),3,1)
        layout5.addWidget(Color("slateblue"),3,2)
        layout5.addWidget(Color("thistle"),3,3)
        layout5.addWidget(Color("orchid"),3,0)
        layout5.addWidget(Color("thistle"),3,2,1,2)
        
        layout2.addLayout(layout5)
        
        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()