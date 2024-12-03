from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QSize

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MagicBox")
        #self.resize(QSize(1200, 800))