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
    QDialog,
    QDialogButtonBox,
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
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QInputDialog,
    QMenu,
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



class integralDock(QDockWidget):
    integralsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super(integralDock, self).__init__(self.tr("Integrals"),parent=parent)
        
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setWidget(self.mainWidget)
        
        self.spectrum = None
        
        self.integralSumButton = QPushButton(self.tr("Change Sum of Integrals"))
        self.integralSumButton.clicked.connect(self.setIngetralSum)
        self.integralSumButton.setEnabled(False)
        self.mainLayout.addWidget(self.integralSumButton)
        
        self.table = QTableWidget(self)
        self.mainLayout.addWidget(self.table)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Start", "End", "Area", "rel. Area", "Color"])
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.itemDoubleClicked.connect(lambda item: self.editIntegral(self.table.row(item)))
        self.table.customContextMenuRequested.connect(self.tableContextMenu)
    
    def setIngetralSum(self):
        if not self.spectrum:
            return
        integralSum, ok = QInputDialog.getDouble(self, self.tr("Enter Sum of all Integrals of this spectrum"), "Σ =", value=100.0, min=0.0, decimals=3)
        if ok:
            self.spectrum.setIntegralSum(integralSum)
            self.integralsChanged.emit()
    
    def setSpectrum(self, spec):
        self.spectrum = spec
        if len(spec.integrals) > 0:
            self.integralSumButton.setEnabled(True)
        else:
            self.integralSumButton.setEnabled(False)
        self.table.clear()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Start", "End", "Area", "rel. Area", "Color"])
        self.table.verticalHeader().hide()
        self.table.setRowCount(len(spec.integrals))
        for row in range(len(spec.integrals)):
            self.table.setItem(row, 0, QTableWidgetItem(str(round(spec.integrals[row]['x1'], 3))))
            self.table.setItem(row, 1, QTableWidgetItem(str(round(spec.integrals[row]['x2'], 3))))
            self.table.setItem(row, 2, QTableWidgetItem(str(round(spec.integrals[row]['area'], 3))))
            self.table.setItem(row, 3, QTableWidgetItem(str(round(spec.integrals[row]['relativeArea'], 3))))
            color = QColor.fromString(spec.integrals[row]['color'])
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            self.table.setItem(row, 4, QTableWidgetItem(QIcon(pix), spec.integrals[row]['color'], 3))
    
    def tableContextMenu(self, pos):
        item = self.table.itemAt(pos)
        if item:
            row = item.row()
            menu = QMenu(self)
            editAction = QAction(self.tr("Edit Integral"))
            deleteAction = QAction(self.tr("Delete Integral"))
            menu.addAction(editAction)
            menu.addAction(deleteAction)
            
            action = menu.exec(self.table.mapToGlobal(pos))
            if action == editAction:
                self.editIntegral(row)
            elif action == deleteAction:
                del self.spectrum.integrals[row]
                self.integralsChanged.emit()
                
    def editIntegral(self, row):
        dgl = integralDialog(self)
        dgl.setData(self.spectrum.integrals[row])
        if dgl.exec():
            data = dgl.getData()
            self.spectrum.updateIntegral(row, data)
            self.integralsChanged.emit()

class integralDialog(QDialog):
    def __init__(self, parent=None):
        super(integralDialog, self).__init__(parent)
        self.setWindowTitle("Integral Options")
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QFormLayout()
        
        self.startEdit = QLineEdit(self)
        self.endEdit = QLineEdit(self)
        self.relAreaEdit = QLineEdit(self)
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString("#000000"))
        self.colorButton = QPushButton(QIcon(pix), "#000000")
        self.colorButton.clicked.connect(self.chooseColor)
        
        self.layout.addRow(self.tr("Start"), self.startEdit)
        self.layout.addRow(self.tr("End"), self.endEdit)
        self.layout.addRow(self.tr("rel. Area"), self.relAreaEdit)
        self.layout.addRow(self.tr("Color"), self.colorButton)
                
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

  
    def getData(self):
        data = {}
        data['x1'] = float(self.startEdit.text().replace(",", "."))
        data['x2'] = float(self.endEdit.text().replace(",", "."))
        data['relativeArea'] = float(self.relAreaEdit.text().replace(",", "."))
        data['color'] = self.color
        return data
    
    def setData(self, data):
        self.startEdit.setText(str(data['x1']))
        self.endEdit.setText(str(data['x2']))
        self.relAreaEdit.setText(str(data['relativeArea']))
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString(data['color']))
        self.colorButton.setIcon(QIcon(pix))
        self.colorButton.setText(data['color'])
        self.color = data['color']
    
    def chooseColor(self):
        dgl = QColorDialog(self)
        dgl.setCurrentColor(QColor.fromString(self.color))
        if dgl.exec():
            color = dgl.currentColor()
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            self.colorButton.setIcon(QIcon(pix))
            self.colorButton.setText(color.name())
            self.color = color.name()
