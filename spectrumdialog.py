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
        self.line_style_names = [self.tr("no line"), self.tr("solid line"), self.tr("dashed line"), self.tr("dash-dot line"), self.tr("dotted line")]
        self.layout.addWidget(QLabel(self.tr("Line Style: ")), 2,0)
        self.lineStyleCombo = QComboBox()
        self.lineStyleCombo.addItems(self.line_style_names)
        self.layout.addWidget(self.lineStyleCombo, 2,1)
        
        self.marker_style = ['', '.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h', 'H', '+', 'x', 'X', 'D',  'd', '|', '_']
        self.marker_stye_names = [self.tr("no marker"), self.tr("point"), self.tr("pixel"), self.tr("circle"), self.tr("triangle downwards")
                                  , self.tr("triangle upwards"), self.tr("triangle to the left"), self.tr("triangle to the right"), self.tr("tri downwards")
                                  , self.tr("tri upwards"), self.tr("tri to the left"), self.tr("tri to the right"), self.tr("octagon")
                                  , self.tr("square"), self.tr("pentagon"), self.tr("filled plus"), self.tr("star")
                                  , self.tr("hexagon 1"), self.tr("hexagon 2"), self.tr("plus"), self.tr("x")
                                  , self.tr("filled x"), self.tr("diamond"), self.tr("thin diamond"), self.tr("vline"), self.tr("hline")]
        self.layout.addWidget(QLabel(self.tr("Marker Style: ")), 3,0)
        self.markerStyleCombo = QComboBox()
        self.markerStyleCombo.addItems(self.marker_stye_names)
        self.layout.addWidget(self.markerStyleCombo, 3,1)
                
        self.layout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.setLayout(self.layout)

  
    def getData(self):
        data = {}
        data["Title"] = self.titleEdit.text()
        data["Color"] = self.color
        data["Line Style"] = self.line_styles[self.lineStyleCombo.currentIndex()]
        data["Marker Style"] = self.marker_style[self.markerStyleCombo.currentIndex()]
        return data
    
    def setData(self, data):
        self.titleEdit.setText(data['Title'])
        self.color = data['Color']
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString(self.color))
        self.colorButton.setIcon(QIcon(pix))
        self.colorButton.setText(self.color)
        self.lineStyleCombo.setCurrentIndex(self.line_styles.index(data['Line Style']))
        self.markerStyleCombo.setCurrentIndex(self.marker_style.index(data['Marker Style']))
    
    def chooseColor(self):
        dgl = QColorDialog(self)
        if dgl.exec():
            color = dgl.currentColor()
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            self.colorButton.setIcon(QIcon(pix))
            self.colorButton.setText(color.name())
            self.color = color.name()