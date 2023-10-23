#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:41:15 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QSize, QEvent
from PyQt6.QtWidgets import (
    QListWidget,
    QListView,
    QGridLayout,
    QDockWidget,
    QWidget,
    QPushButton,
    QMenu,
    QAbstractItemView
)

class pageView(QListWidget):
    pageUpRequest = pyqtSignal(int)
    pageDownRequest = pyqtSignal(int)
    pageEditRequest = pyqtSignal(int)
    pageDeleteRequest = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(pageView, self).__init__(parent=parent)
        
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setFlow(QListView.Flow.LeftToRight)
        self.setResizeMode(QListView.ResizeMode.Fixed)
        self.setIconSize(QSize(200,200))
        self.setGridSize(QSize(200,200))
        self.installEventFilter(self)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
    def resizeEvent(self, e):
        self.setIconSize(QSize(int(e.size().width()*0.95), int(e.size().width()*0.95)))
        super().resizeEvent(e)
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.ContextMenu and source == self:
            item = source.itemAt(event.pos())
            if item:
                row = self.row(item)
                menu = QMenu(self)
                editAction = QAction(self.tr("Edit Page"))
                upAction = QAction(self.tr("Page Up"))
                downAction = QAction(self.tr("Page Down"))
                deleteAction = QAction(self.tr("Delete Page"))
                menu.addAction(editAction)
                if row > 0:
                    menu.addAction(upAction)
                if row < self.count() - 1:
                    menu.addAction(downAction)
                menu.addAction(deleteAction)
                
                action = menu.exec(event.globalPos())
                if action == editAction:
                    self.pageEditRequest.emit(row)
                elif action == upAction:
                    self.pageUpRequest.emit(row)
                elif action == downAction:
                    self.pageDownRequest.emit(row)
                elif action == deleteAction:
                    self.pageDeleteRequest.emit(row)
        
        return super(pageView, self).eventFilter(source, event)

class spectraView(QListWidget):
    spectrumUpRequest = pyqtSignal(int)
    spectrumDownRequest = pyqtSignal(int)
    spectrumEditRequest = pyqtSignal(int)
    spectrumDeleteRequest = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super(spectraView, self).__init__(parent=parent)
        self.installEventFilter(self)
    
    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.ContextMenu and source == self:
            item = source.itemAt(event.pos())
            if item:
                row = self.row(item)
                menu = QMenu(self)
                editAction = QAction(self.tr("Edit Spectrum"))
                upAction = QAction(self.tr("Spectrum Up"))
                downAction = QAction(self.tr("Spectrum Down"))
                deleteAction = QAction(self.tr("Delete Spectrum"))
                menu.addAction(editAction)
                if row > 0:
                    menu.addAction(upAction)
                if row < self.count() - 1:
                    menu.addAction(downAction)
                menu.addAction(deleteAction)
                
                action = menu.exec(event.globalPos())
                if action == editAction:
                    self.spectrumEditRequest.emit(row)
                elif action == upAction:
                    self.spectrumUpRequest.emit(row)
                elif action == downAction:
                    self.spectrumDownRequest.emit(row)
                elif action == deleteAction:
                    self.spectrumDeleteRequest.emit(row)
        
        return super(spectraView, self).eventFilter(source, event)