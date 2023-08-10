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
    QListView
)

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