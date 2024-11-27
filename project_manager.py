import sys
import os
import io

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import xml.etree.ElementTree as ET

class Project():
    def __init__(self, name, load=False):
        self.__name = name
        self.__path = os.path.join(ProjectManager.globalPath(), self.__name)
        self.__image_references_path = os.path.join(self.__path, "Reference Images Directory")
        self.__project_file_path = os.path.join(self.__path, "project.xml")
        self.__assets = []

        if load:
            self.__loadFromDisk()

    def name(self):                  return self.__name
    def path(self):                  return self.__path
    def image_references_path(self): return self.__image_references_path
    def project_file_path(self):     return self.__project_file_path

    def addAsset(self, name):
        asset = {}
        asset["name"] = name
        self.__assets.append(asset)
        return asset
    
    def assets(self):
        return self.__assets

    def save(self):
        if not os.path.exists(self.path()):
            os.makedirs(self.path())
            os.mkdir(self.image_references_path())
        file = os.open(self.project_file_path(), os.O_RDWR | os.O_CREAT)
        os.write(file, self.__serializeAsXml())
        os.close(file)

    def __loadFromDisk(self):
        root = ET.parse(self.project_file_path()).getroot()
        for asset in root.find("Assets").findall("Item"):
            self.addAsset(asset.get("name"))
    
    def __serializeAsXml(self):
        if len(self.assets()) == 0:
            return b"<?xml version=\"1.0\"?>"
        
        root = ET.fromstring("<MagicBox></MagicBox>")
        root.append(ET.Element("Assets"))
        xml_assets = root.find("Assets")

        for asset in self.assets():
            e = ET.Element("Item", {"name": asset["name"]})
            xml_assets.append(e)
        
        return ET.tostring(root)

class ProjectManager():

    @staticmethod
    def globalPath():
        home = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]
        return os.path.join(home, "MagicBox")

    @staticmethod
    def newProject(name: str) -> Project | None:
        if not ProjectManager.isProjectNameValid(name):
            return None
        proj = Project(name)
        proj.save()
        return proj
    
    @staticmethod
    def openProject(name: str) -> Project | None:
        if not ProjectManager.isProjectNameValid(name):
            return None
        try:
            proj = Project(name, load=True)
            return proj
        except:
            return None

    @staticmethod
    def listProjects() -> list[str]:
        dirs = []
        for path in os.listdir(ProjectManager.globalPath()):
            abs_path = os.path.join(ProjectManager.globalPath(), path)
            if os.path.isdir(abs_path) and os.path.exists(os.path.join(abs_path, "project.xml")):
                dirs.append(path)
        return dirs

    @staticmethod
    def projectNameRegex():
        return QRegularExpression("^[A-Za-z_][A-Za-z0-9_]*$")
    
    @staticmethod
    def assetNameRegex():
        return QRegularExpression("^[A-Za-z_][A-Za-z0-9_]*$")
    
    @staticmethod
    def isProjectNameValid(name: str):
        return ProjectManager.projectNameRegex().match(name).hasMatch()

    @staticmethod
    def isAssetNameValid(name: str):
        return ProjectManager.assetNameRegex().match(name).hasMatch()