#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QPixmap, QIcon, QStandardItem, QStandardItemModel, QImage
from PyQt6.QtCore import Qt

import specplot

class DataPage():
    def __init__(self, title=""):
        self.figureCanvas = specplot.specplot()
        self.figureCanvas.draw()
        size = self.figureCanvas.size()
        width, height = size.width(), size.height()
        im = QImage(self.figureCanvas.buffer_rgba(), width, height, QImage.Format.Format_ARGB32)
        self.icon = QIcon(QPixmap(im))
        self.title = title

class DataModelItem(QStandardItem):
    def __init__(self, data):
        super(DataModelItem, self).__init__()
        self._data = data
        self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)
        
    def type(self):
        return type(self._data)
    
    def data(self, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if self.type() == DataPage:
                return self._data.title
        elif role == Qt.ItemDataRole.DecorationRole:
            if self.type() == DataPage:
                return self._data.icon



class DataModel(QStandardItemModel):
    def __init__(self, nodes = []):
        QStandardItemModel.__init__(self)
        
