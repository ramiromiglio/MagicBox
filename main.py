import sys
import random
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from project_manager import *
from basic_dialog import *
from main_menu import *
from dashboard import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MagicBox")
        self.setFixedSize(QSize(800, 600))

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.window = MainWindow()
        self.view = MainMenu(self.window)
        self.view.onCreate.connect(self.createAndOpen)
        self.view.onOpen.connect(self.openExistingProject)
        self.window.setCentralWidget(self.view)
        self.window.show()
    
    def createAndOpen(self, name: str):
        self.project = ProjectManager.newProject(name)
        if self.project != None:
            self.view.deleteLater()
            self.view = Dashboard(self, self.project, self.window)
            self.window.setCentralWidget(self.view)

    def openExistingProject(self, name: str):
        self.project = ProjectManager.openProject(name)
        if self.project != None:
            self.view.deleteLater()
            self.view = Dashboard(self, self.project, self.window)
            self.window.setCentralWidget(self.view)
        
def main():
    app = App(sys.argv)
    app.exec()

if __name__ == '__main__':
    main()