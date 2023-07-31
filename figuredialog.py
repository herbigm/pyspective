#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 07:59:29 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon, QDoubleValidator
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QLineEdit
)
import json
import os.path

import numpy as np

class figureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Figure Options")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.oldData = None

        self.layout = QGridLayout()
        
        self.layout.addWidget(QLabel(self.tr("Invert Abscissa: ")), 0,0)
        self.invertXcheck = QCheckBox()
        self.layout.addWidget(self.invertXcheck, 0,1, 1, 3)
        self.invertXcheck.stateChanged.connect(self.invertX)
        self.layout.addWidget(QLabel(self.tr("Label of Abscissa: ")), 1,0)
        self.xLabelEdit = QLineEdit()
        self.layout.addWidget(self.xLabelEdit, 1,1, 1, 3)
        self.layout.addWidget(QLabel(self.tr("Label of Ordinate: ")), 2,0)
        self.yLabelEdit = QLineEdit()
        self.layout.addWidget(self.yLabelEdit, 2,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Abscissa Unit: ")), 3,0)
        self.xUnitCombo = QComboBox()
        self.xUnitCombo.currentTextChanged.connect(self.changeAbscissa)
        self.layout.addWidget(self.xUnitCombo, 3,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Ordinate Unit: ")), 4,0)
        self.yUnitCombo = QComboBox()
        self.yUnitCombo.currentTextChanged.connect(self.changeOrdinate)
        self.layout.addWidget(self.yUnitCombo, 4,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Abscissa Range: ")), 5,0)
        self.xRangeLower = QLineEdit()
        self.layout.addWidget(self.xRangeLower, 5,1)
        self.layout.addWidget(QLabel(self.tr("to ")), 5,2)
        self.xRangeUpper = QLineEdit()
        self.layout.addWidget(self.xRangeUpper, 5,3)
        self.layout.addWidget(QLabel(self.tr("Ordinate Range: ")), 6,0)
        self.yRangeLower = QLineEdit()
        self.layout.addWidget(self.yRangeLower, 6,1)
        self.layout.addWidget(QLabel(self.tr("to ")), 6,2)
        self.yRangeUpper = QLineEdit()
        self.layout.addWidget(self.yRangeUpper, 6,3)
        self.layout.addWidget(QLabel(self.tr("Title: ")), 7,0)
        self.titleEdit = QLineEdit()
        self.layout.addWidget(self.titleEdit, 7,1,1,3)
        
        
        self.layout.addWidget(self.buttonBox, 8, 0, 1, 4)
        self.setLayout(self.layout)
        
        if self.settings.value("lastFigureOptions"): # load old settings if present
            lastFigureOptions = self.settings.value("lastFigureOptions")
            self.setData(lastFigureOptions)
  
    def getData(self):
        data = {}
        data["invertX"] = self.invertXcheck.isChecked()
        data["XLabel"] = self.xLabelEdit.text()
        data["YLabel"] = self.yLabelEdit.text()
        data["XUnit"] = self.xUnitCombo.currentText()
        data["YUnit"] = self.yUnitCombo.currentText()
        data["Xlim"] = [float(self.xRangeLower.text().replace(",", ".")), float(self.xRangeUpper.text().replace(",", "."))]
        data["Ylim"] = [float(self.yRangeLower.text()), float(self.yRangeUpper.text())]
        data["Title"] = self.titleEdit.text()
        self.settings.setValue("lastFigureOptions", data)
        return data
    
    def setData(self, data):
        self.xLabelEdit.setText(data["XLabel"])
        self.yLabelEdit.setText(data["YLabel"])
        opticalUnitsX = ["1/CM", "MICROMETERS", "NANOMETERS"]
        if data["XUnit"] in opticalUnitsX:
            self.xUnitCombo.clear()
            self.xUnitCombo.addItems(opticalUnitsX)
        self.xUnitCombo.setCurrentText(data["XUnit"])
        opticalUnitsY = ["TRANSMITTANCE", "REFLECTANCE", "ABSORBANCE"]
        if data["YUnit"] in opticalUnitsY:
            self.yUnitCombo.clear()
            self.yUnitCombo.addItems(opticalUnitsY)
        self.yUnitCombo.setCurrentText(data["YUnit"])
        self.xRangeLower.setText(str(data["Xlim"][0]))
        self.xRangeUpper.setText(str(data["Xlim"][1]))
        self.yRangeLower.setText(str(data["Ylim"][0]))
        self.yRangeUpper.setText(str(data["Ylim"][1]))
        self.titleEdit.setText(data["Title"])
        self.oldData = self.getData()
    
    def invertX(self, state):
        tmp = self.xRangeLower.text()
        self.xRangeLower.setText(self.xRangeUpper.text())
        self.xRangeUpper.setText(tmp)
        self.oldData["Xlim"][0], self.oldData["Xlim"][1] = self.oldData["Xlim"][1], self.oldData["Xlim"][0] 
    
    def changeAbscissa(self, new):
        if not self.oldData:
            return
        if new == "NANOMETERS":
            if self.oldData["XUnit"] == "1/CM":
                self.xRangeLower.setText(str(1e7 / self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(1e7 / self.oldData["Xlim"][1]))
            elif self.oldData["XUnit"] == "MICROMETERS":
                self.xRangeLower.setText(str(self.oldData["Xlim"][0] * 1e3))
                self.xRangeUpper.setText(str(self.oldData["Xlim"][1] * 1e3))
            else:
                self.xRangeLower.setText(str(self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(self.oldData["Xlim"][1]))
        elif new == "MICROMETERS":
            if self.oldData["XUnit"] == "1/CM":
                self.xRangeLower.setText(str(1e4 / self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(1e4 / self.oldData["Xlim"][1]))
            elif self.oldData["XUnit"] == "NANOMETERS":
                self.xRangeLower.setText(str(self.oldData["Xlim"][0] * 1e-3))
                self.xRangeUpper.setText(str(self.oldData["Xlim"][1] * 1e-3))
            else:
                self.xRangeLower.setText(str(self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(self.oldData["Xlim"][1]))
        elif new == "1/CM":
            if self.oldData["XUnit"] == "MICROMETERS":
                self.xRangeLower.setText(str(1e4 / self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(1e4 / self.oldData["Xlim"][1]))
            elif self.oldData["XUnit"] == "NANOMETERS":
                self.xRangeLower.setText(str(1e7 / self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(1e7 / self.oldData["Xlim"][1]))
            else:
                self.xRangeLower.setText(str(self.oldData["Xlim"][0]))
                self.xRangeUpper.setText(str(self.oldData["Xlim"][1]))
        self.xLabelEdit.setText(new)
    
    def changeOrdinate(self, new):
        if not self.oldData:
            return
        if new == "TRANSMITTANCE":
            if self.oldData["YUnit"] == "REFLECTANCE":
                pass # nothing to do!
            elif self.oldData["YUnit"] == "ABSORBANCE":
                self.yRangeLower.setText(str(round(10 ** -(self.oldData["Ylim"][1])*100,2)))
                self.yRangeUpper.setText(str(round(10 ** -(self.oldData["Ylim"][0])*100,2)))
        elif new == "REFLECTANCE":
            if self.oldData["YUnit"] == "TRANSMITTANCE":
                pass # nothing to do!
            elif self.oldData["YUnit"] == "ABSORBANCE":
                self.yRangeLower.setText(str(round(10 ** -(self.oldData["Ylim"][1])*100,2)))
                self.yRangeUpper.setText(str(round(10 ** -(self.oldData["Ylim"][0])*100,2)))
        elif new == "ABSORBANCE":
            if self.oldData["YUnit"] == "REFLECTANCE":
                self.yRangeLower.setText(str(-np.log10(self.oldData["Ylim"][1]/100)))
                self.yRangeUpper.setText(str(-np.log10(self.oldData["Ylim"][0]/100)))
            elif self.oldData["YUnit"] == "TRANSMITTANCE":
                self.yRangeLower.setText(str(-np.log10(self.oldData["Ylim"][1]/100)))
                self.yRangeUpper.setText(str(-np.log10(self.oldData["Ylim"][0]/100)))
            
        self.yLabelEdit.setText(new)
            
    