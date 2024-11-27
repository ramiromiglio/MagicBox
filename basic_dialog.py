from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class BasicDialog(QDialog):
    onClose = pyqtSignal(bool)

    def __init__(self, widget, buttonText, parent):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        if widget:
            self.layout().addWidget(widget)
        button = QPushButton(buttonText)
        button.clicked.connect(self.onButtonClick)
        self.layout().addWidget(button)
        self.show()
    
    def onButtonClick(self):
        self.onClose.emit(True)
        self.accept()

    def closeEvent(self, e):
        self.onClose.emit(False)