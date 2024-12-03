import sys
import os
import io

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import xml.etree.ElementTree as ET

class AssetData(QObject):

    changed = pyqtSignal()

    def __init__(self, project, name):
        super().__init__()
        self.__project = project
        self.__name = name
        self.__images: list[str] = []
        self.__aiModel = None
        self.__style = None
    
    def name(self):
        return self.__name

    def images(self) -> list[str]:
        return self.__images

    def addImage(self, image_path):
        image_path = image_path.replace("/", "\\")
        try:
            self.__images.index(image_path)
        except ValueError:
            self.__images.append(image_path)
            self.changed.emit()

    def deleteImage(self, image_path):
        image_path = image_path.replace("/", "\\")
        try:
            self.__images.remove(image_path)
            self.changed.emit()
        except ValueError:
            pass

    def aiModels(self):
        return ["Stable Difussion 1.5", "DALLE 3"]
    
    def aiStyles(self):
        return ["Cartoon", "Photoreal"]
    
    def setAiModel(self, index):
        pass

    def setStyle(self, index):
        pass

    @staticmethod
    def fromXmlElement(project, xml_element: ET.Element):
        asset = AssetData(project, xml_element.get("name"))
        asset.__aiModel = xml_element.get("model")
        asset.__style = xml_element.get("style")

        for image_path in xml_element.findall("ImagePath"):
            asset.addImage(image_path.text)

        return asset

    def serialize(self) -> ET.Element:
        item = ET.Element("Item")
        item.set("name", self.__name)

        for path in self.__images:
            x_path = ET.Element("ImagePath")
            x_path.text = path
            item.append(x_path)
        
        if self.__aiModel:
            item.set("model", self.__aiModel)
        if self.__style:
            item.set("style", self.__style)
        
        return item

class Project():
    def __init__(self, name, load=False):
        self.__name = name
        self.__path = self.constructPath(self.__name)
        self.__image_references_path = self.constructPath("Reference Images Directory")
        self.__project_file_path = self.constructPath("project.xml")
        self.__assets: list[AssetData] = []

        if load:
            self.__loadFromDisk()

    def name(self):                  return self.__name
    def path(self):                  return self.__path
    def image_references_path(self): return self.__image_references_path
    def project_file_path(self):     return self.__project_file_path

    def addAsset(self, name):
        match = list(filter(lambda x: x.name() == name, self.__assets))
        if len(match) > 0:
            raise Exception()
        else:
            asset = AssetData(self, name)
            self.__addAsset(asset)
            return asset
    
    def __addAsset(self, asset_data):
        self.__assets.append(asset_data)
    
    def addAssetXml(self, xml_element):
        asset = AssetData(self, xml_element)
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
    
    def constructPath(self, *extra: list[str]):
        home = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]
        return os.path.join(home, "MagicBox", self.__name, *extra)

    def __loadFromDisk(self):
        root = ET.parse(self.project_file_path()).getroot()
        for it in root.find("Assets").findall("Item"):
            asset = AssetData.fromXmlElement(self, it)
            self.__addAsset(asset)
    
    def __serializeAsXml(self):
        root = ET.fromstring("<MagicBox></MagicBox>")

        if len(self.assets()) == 0:
            return ET.tostring(root)
        
        xml_assets = ET.Element("Assets")
        for asset in self.assets():
            xml_assets.append(asset.serialize())
        root.append(xml_assets)
        
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
    
    @staticmethod
    def constructPath(*extra):
        loc = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.AppDataLocation)[0]
        path = os.path.join(loc, *extra)
        return path.replace('\\', '/')
    
    @staticmethod
    def randomProjectName():
        path = ProjectManager.constructPath()
        i = 1
        def_name = "MyProject"
        while True:
            path = os.path.join(path, def_name + str(i))
            if os.path.exists(path):
                i = i + 1
            else:
                return def_name + str(i)