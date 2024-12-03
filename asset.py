import os

from PyQt6.QtWidgets import *
from PyQt6.QtCore    import *
from PyQt6.QtGui     import *

from project import AssetData, ProjectManager

import rpack
from typing import Dict

from item_data_constants import ItemDataConstants

class AssetImagesSceneWidget(QGraphicsView):
    def __init__(self, asset_data: AssetData):
        super().__init__()
        self.__asset_data = asset_data
        self.__scene = QGraphicsScene()
        self.setScene(self.__scene)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setSceneRect(-10000, -10000, 20000, 20000)
    
    def wheelEvent(self, event):
        angle = event.angleDelta()
        if angle.y() > 0:
            wheel = 1.2
        else:
            wheel = 0.8
        self.scale(wheel, wheel)
    
    def focus(self, image_path):
        # First, deselect all
        for selected in self.__scene.selectedItems()[:]:
            selected.setSelected(False)

        fucused_items = list(filter(lambda item: item.data(ItemDataConstants.DATA_FILE_FULL_PATH) ==
                                    image_path, self.__scene.items()))
        if len(fucused_items) > 0:
            self.centerOn(fucused_items[0])
            fucused_items[0].setSelected(True)

    def update(self):
        sizes = []
        spacing = QPoint(40, 40)
        scene_images = list(map(lambda item: item.data(ItemDataConstants.DATA_FILE_FULL_PATH), self.__scene.items()))

        for image_path in self.__asset_data.images():
            if image_path not in scene_images:
                item = QGraphicsPixmapItem()                
                item.setData(ItemDataConstants.DATA_FILE_FULL_PATH, image_path)
                pixmap = QPixmap(image_path)
                item.setPixmap(pixmap)
                self.__scene.addItem(item)
                scene_images.append(image_path)
                item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
        
        # Remove useless items (deleted images)
        for item in self.__scene.items()[:]:
            image_path = item.data(ItemDataConstants.DATA_FILE_FULL_PATH)
            if image_path not in self.__asset_data.images():
                self.__scene.removeItem(item)
                del item

        # Pack pixmaps again
        for item in self.__scene.items():
            w = item.pixmap().width()
            h = item.pixmap().height()
            sizes.append( (w + spacing.x(), h + spacing.y()) )
        
        packed_sizes = rpack.pack(sizes)

        for i, item in enumerate(self.__scene.items()):
            old_pos = item.pos()
            new_pos = QPointF( float(packed_sizes[i][0]), float(packed_sizes[i][1]) )

            def slot_StepAnimation():
                oldValue = self.sender().property("OldValue")
                endValue = self.sender().property("EndValue")
                item = self.sender().property("Item")
                elapsed = self.sender().property("Elapsed")
                duration = self.sender().property("Duration")

                pos = oldValue + ((endValue - oldValue) * (elapsed / duration))
                item.setPos(pos)
                if (item.pos() - endValue).manhattanLength() < 1:
                    self.sender().stop()
                else:
                    elapsed = elapsed + 16
                    self.sender().setProperty("Elapsed", elapsed)
                    if elapsed >= duration:
                        self.sender().stop()
                        item.setPos(endValue)

            timer = QTimer(self)
            timer.timeout.connect(slot_StepAnimation)
            timer.setProperty("Item", item)
            timer.setProperty("OldValue", old_pos)
            timer.setProperty("EndValue", new_pos)
            timer.setProperty("Elapsed", 0)
            timer.setProperty("Duration", 1000)
            timer.start(16) # 60 FPS aprox.
    
    # TODO TODO TODO
    def mouseDoubleClickEvent(self, event):
        #print(event.pos())
        #pos = self.mapToScene(event.pos())
        #item = self.__scene.itemAt(pos.x(), pos.y(), self.transform())
        #if item is not None:
            #item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, True)
            #item.setSelected(True)
            #item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsSelectable, False)
        pass

class AssetPanelWidget(QWidget):    

    def __init__(self, asset_data: AssetData):
        super().__init__()
        self.setLayout(QHBoxLayout())
        self.__list_view = QListWidget()
        self.__list_view.setWindowTitle("Reference Images")
        self.__list_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.__list_view.customContextMenuRequested.connect(self.showContextMenuForImageList)
        self.__list_view.setMinimumWidth(150)
        self.__list_view.itemDoubleClicked.connect(self.focusImage)
        self.__images_scene = AssetImagesSceneWidget(asset_data)
        self.__asset_data = asset_data
        self.layout().addWidget(self.__list_view)
        self.layout().addWidget(self.__images_scene)
    
    def update(self):
        self.__images_scene.update()
        self.__list_view.clear()
        for image_path in self.__asset_data.images():
            item = QListWidgetItem(os.path.basename(image_path))
            item.setData(ItemDataConstants.DATA_FILE_FULL_PATH, image_path)
            icon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "image_icon.png"))
            item.setIcon(icon)
            self.__list_view.addItem(item)
    
    def showContextMenuForImageList(self, pos):
        menu = QMenu(self)
        if len(self.__list_view.selectedItems()) == 0:
            action = QAction("Add image", self)
            action.triggered.connect(self.addImage)
        else:
            action = QAction("Delete", self)
            action.triggered.connect(self.deleteImage)
        menu.addAction(action)
        menu.exec(self.__list_view.mapToGlobal(pos))
    
    def addImage(self):
        filepath = QFileDialog.getOpenFileName(self, "Open Image", None,
                                               "Image Files (*.png *.jpg *.bmp);;All files (*)")
        self.__asset_data.addImage(filepath[0])
    
    def deleteImage(self):
        filepath = self.__list_view.currentItem().data(ItemDataConstants.DATA_FILE_FULL_PATH)
        self.__asset_data.deleteImage(filepath)
    
    def focusImage(self, item):
        self.__images_scene.focus(item.data(ItemDataConstants.DATA_FILE_FULL_PATH))

class AssetWidget(QWidget):
    def __init__(self, asset_data: AssetData):
        super().__init__()

        self.__asset_data = asset_data
        self.__asset_data.changed.connect(self.update)
        self.__details = QWidget(self)
        self.__output = AssetPanelWidget(asset_data)
        self.__output.update()
        self.__tags: list[str] = []
        self.__tags_grid = QGridLayout()
        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self.__details)
        splitter.addWidget(self.__output)
        splitter.setSizes([1, 3])
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(splitter)
        self.setupDetails()
        self.setupOutput()
    
    def setupDetails(self):
        self.__details.setLayout(QVBoxLayout())

        # AI model
        self.__details.layout().addWidget(QLabel("Base Model", self))
        combo = QComboBox(self)
        for model in self.__asset_data.aiModels():
            combo.addItem(model)
        self.__details.layout().addWidget(combo)

        # Predefined AI styles
        self.__details.layout().addWidget(QLabel("Style", self))
        combo = QComboBox(self)
        for style in self.__asset_data.aiStyles():
            combo.addItem(style)
        self.__details.layout().addWidget(combo)       

        # Tags
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Tags", self))
        tags = QToolButton(self)
        layout.addWidget(tags)
        self.__details.layout().addLayout(layout)
        tags.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        tags.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons", "tag_icon.webp")))
        tags.triggered.connect(lambda action: self.addTag(action.text()))

        tagsMenu = QMenu("Tags", self)
        tags.setMenu(tagsMenu)
        for tag in ["Digital painting", "Hyper-realistic", "Portrait", "Landscape", "Fantasy", "Cyberpunk"]:
            action = QAction(tag, self)
            tagsMenu.addAction(action)
        
        self.__details.layout().addLayout(self.__tags_grid)

        self.__details.layout().addStretch(1)
        self.__details.layout().addWidget(QLabel("Prompt", self))
        prompt = QTextEdit()
        self.__details.layout().addWidget(prompt)
        button = QPushButton("Imagine")
        self.__details.layout().addWidget(button)
    
    def setupOutput(self):
        self.__output.setLayout(QVBoxLayout())

    def update(self):
        self.__output.update()

    def assetData(self):
        return self.__asset_data
    
    def addTag(self, tag):
        if tag not in self.__tags:
            self.__tags.append(tag)
        
        self.updateTags()
    
    def updateTags(self):
        for i in range(self.__tags_grid.count()):
            w = self.__tags_grid.takeAt(0)
            w.widget().deleteLater()        

        def showMenu(pos):
            def slot_DeleteTag(action):
                self.__tags.remove(action.data())
                self.updateTags()

            action = QAction("Delete", self)
            action.setData(self.sender().text())
            menu = QMenu(self)
            menu.addAction(action)
            menu.triggered.connect(slot_DeleteTag)
            menu.exec(self.sender().mapToGlobal(pos))

        c = 0
        r = 0
        for tag in self.__tags:
            button = QPushButton(tag, self)
            button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            button.customContextMenuRequested.connect(showMenu)
            self.__tags_grid.addWidget(button, r, c)
            if c == 1:
                r = r + 1
                c = 0
            else:
                c = 1