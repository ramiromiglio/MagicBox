from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class BasicDialog(QDialog):
    signal_Reject = pyqtSignal()
    signal_Accept = pyqtSignal()
    signal_Close = pyqtSignal(bool)

    def __init__(self, widget, buttonText, parent):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        widget.setParent(self)
        self.layout().addWidget(widget)
        button = QPushButton(buttonText, self)
        button.clicked.connect(self.onButtonClick)
        self.layout().addWidget(button)
        self.show()
    
    def onButtonClick(self):
        self.signal_Accept.emit()
        self.signal_Close.emit(True)
        self.accept()

    def closeEvent(self, e):
        self.signal_Reject.emit()
        self.signal_Close.emit(False)