import sys
import random
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from project_manager import *
from basic_dialog import *

class Asset(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        left_panel = QVBoxLayout()

class Dashboard(QWidget):
    def __init__(self, app, project, parent):
        super().__init__(parent)
        self.app = app
        self.project = project
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setupMenu()
        self.setupTabs()
    
    def setupMenu(self):
        menu = self.app.window.menuBar()
        menu_file = menu.addMenu("File")
        menu_asset = menu.addMenu("Assets")

        action_asset_new = QAction("New", self)
        action_asset_new.triggered.connect(self.newAsset)
        menu_asset.addAction(action_asset_new)

        action_asset_save = QAction("Save", self)
        action_asset_save.triggered.connect(self.saveAsset)
        menu_asset.addAction(action_asset_save)

    def setupTabs(self):
        self.tabs = QTabWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.tabs)
        for asset in self.project.assets():
            self.tabs.addTab(QWidget(), asset["name"])
    
    def newAsset(self):
        widget = QWidget()
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(QLabel("Asset Name"))
        asset_name = QLineEdit()
        asset_name.setValidator(QRegularExpressionValidator(ProjectManager.assetNameRegex()))
        widget.layout().addWidget(asset_name)
        dialog = BasicDialog(widget, "Create New Asset", self)

        def onClose(create: bool):
            if create:
                self.project.addAsset(asset_name.text())
                self.tabs.addTab(Asset(), asset_name.text())
                self.project.save()

        dialog.onClose.connect(onClose)
    
    def saveAsset(self):
        pass