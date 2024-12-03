import sys

from PyQt6.QtWidgets import *
from PyQt6.QtCore    import *
from PyQt6.QtGui     import *

from menu   import MainMenu
from dashboard   import DashboardWidget
from window import MainWindow
from project import ProjectManager

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.__window = MainWindow()
        self.__view = MainMenu(self.__window)        
        self.__view.signal_CreateProject.connect(self.createProject)
        self.__view.signal_LoadProject.connect(self.loadProject)
        self.__project = None
        self.__window.setCentralWidget(self.__view)
        self.__window.showMaximized()
    
    def createProject(self, name):
        self.__project = ProjectManager.newProject(name)
        if self.__project:
            self.__view.deleteLater()
            self.__view = DashboardWidget(self)
            self.__window.setCentralWidget(self.__view)

    def loadProject(self, name):
        self.__project = ProjectManager.openProject(name)
        if self.__project:
            self.__view.deleteLater()
            self.__view = DashboardWidget(self)
            self.__window.setCentralWidget(self.__view)
    
    def project(self):
        return self.__project
    
    def window(self):
        return self.__window

if __name__ == '__main__':
    app = App(sys.argv)
    app.exec()