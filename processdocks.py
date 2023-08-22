#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:41:15 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QDateTime
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
)

class peakpickingDock(QDockWidget):
    peaksFound = pyqtSignal()
    
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
        
        self.settingsLayout.addRow(self.tr("Height"), self.heightEdit)
        self.settingsLayout.addRow(self.tr("Threshold"), self.thresholdEdit)
        self.settingsLayout.addRow(self.tr("Distance"), self.distanceEdit)
        self.settingsLayout.addRow(self.tr("Prominence"), self.prominenceEdit)
        self.settingsLayout.addRow(self.tr("Width"), self.widthEdit)
        
        self.startButton = QPushButton(self.tr("Start Peakpicking"))
        self.startButton.clicked.connect(self.peakpicking)
        self.mainLayout.addWidget(self.startButton)
        
        self.resultGroup = QGroupBox(self.tr("Results"))
        self.resultField = QPlainTextEdit()
        self.resultLayout = QVBoxLayout()
        self.resultLayout.addWidget(self.resultField)
        self.resultGroup.setLayout(self.resultLayout)
        
        self.mainLayout.addWidget(self.resultGroup)
        
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
        self.peaksFound.emit()