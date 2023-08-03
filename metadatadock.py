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
    QDockWidget,
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

class metadataDock(QDockWidget):
    def __init__(self, parent=None):
        super(metadataDock, self).__init__(self.tr("Metadata"),parent=parent)
        
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        
        self.coreData = QGroupBox(self.tr("Core Information"))
        self.coreLayout = QGridLayout()
        self.coreLayout.setColumnMinimumWidth(0, 150)
        self.coreLayout.setColumnMinimumWidth(1, 200)
        self.coreData.setLayout(self.coreLayout)
        self.mainLayout.addWidget(self.coreData, 0)
        
        self.coreLayout.addWidget(QLabel(self.tr("Title")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.titleEdit = QLineEdit()
        self.coreLayout.addWidget(self.titleEdit, 0,1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Data Type")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dataTypeCombo = QComboBox()
        self.dataTypeCombo.addItems(["Raman", "Infrared", "UV/VIS", "NMR"])
        self.coreLayout.addWidget(self.dataTypeCombo, 1, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Origin")), 4,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.originEdit = QPlainTextEdit()
        self.coreLayout.addWidget(self.originEdit, 4, 1)
        
        self.coreLayout.addWidget(QLabel(self.tr("Owner")), 5,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.ownerEdit = QPlainTextEdit()
        self.coreLayout.addWidget(self.ownerEdit, 5, 1)
        
        self.spectralData = QGroupBox(self.tr("Spectral Parameters"))
        self.spectralLayout = QGridLayout()
        self.spectralLayout.setColumnMinimumWidth(0, 150)
        self.spectralLayout.setColumnMinimumWidth(1, 200)
        self.spectralData.setLayout(self.spectralLayout)
        self.mainLayout.addWidget(self.spectralData, 1)
        
        self.spectralLayout.addWidget(QLabel(self.tr("Unit of X axis")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.xUnitEdit = QLineEdit()
        self.spectralLayout.addWidget(self.xUnitEdit, 0, 1)
        
        self.spectralLayout.addWidget(QLabel(self.tr("Unit of Y axis")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.yUnitEdit = QLineEdit()
        self.spectralLayout.addWidget(self.yUnitEdit, 1, 1)
        
        self.spectralLayout.addWidget(QLabel(self.tr("Resolution")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.resolutionEdit = QLineEdit()
        self.spectralLayout.addWidget(self.resolutionEdit, 2, 1)
        
        self.spectralLayout.addWidget(QLabel(self.tr("Delta X")), 3,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.deltaXEdit = QLineEdit()
        self.spectralLayout.addWidget(self.deltaXEdit, 3, 1)
        
        self.noteData = QGroupBox(self.tr("Note Information"))
        self.noteLayout = QGridLayout()
        self.noteLayout.setColumnMinimumWidth(0, 150)
        self.noteLayout.setColumnMinimumWidth(1, 200)
        self.noteData.setLayout(self.noteLayout)
        self.mainLayout.addWidget(self.noteData, 2)
        
        self.noteLayout.addWidget(QLabel(self.tr("Time and Date")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setDisplayFormat("yyyy-MM-dd hh:mm:ss")
        self.noteLayout.addWidget(self.dateTimeEdit, 0, 1)
        
        self.noteLayout.addWidget(QLabel(self.tr("Source Reference")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.sourceReferenceEdit = QLineEdit()
        self.noteLayout.addWidget(self.sourceReferenceEdit, 1, 1)
        
        self.noteLayout.addWidget(QLabel(self.tr("Cross Reference")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.crossReferenceEdit = QLineEdit()
        self.noteLayout.addWidget(self.crossReferenceEdit, 2, 1)
        
        self.sampleData = QGroupBox(self.tr("Sample Information"))
        self.sampleLayout = QGridLayout()
        self.sampleLayout.setColumnMinimumWidth(0, 150)
        self.sampleLayout.setColumnMinimumWidth(1, 200)
        self.sampleData.setLayout(self.sampleLayout)
        self.mainLayout.addWidget(self.sampleData, 3)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Sample Description")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.sampleDescriptionEdit = QPlainTextEdit()
        self.sampleLayout.addWidget(self.sampleDescriptionEdit, 0, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("CAS Name")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.CASNameEdit = QLineEdit()
        self.sampleLayout.addWidget(self.CASNameEdit, 1, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("CAS RegistryNumber")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.CASRegistryNumberEdit = QLineEdit()
        self.sampleLayout.addWidget(self.CASRegistryNumberEdit, 2, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("IUPAC Name")), 3,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.IUPACNameEdit = QLineEdit()
        self.sampleLayout.addWidget(self.IUPACNameEdit, 3, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Other Names")), 4,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.namesEdit = QLineEdit()
        self.sampleLayout.addWidget(self.namesEdit, 4, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Moleular Formular")), 5,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.molformEdit = QLineEdit()
        self.sampleLayout.addWidget(self.molformEdit, 5, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Wiswesser")), 6,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.wiswesserEdit = QLineEdit()
        self.sampleLayout.addWidget(self.wiswesserEdit, 6, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Beilstein Lawson Number")), 7,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.BeilsteinNumberEdit = QLineEdit()
        self.sampleLayout.addWidget(self.BeilsteinNumberEdit, 7, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Melting Point")), 8,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.meltingPointEdit = QLineEdit()
        self.sampleLayout.addWidget(self.meltingPointEdit, 8, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Boiling Point")), 9,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.boilingPointEdit = QLineEdit()
        self.sampleLayout.addWidget(self.boilingPointEdit, 9, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Refractive Index")), 10,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.refractiveIndexEdit = QLineEdit()
        self.sampleLayout.addWidget(self.refractiveIndexEdit, 10, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Density")), 11,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.densityEdit = QLineEdit()
        self.sampleLayout.addWidget(self.densityEdit, 11, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Molecular Weight")), 12,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.molecularWeightEdit = QLineEdit()
        self.sampleLayout.addWidget(self.molecularWeightEdit, 12, 1)
        
        self.sampleLayout.addWidget(QLabel(self.tr("Concentrations")), 13,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.concentrationsEdit = QPlainTextEdit()
        self.sampleLayout.addWidget(self.concentrationsEdit, 13, 1)
        
        self.equipmentData = QGroupBox(self.tr("Equipment Information"))
        self.equipmentLayout = QGridLayout()
        self.equipmentLayout.setColumnMinimumWidth(0, 150)
        self.equipmentLayout.setColumnMinimumWidth(1, 200)
        self.equipmentData.setLayout(self.equipmentLayout)
        self.mainLayout.addWidget(self.equipmentData, 4)
        
        self.equipmentLayout.addWidget(QLabel(self.tr("Spectrmoeter")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.spectrometerEdit = QLineEdit()
        self.equipmentLayout.addWidget(self.spectrometerEdit, 0, 1)
        
        self.equipmentLayout.addWidget(QLabel(self.tr("Instrumental Parameters")),1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.instrumentalParameterEdit = QPlainTextEdit()
        self.equipmentLayout.addWidget(self.instrumentalParameterEdit, 1, 1)
        
        self.samplingData = QGroupBox(self.tr("Sampling Information"))
        self.samplingLayout = QGridLayout()
        self.samplingLayout.setColumnMinimumWidth(0, 150)
        self.samplingLayout.setColumnMinimumWidth(1, 200)
        self.samplingData.setLayout(self.samplingLayout)
        self.mainLayout.addWidget(self.samplingData, 5)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Sampling Procedure")), 0,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.samplingProcedureEdit = QPlainTextEdit()
        self.samplingLayout.addWidget(self.samplingProcedureEdit, 0, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("State")), 1,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.stateCombo = QComboBox()
        self.stateCombo.addItems([self.tr("solid"), self.tr("liquid"), self.tr("gas"), self.tr("solution")])
        self.samplingLayout.addWidget(self.stateCombo, 1, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Data Processing")), 2,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.dataProcessingEdit = QPlainTextEdit()
        self.samplingLayout.addWidget(self.dataProcessingEdit, 2, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Temperature")), 3,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.temperatureEdit = QLineEdit()
        self.samplingLayout.addWidget(self.temperatureEdit, 3, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Pressure")), 4,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.pressureEdit = QLineEdit()
        self.samplingLayout.addWidget(self.pressureEdit, 4, 1)
        
        self.samplingLayout.addWidget(QLabel(self.tr("Path Length")), 5,0, alignment=Qt.AlignmentFlag.AlignTop)
        self.pathLengthEdit = QLineEdit()
        self.samplingLayout.addWidget(self.pathLengthEdit, 5, 1)
        
        self.commentData = QGroupBox(self.tr("Comments"))
        self.commentLayout = QVBoxLayout()
        self.commentData.setLayout(self.commentLayout)
        self.mainLayout.addWidget(self.commentData, 6)
        
        self.commentEdit = QPlainTextEdit()
        self.commentLayout.addWidget(self.commentEdit)
                
        self.viewport = QWidget()
        self.viewport.setLayout(self.mainLayout)
        
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.viewport)
        self.setWidget(self.scrollArea)
    
    def getData(self):
        data = {}
        data["Core Data"] = {}
        data["Core Data"]["Title"] = self.titleEdit.text()
        data["Core Data"]["Data Type"] = self.dataTypeCombo.currentText()
        data["Core Data"]["Origin"] = self.originEdit.plainText
        data["Core Data"]["Owner"] = self.ownerEdit.plainText
        data["Spectral Parameters"] = {}
        data["Spectral Parameters"]["X Units"] = self.xUnitEdit.text()
        data["Spectral Parameters"]["Y Units"] = self.yUnitEdit.text()
        data["Spectral Parameters"]["Resolution"] = self.resolutionEdit.text()
        data["Spectral Parameters"]["Delta X"] = self.deltaXEdit.text()
        data["Notes"] = {}
        data["Notes"]["Date Time"] = self.dateTimeEdit.dateTime()
        data["Notes"]["Source Reference"] = self.sourceReferenceEdit.text()
        data["Notes"]["Cross Reference"] = self.crossReferenceEdit.text()
        data["Sample Information"] = {}
        data["Sample Information"]["Sample Description"] = self.sampleDescriptionEdit.plainText
        data["Sample Information"]["CAS Name"] = self.CASNameEdit.text()
        data["Sample Information"]["IUPAC Name"] = self.IUPACNameEdit.text()
        data["Sample Information"]["Names"] = self.namesEdit.text()
        data["Sample Information"]["Molform"] = self.molformEdit.text()
        data["Sample Information"]["CAS Registry No"] = self.CASRegistryNumberEdit.text()
        data["Sample Information"]["Wiswesser"] = self.wiswesserEdit.text()
        data["Sample Information"]["Beilstein Lawson No"] = self.BeilsteinNumberEdit.text()
        data["Sample Information"]["Melting Point"] = self.meltingPointEdit.text()
        data["Sample Information"]["Boiling Point"] = self.boilingPointEdit.text()
        data["Sample Information"]["Refractive Index"] = self.refractiveIndexEdit.text()
        data["Sample Information"]["Density"] = self.densityEdit.text()
        data["Sample Information"]["Molecular Weight"] = self.molecularWeightEdit.text()
        data["Sample Information"]["Concentrations"] = self.concentrationsEdit.plainText
        data["Equipment Information"] = {}
        data["Equipment Information"]["Spectrometer"] = self.spectrometerEdit.text()
        data["Equipment Information"]["Instrumental Parameters"] = self.instrumentalParameterEdit.plainText
        data["Sampling Information"] = {}
        data["Sampling Information"]["Sampling Procedure"] = self.samplingProcedureEdit.plainText
        data["Sampling Information"]["State"] = self.stateCombo.currentText()
        data["Sampling Information"]["Path Length"] = self.pathLengthEdit.text()
        data["Sampling Information"]["Pressure"] = self.pressureEdit.text()
        data["Sampling Information"]["Temperature"] = self.temperatureEdit.text()
        data["Sampling Information"]["Data Processing"] = self.dataProcessingEdit.plainText
        data["Comments"] = self.commentEdit.plainText
        return data
    
    def setData(self, data):
        self.titleEdit.setText(data["Core Data"]["Title"])
        self.dataTypeCombo.setCurrentText(data["Core Data"]["Data Type"])
        self.originEdit.setPlainText(data["Core Data"]["Origin"])
        self.ownerEdit.setPlainText(data["Core Data"]["Owner"])
        self.xUnitEdit.setText(data["Spectral Parameters"]["X Units"])
        self.yUnitEdit.setText(data["Spectral Parameters"]["Y Units"])
        self.resolutionEdit.setText(data["Spectral Parameters"]["Resolution"])
        self.deltaXEdit.setText(data["Spectral Parameters"]["Delta X"])
        self.dateTimeEdit.setDateTime(data["Notes"]["Date Time"])
        self.sourceReferenceEdit.setText(data["Notes"]["Source Reference"])
        self.crossReferenceEdit.setText(data["Notes"]["Cross Reference"])
        self.sampleDescriptionEdit.setPlainText(data["Sample Information"]["Sample Description"])
        self.CASNameEdit.setText(data["Sample Information"]["CAS Name"])
        self.IUPACNameEdit.setText(data["Sample Information"]["IUPAC Name"])
        self.namesEdit.setText(data["Sample Information"]["Names"])
        self.molformEdit.setText(data["Sample Information"]["Molform"])
        self.CASRegistryNumberEdit.setText(data["Sample Information"]["CAS Registry No"])
        self.wiswesserEdit.setText(data["Sample Information"]["Wiswesser"])
        self.BeilsteinNumberEdit.setText(data["Sample Information"]["Beilstein Lawson No"])
        self.meltingPointEdit.setText(data["Sample Information"]["Melting Point"])
        self.boilingPointEdit.setText(data["Sample Information"]["Boiling Point"])
        self.refractiveIndexEdit.setText(data["Sample Information"]["Refractive Index"])
        self.densityEdit.setText(data["Sample Information"]["Density"])
        self.molecularWeightEdit.setText(data["Sample Information"]["Molecular Weight"])
        self.concentrationsEdit.setPlainText(data["Sample Information"]["Concentrations"])
        self.spectrometerEdit.setText(data["Equipment Information"]["Spectrometer"])
        self.instrumentalParameterEdit.setPlainText(data["Equipment Information"]["Instrumental Parameters"])
        self.samplingProcedureEdit.setPlainText(data["Sampling Information"]["Sampling Procedure"])
        self.stateCombo.setCurrentText(data["Sampling Information"]["State"])
        self.pathLengthEdit.setText(data["Sampling Information"]["Path Length"])
        self.pressureEdit.setText(data["Sampling Information"]["Pressure"])
        self.temperatureEdit.setText(data["Sampling Information"]["Temperature"])
        self.dataProcessingEdit.setPlainText(data["Sampling Information"]["Data Processing"])
        self.commentEdit.setPlainText(data["Comments"])
        