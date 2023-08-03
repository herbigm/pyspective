#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

import specplot

class DataPage():
    def __init__(self, title=""):
        self.figureCanvas = specplot.specplot()
        self.figureCanvas.draw()
        self.icon = QIcon(QPixmap(self.figureCanvas.buffer_rgba()))
        self.title = title

class DataModelItem():
    def __init__(self, data):
        self._data = data
        
        self._children = []
        self._parent = None
        self._row = 0
    
    def data(self, column):
        if type(self._data) == dict:
            return "" # define data of spectrum with indices
        if type(self._data) == DataPage and column == 0:
            return self._data.title
        
    def columnCount(self):
        if type(self._data) == DataPage:
            print("datapage")
            return 1
        return 1
    
    def childCount(self):
        return len(self._children)
    
    def child(self, row):
        if row >=0 and row < self.childCount():
            return self._children[row]
    
    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent:
            return self._parent._children.index(DataModelItem(self))
        return 0
    
    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)


class DataModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes = []):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = DataModelItem(None)
        for node in nodes:
            self._root.addChild(node)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=QtCore.QModelIndex()):
        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()
        
        if not _parent.isValid():
            parentItem = self._root
        else:
            parentItem = _parent.internalPointer()

        child = parentItem.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        #return QtCore.QModelIndex()
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        
        if role == Qt.ItemDataRole.DisplayRole:
            return node.data(index.column())
        if role == Qt.ItemDataRole.DecorationRole:
            return node._data.icon
        return None
