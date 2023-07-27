#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 12:41:15 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QDir, Qt, QDateTime
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QLineEdit,
    QComboBox,
    QPlainTextEdit,
    QDateTimeEdit,
    QWidget,
    QScrollArea,
)

class metadataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Metadata")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("MetadataDialogGeometry"):
            self.restoreGeometry(self.settings.value("MetadataDialogGeometry"))
        
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        self.mainLayout = QGridLayout()
        
        self.coreData = QGroupBox(self.tr("Core Information"))
        self.coreLayout = QGridLayout()
        self.coreLayout.setColumnMinimumWidth(0, 200)
        self.coreLayout.setColumnMinimumWidth(1, 300)
        self.coreData.setLayout(self.coreLayout)
        self.mainLayout.addWidget(self.coreData, 0,0)
        
        self.coreLayout.addWidget(QLabel(self.tr("Title")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.titleEdit = QLineEdit()
        self.coreLayout.addWidget(self.titleEdit, 0,1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Data Type")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dataTypeCombo = QComboBox()
        self.dataTypeCombo.addItems(["Raman", "Infrared", "UV/VIS", "NMR"])
        self.coreLayout.addWidget(self.dataTypeCombo, 1, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Unit of X axis")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.xUnitEdit = QLineEdit()
        self.coreLayout.addWidget(self.xUnitEdit, 2, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Unit of Y axis")), 3,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.yUnitEdit = QLineEdit()
        self.coreLayout.addWidget(self.yUnitEdit, 3, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Origin")), 4,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.originEdit = QPlainTextEdit()
        self.coreLayout.addWidget(self.originEdit, 4, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Owner")), 5,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.ownerEdit = QPlainTextEdit()
        self.coreLayout.addWidget(self.ownerEdit, 5, 1)
        
        self.noteData = QGroupBox(self.tr("Note Information"))
        self.noteLayout = QGridLayout()
        self.noteLayout.setColumnMinimumWidth(0, 200)
        self.noteLayout.setColumnMinimumWidth(1, 300)
        self.noteData.setLayout(self.noteLayout)
        self.mainLayout.addWidget(self.noteData, 2,0)
        
        self.noteLayout.addWidget(QLabel(self.tr("Time and Date")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.noteLayout.addWidget(self.dateTimeEdit, 0, 1)
        
        self.sampleData = QGroupBox(self.tr("Sample Information"))
        self.sampleLayout = QGridLayout()
        self.sampleLayout.setColumnMinimumWidth(0, 200)
        self.sampleLayout.setColumnMinimumWidth(1, 300)
        self.sampleData.setLayout(self.sampleLayout)
        self.mainLayout.addWidget(self.sampleData, 1,0)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Sample Description")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.sampleDescriptionEdit = QPlainTextEdit()
        self.sampleLayout.addWidget(self.sampleDescriptionEdit, 0, 1)
        
        self.equipmentData = QGroupBox(self.tr("Equipment Information"))
        self.equipmentLayout = QGridLayout()
        self.equipmentLayout.setColumnMinimumWidth(0, 200)
        self.equipmentLayout.setColumnMinimumWidth(1, 300)
        self.equipmentData.setLayout(self.equipmentLayout)
        self.mainLayout.addWidget(self.equipmentData, 0,1)
        
        self.equipmentLayout.addWidget(QLabel(self.tr("Spectrmoeter")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.spectrometerEdit = QLineEdit()
        self.equipmentLayout.addWidget(self.spectrometerEdit, 0, 1)
        
        self.equipmentLayout.addWidget(QLabel(self.tr("Instrumental Parameters")),1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.instrumentalParameterEdit = QPlainTextEdit()
        self.equipmentLayout.addWidget(self.instrumentalParameterEdit, 1, 1)
        
        self.samplingData = QGroupBox(self.tr("Sampling Information"))
        self.samplingLayout = QGridLayout()
        self.samplingLayout.setColumnMinimumWidth(0, 200)
        self.samplingLayout.setColumnMinimumWidth(1, 300)
        self.samplingData.setLayout(self.samplingLayout)
        self.mainLayout.addWidget(self.samplingData, 1,1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Sampling Procedure")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.samplingProcedureEdit = QPlainTextEdit()
        self.samplingLayout.addWidget(self.samplingProcedureEdit, 0, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("State")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.stateEdit = QLineEdit()
        self.samplingLayout.addWidget(self.stateEdit, 1, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Data Processing")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dataProcessingEdit = QPlainTextEdit()
        self.samplingLayout.addWidget(self.dataProcessingEdit, 2, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Temperature")), 3,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.temperatureEdit = QLineEdit()
        self.samplingLayout.addWidget(self.temperatureEdit, 3, 1)
        
        self.mainLayout.addWidget(self.buttonBox, 3,0,1,2)
        
        self.viewport = QWidget()
        self.viewport.setLayout(self.mainLayout)
        self.scrollArea = QScrollArea() 
        self.scrollArea.setMinimumHeight(600)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(self.viewport)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scrollArea)
        self.setLayout(self.layout)