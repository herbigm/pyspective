#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:41:15 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QDir, Qt, QSize
from PyQt6.QtWidgets import (
    QListWidget,
    QListView,
    QGridLayout,
    QDockWidget,
    QWidget,
    QPushButton
)

class pageDock(QDockWidget):
    def __init__(self, parent=None):
        super(pageDock, self).__init__(self.tr("Pages"),parent=parent)
        self.pageView = pageView()
        self._mainWidget = QWidget()
        self.layout = QGridLayout()
        self.layout.addWidget(self.pageView, 0, 0, 1, 2)
        self.pageUpButton = QPushButton(self.tr("Page up"))
        self.layout.addWidget(self.pageUpButton, 1, 1)
        self.pageDownButton = QPushButton(self.tr("Page down"))
        self.layout.addWidget(self.pageDownButton, 1, 0)
        self._mainWidget.setLayout(self.layout)
        self.setWidget(self._mainWidget)
        

class pageView(QListWidget):
    def __init__(self, parent=None):
        super(pageView, self).__init__(parent=parent)
        
        self.setViewMode(QListWidget.ViewMode.IconMode)
        self.setFlow(QListView.Flow.TopToBottom)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setIconSize(QSize(200,200))
        
    def resizeEvent(self, e):
        self.setIconSize(QSize(int(e.size().width()*0.95), int(e.size().width()*0.95)))
        super().resizeEvent(e)