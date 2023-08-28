#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 07:59:29 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QWidget,
    QPushButton,
    QFileDialog,
    QComboBox,
    QGroupBox,
    QSpinBox,
    QHBoxLayout,
    QRadioButton
)
import json
import os.path

class openDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open File")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        
        # general Information
        self.layout.addWidget(QLabel(self.tr("File: ")), 0,0)
        self.fileNameLabel = QLabel(self)
        self.layout.addWidget(self.fileNameLabel, 0,1)
        self.openFileButton = QPushButton("...", self)
        self.openFileButton.clicked.connect(self.getFileName)
        self.layout.addWidget(self.openFileButton, 0, 3)
        self.layout.addWidget(QLabel(self.tr("File Type: ")), 1, 0)
        self.fileTypeCombo = QComboBox(self)
        self.fileTypeCombo.addItems(["JCAMP-DX", "Any Text Format"])
        self.fileTypeCombo.currentTextChanged.connect(self.changeFileType)
        self.layout.addWidget(self.fileTypeCombo, 1,1)
        
        # Free Text Settings
        self.freeTextFileSettings = QGroupBox(self.tr("Any Text Format Import Settings"))
        self.freeTextFileSettings.setVisible(False)
        self.settingsLayout = QGridLayout()
        self.freeTextFileSettings.setLayout(self.settingsLayout)
        
        self.settingsLayout.addWidget(QLabel(self.tr("Spectrum Type:")), 0, 0)
        self.spectrumTypeCombo = QComboBox(self)
        self.spectrumTypeCombo.addItems(["Raman", self.tr("Infrared"), "UV/VIS", "NMR", self.tr("XRF")])
        self.settingsLayout.addWidget(self.spectrumTypeCombo, 0, 1)
        
        self.settingsLayout.addWidget(QLabel(self.tr("File Encoding:")), 1, 0)
        self.fileEncodingCombo = QComboBox(self)
        self.fileEncodingCombo.addItems(["utf-8", "iso-8859-1", "iso-8859-2", "iso-8859-3", "iso-8859-4", "iso-8859-5", "iso-8859-6", "iso-8859-7", "iso-8859-8", "iso-8859-9", "iso-8859-10", "iso-8859-11", "iso-8859-13", "iso-8859-14", "iso-8859-15", "iso-8859-16", "cp874", "cp932", "cp936", "cp949", "cp950", "cp1250", "cp1251", "cp1252", "cp1253", "cp1254", "cp1255", "cp1256", "cp1257", "cp1258"])
        self.settingsLayout.addWidget(self.fileEncodingCombo, 1, 1)
        
        self.settingsLayout.addWidget(QLabel(self.tr("Comment Character:")), 2, 0)
        self.commentCharCombo = QComboBox(self)
        self.commentCharCombo.addItems(["#", "%", "$", ";"])
        self.settingsLayout.addWidget(self.commentCharCombo, 2, 1)
        
        self.settingsLayout.addWidget(QLabel(self.tr("Column Delimiter:")), 3, 0)
        self.columnDelimiterCombo = QComboBox(self)
        self.columnDelimiterCombo.addItems(["any whitespace", ",", ";"])
        self.settingsLayout.addWidget(self.columnDelimiterCombo, 3, 1)
        
        self.settingsLayout.addWidget(QLabel(self.tr("Decimal Separator:")), 4, 0)
        self.decimalSeparatorCombo = QComboBox(self)
        self.decimalSeparatorCombo.addItems([",", "."])
        self.settingsLayout.addWidget(self.decimalSeparatorCombo, 4, 1)
        
        self.settingsLayout.addWidget(QLabel(self.tr("Skip Rows:")), 5, 0)
        self.skipRows = QSpinBox(self)
        self.skipRows.setRange(0, int(1e6))
        self.skipRows.setSingleStep(1)
        self.skipRows.setValue(0)
        self.settingsLayout.addWidget(self.skipRows, 5, 1)
        
        self.settingsSaveButton = QPushButton(self.tr("Save Config"), self)
        self.settingsSaveButton.clicked.connect(self.saveSettings)
        self.settingsLayout.addWidget(self.settingsSaveButton, 6, 0)
        self.settingsLoadButton = QPushButton(self.tr("Load Config"), self)
        self.settingsLoadButton.clicked.connect(self.loadSettings)
        self.settingsLayout.addWidget(self.settingsLoadButton, 6, 1)
        
        self.layout.addWidget(self.freeTextFileSettings, 2, 0, 1, 3)
        
        self.openAsGroup = QGroupBox(self.tr("Open as..."))
        self.openAsLayout = QHBoxLayout(self)
        self.openAsGroup.setLayout(self.openAsLayout)
        self.layout.addWidget(self.openAsGroup, 3, 0, 1, 4)
        
        self.openAsDocumentRadio = QRadioButton(self.tr("new Document"))
        self.openAsLayout.addWidget(self.openAsDocumentRadio)
        self.openAsDocumentRadio.setChecked(True)
        
        self.openAsPageRadio = QRadioButton(self.tr("new Page in the current Document"))
        self.openAsLayout.addWidget(self.openAsPageRadio)
        
        self.openAsPlotRadio = QRadioButton(self.tr("new Spectrum in the current Page"))
        self.openAsLayout.addWidget(self.openAsPlotRadio)
        
        self.layout.addWidget(self.buttonBox, 4, 0, 1, 4)
        self.setLayout(self.layout)
        
        if self.settings.value("lastFreeTextSettings"): # load old settings if present
            freeTextSettings = self.settings.value("lastFreeTextSettings")
            self.spectrumTypeCombo.setCurrentText(freeTextSettings["Spectrum Type"])
            self.fileEncodingCombo.setCurrentText(freeTextSettings["File Encoding"])
            self.commentCharCombo.setCurrentText(freeTextSettings["Comment Character"])
            self.columnDelimiterCombo.setCurrentText(freeTextSettings["Column Delimiter"])
            self.decimalSeparatorCombo.setCurrentText(freeTextSettings["Decimal Separator"])
            self.skipRows.setValue(freeTextSettings["skip Rows"])
    
    def getFileName(self):
        if self.settings.value("lastOpenDir"):
            fileName, filterType = QFileDialog.getOpenFileName(None, "Open spectrum", self.settings.value("lastOpenDir"), self.tr("JCAMP-DX File (*.dx *jdx);; Any Type (*.*)"))
        else:
            fileName, filterType = QFileDialog.getOpenFileName(None, "Open spectrum", QDir.homePath(), self.tr("JCAMP-DX File (*.dx);; Any Type (*.*)"))
        if fileName:
            self.fileNameLabel.setText(fileName)
            if filterType == "Any Type (*.*)":
                self.fileTypeCombo.setCurrentText("Any Text Format")
                self.freeTextFileSettings.setVisible(True)
            elif filterType == "JCAMP-DX File (*.dx *jdx)":
                self.fileTypeCombo.setCurrentText("JCAMP-DX")
                self.freeTextFileSettings.setVisible(False)
    
    def changeFileType(self, s):
        if s == "JCAMP-DX":
            self.freeTextFileSettings.setVisible(False)
        elif s == "Any Text Format":
            self.freeTextFileSettings.setVisible(True)
    
    def saveSettings(self):
        freeTextSettings = {}
        freeTextSettings["Spectrum Type"] = self.spectrumTypeCombo.currentText()
        freeTextSettings["File Encoding"] = self.fileEncodingCombo.currentText()
        freeTextSettings["Comment Character"] = self.commentCharCombo.currentText()
        freeTextSettings["Column Delimiter"] = self.columnDelimiterCombo.currentText()
        freeTextSettings["Decimal Separator"] = self.decimalSeparatorCombo.currentText()
        freeTextSettings["skip Rows"] = self.skipRows.value()
        
        baseDir = self.settings.value("lastFreeTextSettingsDir")
        if not baseDir:
            baseDir = QDir.homePath()
        fileName, filterType = QFileDialog.getSaveFileName(None, "Save Config", baseDir, self.tr("JSON file (*.json)"))
        if fileName:
            if not fileName.endswith(".json"):
                fileName += ".json"
            self.settings.setValue("lastFreeTextSettingsDir", os.path.dirname(fileName))
            with open(fileName, "w") as f:
                json.dump(freeTextSettings, f)
    
    def loadSettings(self):
        baseDir = self.settings.value("lastFreeTextSettingsDir")
        print(baseDir)
        if not baseDir:
            baseDir = QDir.homePath()
        fileName, filterType = QFileDialog.getOpenFileName(None, "Load Config", baseDir, self.tr("JSON file (*.json)"))
        if fileName:
            self.settings.setValue("lastFreeTextSettingsDir", os.path.dirname(fileName))
            freeTextSettings = {}
            with open(fileName) as f:
                freeTextSettings = json.load(f)
            self.spectrumTypeCombo.setCurrentText(freeTextSettings["Spectrum Type"])
            self.fileEncodingCombo.setCurrentText(freeTextSettings["File Encoding"])
            self.commentCharCombo.setCurrentText(freeTextSettings["Comment Character"])
            self.columnDelimiterCombo.setCurrentText(freeTextSettings["Column Delimiter"])
            self.decimalSeparatorCombo.setCurrentText(freeTextSettings["Decimal Separator"])
            self.skipRows.setValue(freeTextSettings["skip Rows"])
    
    def setOpenOptions(self, cDoc, cPage):
        self.openAsPageRadio.setEnabled(False)
        self.openAsPlotRadio.setEnabled(False)
        if cDoc != None:
            self.openAsPageRadio.setEnabled(True)
        if cPage != None:
            self.openAsPlotRadio.setEnabled(True)
    
    def getData(self):
        data = {}
        data["File Name"] = self.fileNameLabel.text()
        data['File Type'] = self.fileTypeCombo.currentText()
        
        freeTextSettings = {}
        freeTextSettings["Spectrum Type"] = self.spectrumTypeCombo.currentText()
        freeTextSettings["File Encoding"] = self.fileEncodingCombo.currentText()
        freeTextSettings["Comment Character"] = self.commentCharCombo.currentText()
        freeTextSettings["Column Delimiter"] = self.columnDelimiterCombo.currentText()
        freeTextSettings["Decimal Separator"] = self.decimalSeparatorCombo.currentText()
        freeTextSettings["skip Rows"] = self.skipRows.value()
        
        data['Free Text Settings'] = freeTextSettings
        
        # how to open the file
        if self.openAsDocumentRadio.isChecked():
            data['open as'] = "document"
        elif self.openAsPageRadio.isChecked():
            data['open as'] = "page"
        else:
            data['open as'] = "plot"
            
        self.settings.setValue("lastFreeTextSettings", freeTextSettings)
        return data