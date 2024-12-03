import sys
import random
import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from project import *
from basic_dialog import *
from asset import *

class DashboardWidget(QWidget):

    def __init__(self, app):
        super().__init__()
        self.setLayout(QVBoxLayout())        
        self.__app = app
        self.__menu = app.window().menuBar()
        self.__tabs = QTabWidget(self)        
        self.layout().addWidget(self.__tabs)
        self.setupMenu()
        self.setupTabs()
    
    def setupMenu(self):
        # File menu
        file_menu = self.__menu.addMenu("Project")
        save = QAction("Save", self)
        save.triggered.connect(self.saveProject)
        file_menu.addAction(save)

        # Asset menu
        menu = self.__menu.addMenu("Asset")
        new = QAction("New", self)
        new.triggered.connect(self.newAsset)
        menu.addAction(new)
        save = QAction("Save", self)
        save.triggered.connect(self.saveAsset)
        menu.addAction(save)

    def setupTabs(self):
        self.update()
    
    def newAsset(self):
        asset_name = QLineEdit(self)
        asset_name.setValidator(QRegularExpressionValidator(ProjectManager.assetNameRegex()))

        def slot_CreateAsset():
            name = asset_name.text()
            self.__app.project().addAsset(name)
            self.update()

        widget = QWidget() # The parent will be BasicDialog
        widget.setLayout(QHBoxLayout())
        widget.layout().addWidget(QLabel("Asset Name", widget))
        widget.layout().addWidget(asset_name)
        dialog = BasicDialog(widget, "Create New Asset", self)
        dialog.signal_Accept.connect(slot_CreateAsset)
    
    def saveAsset(self):
        pass

    def saveProject(self):
        self.__app.project().save()

    def update(self):
        for asset_data in self.__app.project().assets():
            found = False
            # Inserto unicamente las tabs que no existen en QTabWidget
            for i in range(self.__tabs.count()):
                w: AssetWidget = self.__tabs.widget(i)
                if w.assetData().name() == asset_data.name():
                    found = True
                    break
            if not found:
                self.__tabs.addTab(AssetWidget(asset_data), asset_data.name())

            #path = "C:/Users/Ramiro/Desktop/MagicBox/images"
            #for file in os.listdir(path):
            #    asset_data.addImage(os.path.join(path, file))
