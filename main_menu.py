import sys
import random
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from project_manager import *
from basic_dialog import *

class MainMenu(QWidget):

    onCreate = pyqtSignal(str)
    onOpen = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        layout = QVBoxLayout()

        button = QPushButton("Create New Project")
        button.clicked.connect(self.onClickCreateNewProject)
        layout.addWidget(button)
        button = QPushButton("Load Project")
        button.clicked.connect(self.onClickLoadProject)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(widget)
    
    def projectPath(self, *extra):
        loc = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppDataLocation)[0]
        path = os.path.join(loc, *extra)
        return path.replace('\\', '/')

    def _projectNameChanged(self, text):
        self.project_path.setText(self.projectPath(text, text + ".xml"))
        self.project_images_path.setText(self.projectPath(text, "Reference Images Directory/"))

    def getNewProjectName(self):
        path = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppDataLocation)[0]
        i = 1
        def_name = "MyProject"
        while True:
            path = os.path.join(path, def_name + str(i))
            if os.path.exists(path):
                i = i + 1
            else:
                return def_name + str(i)

    def onClickCreateNewProject(self):        

        layout = QGridLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        name_validator = QRegularExpressionValidator(QRegularExpression("^[A-Za-z_][A-Za-z0-9_]*$"))

        self.project_path = QLabel()
        self.project_images_path = QLabel()
        self.project_name = QLineEdit()
        self.project_name.setValidator(name_validator)
        self.project_name.textChanged.connect(self._projectNameChanged)
        self.project_name.setText(self.getNewProjectName())

        def onCreate():
            project_name = self.project_name.text()

            if project_name != "":
                self.onCreate.emit(project_name)
            else:
                dialog = QDialog(self)
                QLabel("The project name can't be empty", dialog)
                dialog.exec()

        button_create = QPushButton("Create")
        button_create.clicked.connect(onCreate)

        widgets = [
            QLabel("Project Name"), self.project_name,
            QLabel("Project Location"), self.project_path,
            QLabel("Reference Images"), self.project_images_path,
            button_create, 2
        ]

        assert(len(widgets) % 2 == 0)

        r = 0
        i = 0        

        while i < len(widgets):
            w = widgets[i]
            x = widgets[i + 1]

            if isinstance(x, QWidget):
                layout.addWidget(w, r, 0)
                layout.addWidget(x, r, 1)
            else:
                assert(isinstance(x, int))
                layout.addWidget(w, r, 0, 1, x)

            r = r + 1
            i = i + 2

        dialog = QDialog(self)
        button_create.setProperty("dialog", dialog)
        dialog.setWindowTitle("Create New Project")
        dialog.setLayout(layout)
        dialog.exec()
    

    def onClickLoadProject(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        dialog = QDialog(self)

        def open():
            proj = self.sender().property('project_name')
            dialog.accept()
            self.onOpen.emit(proj)

        for proj in ProjectManager.listProjects():
            button = QPushButton(proj)
            button.clicked.connect(open)
            button.setProperty('project_name', proj)
            layout.addWidget(button)
        
        dialog.setWindowTitle("Open Project")
        dialog.setLayout(layout)
        dialog.exec()