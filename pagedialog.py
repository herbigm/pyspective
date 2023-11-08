#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 07:59:29 2023

@author: marcus
"""

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QLineEdit
)

import numpy as np

class pageDialog(QDialog):
    def __init__(self, parent=None):
        super(pageDialog, self).__init__(parent)
        self.setWindowTitle("Page Options")
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.oldData = None

        self.layout = QGridLayout()
        
        self.layout.addWidget(QLabel(self.tr("Title of Page: ")), 0,0)
        self.pageTitleEdit = QLineEdit()
        self.layout.addWidget(self.pageTitleEdit, 0,1, 1, 3)
        self.layout.addWidget(QLabel(self.tr("Invert Abscissa: ")), 1,0)
        self.invertXcheck = QCheckBox()
        self.layout.addWidget(self.invertXcheck, 1,1, 1, 3)
        self.invertXcheck.stateChanged.connect(self.invertX)
        self.layout.addWidget(QLabel(self.tr("Label of Abscissa: ")), 2,0)
        self.xLabelEdit = QLineEdit()
        self.layout.addWidget(self.xLabelEdit, 2,1, 1, 3)
        self.layout.addWidget(QLabel(self.tr("Label of Ordinate: ")), 3,0)
        self.yLabelEdit = QLineEdit()
        self.layout.addWidget(self.yLabelEdit, 3,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Abscissa Unit: ")), 4,0)
        self.xUnitCombo = QComboBox()
        self.xUnitCombo.currentTextChanged.connect(self.changeAbscissa)
        self.layout.addWidget(self.xUnitCombo, 4,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Ordinate Unit: ")), 5,0)
        self.yUnitCombo = QComboBox()
        self.yUnitCombo.currentTextChanged.connect(self.changeOrdinate)
        self.layout.addWidget(self.yUnitCombo, 5,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Abscissa Range: ")), 6,0)
        self.xRangeLower = QLineEdit()
        self.layout.addWidget(self.xRangeLower, 6,1)
        self.layout.addWidget(QLabel(self.tr("to ")), 6,2)
        self.xRangeUpper = QLineEdit()
        self.layout.addWidget(self.xRangeUpper, 6,3)
        self.layout.addWidget(QLabel(self.tr("Ordinate Range: ")), 7,0)
        self.yRangeLower = QLineEdit()
        self.layout.addWidget(self.yRangeLower, 7,1)
        self.layout.addWidget(QLabel(self.tr("to ")), 7,2)
        self.yRangeUpper = QLineEdit()
        self.layout.addWidget(self.yRangeUpper, 7,3)
        self.layout.addWidget(QLabel(self.tr("Title in Plot: ")), 8,0)
        self.titleEdit = QLineEdit()
        self.layout.addWidget(self.titleEdit, 8,1,1,3)
        self.layout.addWidget(QLabel(self.tr("Show Legend: ")), 9,0)
        self.legendCombo = QComboBox()
        self.legendCombo.addItems(['No Legend', 'best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'])
        self.layout.addWidget(self.legendCombo, 9,1, 1, 3)
        
        self.layout.addWidget(self.buttonBox, 10, 0, 1, 4)
        self.setLayout(self.layout)
        
  
    def getData(self):
        data = {}
        data["invertX"] = self.invertXcheck.isChecked()
        data["XLabel"] = self.xLabelEdit.text()
        data["YLabel"] = self.yLabelEdit.text()
        data["XUnit"] = self.xUnitCombo.currentText()
        data["YUnit"] = self.yUnitCombo.currentText()
        data["XLim"] = [float(self.xRangeLower.text().replace(",", ".")), float(self.xRangeUpper.text().replace(",", "."))]
        data["YLim"] = [float(self.yRangeLower.text()), float(self.yRangeUpper.text())]
        data["PlotTitle"] = self.titleEdit.text()
        data["PageTitle"] = self.pageTitleEdit.text()
        if self.legendCombo.currentText() == "No Legend":
            data['Legend'] = ""
        else:
            data['Legend'] = self.legendCombo.currentText()
        return data
    
    def setData(self, data):
        if "XLabel" in data:
            self.xLabelEdit.setText(data["XLabel"])
        if "YLabel" in data:
            self.yLabelEdit.setText(data["YLabel"])
        if "XUnit" in data:
            opticalUnitsX = ["1/CM", "MICROMETERS", "NANOMETERS"]
            if data["XUnit"] in opticalUnitsX:
                self.xUnitCombo.clear()
                self.xUnitCombo.addItems(opticalUnitsX)
            self.xUnitCombo.setCurrentText(data["XUnit"])
        if "YUnit" in data:
            opticalUnitsY = ["TRANSMITTANCE", "REFLECTANCE", "ABSORBANCE"]
            if data["YUnit"] in opticalUnitsY:
                self.yUnitCombo.clear()
                self.yUnitCombo.addItems(opticalUnitsY)
            self.yUnitCombo.setCurrentText(data["YUnit"])
        if "XLim" in data:
            self.xRangeLower.setText(str(data["XLim"][0]))
            self.xRangeUpper.setText(str(data["XLim"][1]))
        if "YLim" in data:
            self.yRangeLower.setText(str(data["YLim"][0]))
            self.yRangeUpper.setText(str(data["YLim"][1]))
        if "PlotTitle" in data:
            self.titleEdit.setText(data["PlotTitle"])
        if "PageTitle" in data:
            self.pageTitleEdit.setText(data["PageTitle"])
        if "Legend" in data:
            if data["Legend"] != "":
                self.legendCombo.setCurrentText(data["Legend"])
            else:
                self.legendCombo.setCurrentText("No Legend")
        self.oldData = self.getData()
    
    def invertX(self, state):
        tmp = self.xRangeLower.text()
        self.xRangeLower.setText(self.xRangeUpper.text())
        self.xRangeUpper.setText(tmp)
        self.oldData["XLim"][0], self.oldData["XLim"][1] = self.oldData["XLim"][1], self.oldData["XLim"][0] 
    
    def changeAbscissa(self, new):
        if not self.oldData:
            return
        if new == "NANOMETERS":
            if self.oldData["XUnit"] == "1/CM":
                self.xRangeLower.setText(str(1e7 / self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(1e7 / self.oldData["XLim"][1]))
            elif self.oldData["XUnit"] == "MICROMETERS":
                self.xRangeLower.setText(str(self.oldData["XLim"][0] * 1e3))
                self.xRangeUpper.setText(str(self.oldData["XLim"][1] * 1e3))
            else:
                self.xRangeLower.setText(str(self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(self.oldData["XLim"][1]))
        elif new == "MICROMETERS":
            if self.oldData["XUnit"] == "1/CM":
                self.xRangeLower.setText(str(1e4 / self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(1e4 / self.oldData["XLim"][1]))
            elif self.oldData["XUnit"] == "NANOMETERS":
                self.xRangeLower.setText(str(self.oldData["XLim"][0] * 1e-3))
                self.xRangeUpper.setText(str(self.oldData["XLim"][1] * 1e-3))
            else:
                self.xRangeLower.setText(str(self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(self.oldData["XLim"][1]))
        elif new == "1/CM":
            if self.oldData["XUnit"] == "MICROMETERS":
                self.xRangeLower.setText(str(1e4 / self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(1e4 / self.oldData["XLim"][1]))
            elif self.oldData["XUnit"] == "NANOMETERS":
                self.xRangeLower.setText(str(1e7 / self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(1e7 / self.oldData["XLim"][1]))
            else:
                self.xRangeLower.setText(str(self.oldData["XLim"][0]))
                self.xRangeUpper.setText(str(self.oldData["XLim"][1]))
        self.xLabelEdit.setText(new)
    
    def changeOrdinate(self, new):
        if not self.oldData:
            return
        if new == "TRANSMITTANCE":
            if self.oldData["YUnit"] == "REFLECTANCE":
                pass # nothing to do!
            elif self.oldData["YUnit"] == "ABSORBANCE":
                self.yRangeLower.setText(str(round(10 ** -(self.oldData["YLim"][1])*100,2)))
                self.yRangeUpper.setText(str(round(10 ** -(self.oldData["YLim"][0])*100,2)))
            else:
                self.yRangeLower.setText(str(self.oldData["YLim"][0]))
                self.yRangeUpper.setText(str(self.oldData["YLim"][1]))
        elif new == "REFLECTANCE":
            if self.oldData["YUnit"] == "TRANSMITTANCE":
                pass # nothing to do!
            elif self.oldData["YUnit"] == "ABSORBANCE":
                self.yRangeLower.setText(str(round(10 ** -(self.oldData["YLim"][1])*100,2)))
                self.yRangeUpper.setText(str(round(10 ** -(self.oldData["YLim"][0])*100,2)))
            else:
                self.yRangeLower.setText(str(self.oldData["YLim"][0]))
                self.yRangeUpper.setText(str(self.oldData["YLim"][1]))
        elif new == "ABSORBANCE":
            if self.oldData["YUnit"] == "REFLECTANCE":
                self.yRangeLower.setText(str(-np.log10(self.oldData["YLim"][1]/100)))
                self.yRangeUpper.setText(str(-np.log10(self.oldData["YLim"][0]/100)))
            elif self.oldData["YUnit"] == "TRANSMITTANCE":
                self.yRangeLower.setText(str(-np.log10(self.oldData["YLim"][1]/100)))
                self.yRangeUpper.setText(str(-np.log10(self.oldData["YLim"][0]/100)))
            else:
                self.yRangeLower.setText(str(self.oldData["YLim"][0]))
                self.yRangeUpper.setText(str(self.oldData["YLim"][1]))
            
        self.yLabelEdit.setText(new)
            
    