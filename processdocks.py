#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:41:15 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon, QPixmap, QColor
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QDateTime, QSize
from PyQt6.QtWidgets import (
    QDockWidget,
    QFormLayout,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QPlainTextEdit,
    QDateTimeEdit,
    QWidget,
    QScrollArea,
    QPushButton,
    QSpinBox,
    QColorDialog,
)

class peakpickingDock(QDockWidget):
    peaksChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super(peakpickingDock, self).__init__(self.tr("Peakpicking"),parent=parent)
        
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        
        self.settingsGroup = QGroupBox(self.tr("Settings"))
        self.settingsLayout = QFormLayout()
        self.settingsGroup.setLayout(self.settingsLayout)
        self.mainLayout.addWidget(self.settingsGroup)
        
        self.heightEdit = QLineEdit()
        self.thresholdEdit = QLineEdit()
        self.distanceEdit = QSpinBox()
        self.distanceEdit.setMinimum(1)   
        self.distanceEdit.setValue(1)
        self.distanceEdit.setSingleStep(1)
        self.prominenceEdit = QLineEdit()
        self.widthEdit = QLineEdit()
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString("#000000"))
        self.colorButton = QPushButton(QIcon(pix), "#000000")
        self.colorButton.clicked.connect(self.chooseColor)
        self.color = "#000000"
        
        self.settingsLayout.addRow(self.tr("Height"), self.heightEdit)
        self.settingsLayout.addRow(self.tr("Threshold"), self.thresholdEdit)
        self.settingsLayout.addRow(self.tr("Distance"), self.distanceEdit)
        self.settingsLayout.addRow(self.tr("Prominence"), self.prominenceEdit)
        self.settingsLayout.addRow(self.tr("Width"), self.widthEdit)
        self.settingsLayout.addRow(self.tr("Color"), self.colorButton)
        
        self.startButton = QPushButton(self.tr("Start Peakpicking"))
        self.startButton.clicked.connect(self.peakpicking)
        self.mainLayout.addWidget(self.startButton)
        
        self.resultGroup = QGroupBox(self.tr("Results"))
        self.resultField = QPlainTextEdit()
        self.resultLayout = QVBoxLayout()
        self.resultLayout.addWidget(self.resultField)
        self.resultGroup.setLayout(self.resultLayout)
        
        self.mainLayout.addWidget(self.resultGroup)
        
        self.deletePeaksButton = QPushButton(self.tr("Delete all Peaks"))
        self.mainLayout.addWidget(self.deletePeaksButton)
        self.deletePeaksButton.clicked.connect(self.deletePeaks)
        
        self.setWidget(self.mainWidget)
        
        self.spectrum = None
    
    def peakpicking(self):
        if not self.spectrum:
            return
        if self.heightEdit.text() != "":
            height = float(self.heightEdit.text().replace(",", "."))
        else:
            height = None
        if self.thresholdEdit.text() != "":
            threshold = float(self.thresholdEdit.text().replace(",", "."))
        else:
            threshold = None
        distance = self.distanceEdit.value()
        if self.prominenceEdit.text() != "":
            prominence = float(self.prominenceEdit.text().replace(",", "."))
        else:
            prominence = None
        if self.widthEdit.text() != "":
            width = float(self.widthEdit.text().replace(",", "."))
        else:
            width = None
        self.resultField.setPlainText(self.spectrum.peakpicking(height, threshold, distance, prominence, width))
        self.spectrum.peakParameter["Height"] = self.heightEdit.text()
        self.spectrum.peakParameter["Threshold"] = self.thresholdEdit.text()
        self.spectrum.peakParameter["Distance"] = distance
        self.spectrum.peakParameter["Prominence"] = self.prominenceEdit.text()
        self.spectrum.peakParameter["Width"] = self.widthEdit.text()
        self.spectrum.peakParameter["Color"] = self.color
        self.peaksChanged.emit()
    
    def setSpectrum(self, spec):
        self.spectrum = spec
        self.resultField.setPlainText(spec.peakString)
        self.heightEdit.setText(spec.peakParameter['Height'])
        self.thresholdEdit.setText(spec.peakParameter['Threshold'])
        self.distanceEdit.setValue(spec.peakParameter['Distance'])
        self.prominenceEdit.setText(spec.peakParameter['Prominence'])
        self.widthEdit.setText(spec.peakParameter['Width'])
        color = QColor.fromString(spec.peakParameter['Color'])
        pix = QPixmap(QSize(32,32))
        pix.fill(color)
        self.colorButton.setIcon(QIcon(pix))
        self.colorButton.setText(color.name())
        self.color = color.name()
    
    def deletePeaks(self):
        if not self.spectrum:
            return
        self.spectrum.peaks = []
        self.spectrum.peakString = ""
        self.resultField.setPlainText("")
        self.peaksChanged.emit()
    
    def chooseColor(self):
        dgl = QColorDialog(QColor.fromString(self.color), self)
        if dgl.exec():
            color = dgl.currentColor()
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            self.colorButton.setIcon(QIcon(pix))
            self.colorButton.setText(color.name())
            self.color = color.name()