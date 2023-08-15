#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 07:59:29 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon, QPixmap, QColor
from PyQt6.QtCore import QDir, QSize
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLineEdit,
    QLabel,
    QPushButton,
    QColorDialog,
    QComboBox
)
import json
import os.path

class spectrumDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Spectrum Options")
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        
        self.layout.addWidget(QLabel(self.tr("Title: ")), 0,0)
        self.titleEdit = QLineEdit()
        self.layout.addWidget(self.titleEdit, 0,1)
                
        self.layout.addWidget(QLabel(self.tr("Color: ")), 1,0)
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString("#000000"))
        self.colorButton = QPushButton(QIcon(pix), "#000000")
        self.layout.addWidget(self.colorButton, 1,1)
        self.colorButton.clicked.connect(self.chooseColor)
        self.color = "#000000"
        
        self.line_styles = ['', '-', '--', '-.', ':']
        self.line_style_names = [self.tr("no line"), self.tr("solid line"), self.tr("dashed line"), self.tr("dash-dor line"), self.tr("dotted line")]
        self.layout.addWidget(QLabel(self.tr("Line Style: ")), 2,0)
        self.lineStyleCombo = QComboBox()
        self.lineStyleCombo.addItems(self.line_style_names)
        
        self.markerStyleCombo = QComboBox()
        
        self.layout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.setLayout(self.layout)

  
    def getData(self):
        data = {}
        data["Color"] = self.color
        data["Title"] = self.titleEdit.text()
        data["Line Style"] = self.line_styles[self.lineStyleCombo.currentIndex()]
        data["Marker Style"] = self.markerStyleCombo.currentIndex()
        return data
    
    def chooseColor(self):
        dgl = QColorDialog(self)
        if dgl.exec():
            color = dgl.currentColor()
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            self.colorButton.setIcon(QIcon(pix))
            self.colorButton.setText(color.name())
            self.color = color.name()