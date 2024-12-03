import sys
import random
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from project import *
from basic_dialog import *

class CreateProjectDialog(QDialog):

    signal_Create = pyqtSignal(str)

    def __init__(self, parent, menu):
        super().__init__(parent)

        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)

        proj_path = QLabel(self)
        proj_images = QLabel(self)

        def slot_projectNameChanged(text):
            proj_path.setText(ProjectManager.constructPath(text, text + ".xml"))
            proj_images.setText(ProjectManager.constructPath(text, "Reference Images Directory/"))

        proj_name = QLineEdit(self)
        proj_name.setValidator(QRegularExpressionValidator(ProjectManager.projectNameRegex()))
        proj_name.textChanged.connect(slot_projectNameChanged)
        proj_name.setText(ProjectManager.randomProjectName())

        dialog = QDialog(self)

        def slot_Click():
            if proj_name.text() != "":
                self.signal_Create.emit(proj_name.text())
                dialog.accept()
            else:
                dialog = QDialog(self)
                dialog.setLayout(QVBoxLayout())
                dialog.layout().addWidget(QLabel("The project name can't be empty", dialog))
                dialog.exec()

        button = QPushButton("Create", self)
        button.clicked.connect(slot_Click)

        layout.addRow("Project Name", proj_name)
        layout.addRow("Project Location", proj_path)
        layout.addRow("Reference images", proj_images)
        layout.addRow(button)

        dialog.setWindowTitle("Create New Project")
        dialog.setLayout(layout)
        dialog.exec()

class MainMenu(QWidget):

    signal_CreateProject = pyqtSignal(str)
    signal_LoadProject = pyqtSignal(str)

    def __init__(self, parent):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        def slot_CreateProject():
            dialog = CreateProjectDialog(self)
            dialog.signal_Create.connect(lambda s: self.signal_CreateProject.emit(s))

        def slot_LoadProject():
            layout = QVBoxLayout()
            layout.setContentsMargins(30, 30, 30, 30)

            dialog = QDialog(self)

            def open():
                proj = self.sender().property('project_name')
                dialog.accept()
                self.signal_LoadProject.emit(proj)

            for proj in ProjectManager.listProjects():
                button = QPushButton(proj)
                button.clicked.connect(open)
                button.setProperty('project_name', proj)
                layout.addWidget(button)
            
            dialog.setWindowTitle("Open Project")
            dialog.setLayout(layout)
            dialog.exec()

        w = QWidget(self)
        w.setLayout(QVBoxLayout())
        w.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout.addWidget(w)

        button = QPushButton("Create New Project")
        button.clicked.connect(slot_CreateProject)
        button.setStyleSheet("padding: 10px 12px;")
        w.layout().addWidget(button)
        button = QPushButton("Load Project")
        button.clicked.connect(slot_LoadProject)
        button.setStyleSheet("padding: 10px 12px;")
        w.layout().addWidget(button)