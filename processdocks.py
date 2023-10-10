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
    QListWidget,
    QGridLayout,
    QFileDialog,
    QListWidgetItem,
    QCheckBox,
    QTextEdit
)

import os
import math
import json

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

class XrdDock(QDockWidget):
    referenceChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super(XrdDock, self).__init__(parent)
        self.setWindowTitle("XRD References")
        
        self.spectrum = None
        
        self.mainWidget = QWidget()
        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)
        
        self.addButton = QPushButton(self.tr("Add Reference"), self)
        self.layout.addWidget(self.addButton)
        self.addButton.clicked.connect(self.showDialog)
        
        self.referenceList = QListWidget(self)
        self.layout.addWidget(self.referenceList)
        self.referenceList.itemDoubleClicked.connect(self.updateReference)
        self.referenceList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.referenceList.customContextMenuRequested.connect(self.showContextMenu)
        
        self.setWidget(self.mainWidget)
    
    def setSpectrum(self, spec):
        self.spectrum = spec
        for ref in spec.references:
            pix = QPixmap(QSize(32,32))
            pix.fill(QColor.fromString(ref['Color']))
            self.referenceList.addItem(QListWidgetItem(QIcon(pix), ref['Title']))
    
    def showDialog(self):
        if not self.spectrum:
            return
        dgl = XrdReferenceDialog(self)
        if dgl.exec():
            data = dgl.getData()
            
            if data['File Name'] == "":
                return
            with open(data['File Name']) as f:
                lines = f.readlines()
                x = []
                y = []
                if lines[0].strip().lower() == "h      k      l  d-spacing       f^2     multiplicity":
                    for line in lines[1:]:
                        parts = line.split()
                        y.append(float(parts[4]))
                        x.append(round(math.asin(self.spectrum.wavelength / 2.0 / float(parts[3]))*180.0/math.pi*2, 2))
                elif lines[0].strip().lower() == "h	k	l	2theta	d-value	mult	intensity":
                    for line in lines[1:]:
                        parts = line.split()
                        y.append(float(parts[5]))
                        x.append(float(parts[3]))
                # make x unique
                newX = [0]
                newY = [0]
                for i in range(len(x)):
                    if x[i] != newX[-1]:
                        newX.append(x[i])
                        newY.append(y[i])
                    else:
                        newY[-1] += y[i]
                ref = {}
                ref['x'] = newX[1:]
                ref['y'] = newY[1:]
                ref['Color'] = data['Color']
                ref['Title'] = data['Title']
                ref['Display'] = data['Display']
                self.spectrum.references.append(ref)
                self.referenceChanged.emit()
                
                pix = QPixmap(QSize(32,32))
                pix.fill(QColor.fromString(data['Color']))
                self.referenceList.addItem(QListWidgetItem(QIcon(pix), data['Title']))
    
    def updateReference(self, item):
        if not self.spectrum:
            return
        index = self.referenceList.row(item)
        dgl = XrdReferenceDialog(self)
        dgl.setData(self.spectrum.references[index])
        if dgl.exec():
            data = dgl.getData()
            self.spectrum.references[index]['Color'] = data['Color']
            self.spectrum.references[index]['Title'] = data['Title']
            self.spectrum.references[index]['Display'] = data['Display']
            self.referenceChanged.emit()
            pix = QPixmap(QSize(32,32))
            pix.fill(QColor.fromString(data['Color']))
            item.setIcon(QIcon(pix))
            item.setText(data['Title'])
    
    def showContextMenu(self, pos):
        item = self.referenceList.itemAt(pos)
        if item:
            row = self.referenceList.row(item)
            menu = QMenu(self)
            editAction = QAction(self.tr("Edit Reference Display"))
            deleteAction = QAction(self.tr("Delete Reference"))
            menu.addAction(editAction)
            menu.addAction(deleteAction)
            
            action = menu.exec(self.referenceList.mapToGlobal(pos))
            if action == editAction:
                self.updateReference(item)
            elif action == deleteAction:
                del self.spectrum.references[row]
                self.referenceList.takeItem(row)
                self.referenceChanged.emit()
            

class XrdReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super(XrdReferenceDialog, self).__init__(parent)
        self.setWindowTitle("XRD Reference Dialog")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        
        self.fileNameLabel0 = QLabel(self.tr("File Name: "))
        self.layout.addWidget(self.fileNameLabel0, 0, 0, 1,1)
        self.fileNameLabel = QLabel(self.tr(""))
        self.layout.addWidget(self.fileNameLabel, 0, 1, 1, 1)
        self.fileNameButton = QPushButton("...", self)
        self.fileNameButton.clicked.connect(self.chooseFile)
        self.layout.addWidget(self.fileNameButton, 0, 2, 1, 1)
        
        self.layout.addWidget(QLabel('Title: '), 1, 0, 1, 1)
        self.titleEdit = QLineEdit(self)
        self.layout.addWidget(self.titleEdit, 1, 1, 1, 2)
        
        self.layout.addWidget(QLabel(self.tr("Color: ")), 2, 0, 1, 1)
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString("#000000"))
        self.colorButton = QPushButton(QIcon(pix), "#000000")
        self.colorButton.clicked.connect(self.chooseColor)
        self.layout.addWidget(self.colorButton, 2, 1, 1, 2)
        
        self.layout.addWidget(QLabel('Display: '), 3, 0, 1, 1)
        self.displayCheck = QCheckBox(self)
        self.displayCheck.setChecked(True)
        self.layout.addWidget(self.displayCheck, 3, 1, 1, 2)
                
        self.layout.addWidget(self.buttonBox, 4, 0, 1, 3)
        self.setLayout(self.layout)
        
        self.color = "#000000"

  
    def getData(self):
        data = {}
        data['File Name'] = self.fileNameLabel.text()
        data['Title'] = self.titleEdit.text()
        data['Color'] = self.color
        data['Display'] = self.displayCheck.isChecked()
        return data
    
    def setData(self, data):
        self.fileNameLabel0.hide()
        self.fileNameLabel.hide()
        self.fileNameButton.hide()
        
        self.titleEdit.setText(data['Title'])
        self.displayCheck.setChecked(data['Display'])
        pix = QPixmap(QSize(32,32))
        pix.fill(QColor.fromString(data['Color']))
        self.colorButton.setIcon(QIcon(pix))
        self.colorButton.setText(data['Color'])
        self.color = data['Color']
    
    def chooseFile(self):
        if self.settings.value("lastXrdReferenceOpenDir"):
            fileName, filterType = QFileDialog.getOpenFileName(None, "Open Reference", self.settings.value("lastXrdReferenceOpenDir"), self.tr("hkl-File (*.hkl *.csv *.txt)"))
        else:
            fileName, filterType = QFileDialog.getOpenFileName(None, "Open Reference", QDir.homePath(), self.tr("hkl-File (*.hkl *.csv *.txt)"))
        if fileName:
            self.fileNameLabel.setText(fileName)
            self.settings.setValue("lastXrdReferenceOpenDir", os.path.dirname(fileName))
            
    
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
        
class XrfDock(QDockWidget):
    referenceChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super(XrfDock, self).__init__(parent)
        self.setWindowTitle("XRF References")
        
        self.spectrum = None
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("XRFElementLines"):
            self.ElementLines = self.settings.value("XRFElementLines")
        else:
            self.ElementLines = json.load(open("ElementLines.json"))
            self.settings.setValue("XRFElementLines", self.ElementLines)
        
        self.mainWidget = QWidget()
        self.layout = QGridLayout()
        self.mainWidget.setLayout(self.layout)
        
        PeriodicTable = [['H', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'He'], 
                 ['Li', 'Be', '', '', '', '', '', '', '', '', '', '', 'B', 'C', 'N', 'O', 'F', 'Ne'],
                 ['Na', 'Mg', '', '', '', '', '', '', '', '', '', '', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar'],
                 ['K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr'],
                 ['Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe'],
                 ['Cs', 'Ba', '', 'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po', 'At', 'Rn'],
                 ['Fr', 'Ra', '', '(Rf)', '(Db)', '(Sg)', '(Bh)', '(Hs)', '(Mt)', '(Ds)', '(Rg)', '(Cn)', '(Nh)', '(Fl)', '(Mc)', '(Lv)', '(Ts)', '(Og)'],
                 ['', '', 'La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', ''],
                 ['', '', 'Ac', 'Th', 'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', '(Es)', '(Fm)', '(Md)', '(No)', '(Lr)', '']
                 ]
        self.Buttons = [] # buttons to access when loading spectrum to set right color
        for period in range(len(PeriodicTable)):
            for group in range(len(PeriodicTable[period])):
                if PeriodicTable[period][group] != "":
                    btn = QPushButton(PeriodicTable[period][group], self)
                    btn.setFixedSize(25,25)
                    if PeriodicTable[period][group].startswith("("):
                        btn.setEnabled(False)
                    else:
                        btn.clicked.connect(self.buttonClicked)
                        self.Buttons.append(btn)
                    self.layout.addWidget(btn, period, group)
        self.settingsBtn = QPushButton(self.tr("Change Element Color Settings"), self)
        self.layout.addWidget(self.settingsBtn, 0, 3, 1, 8)
        self.settingsBtn.clicked.connect(self.setElementColors)
        self.guessBtn = QPushButton(self.tr("Guess Elements from Peaks"), self)
        self.layout.addWidget(self.guessBtn, 1, 3, 1, 8)
        self.guessBtn.clicked.connect(self.guessElements)
        
        self.setWidget(self.mainWidget)
    
    def setSpectrum(self, spec):
        self.spectrum = spec
        for btn in self.Buttons:
            element = btn.text()
            if element in spec.references:
                btn.setStyleSheet("background-color: " + self.ElementLines[btn.text()]['Display Color'])
            else:
                btn.setStyleSheet("")
    
    def buttonClicked(self):
        btn = self.sender()
        element = btn.text()
        if element in self.spectrum.references:
            self.spectrum.references.remove(element)
            btn.setStyleSheet("")
        else: 
            btn.setStyleSheet("background-color: " + self.ElementLines[element]['Display Color'])
            self.spectrum.references.append(element)
        
        self.referenceChanged.emit()
    
    def setElementColors(self):
        dgl = ElementColorDialog(self)
        if dgl.exec():
            self.ElementLines = dgl.getData()
            self.settings.setValue("XRFElementLines", self.ElementLines)
            self.updateBtnColors()
    
    def updateBtnColors(self):
        for btn in self.Buttons:
            if btn.styleSheet() != "":
                btn.setStyleSheet("background-color: " + self.ElementLines[btn.text()]['Display Color'])
        self.referenceChanged.emit()
        
    def guessElements(self):
        guess = ""
        dgl = XrfElementGuessDialog()
        if len(self.spectrum.peaks) < 1:
            dgl.output.setPlainText("No Peaks. Please start PeakPicking before guessing Elements")
            dgl.exec()
            return
        
        for peak in self.spectrum.x[self.spectrum.peaks]:
            differences = []
            for element in self.ElementLines:
                for line in self.ElementLines[element]['Lines']:
                    d = peak*1000 - line['Energy']
                    d **= 2
                differences.append([element + " " + line['symbolSiegbahn'], round(line['Energy'] / 1000.0, 2), line['rel. Intensity'], d])
            differences = sorted(differences, key=lambda d: d[3])
            
            guess += "Element guess for peak at " + str(round(peak, 2)) + " keV\n"
            guess += "Line \t theo. Energy\t rel. Intensity\n"
            for i in range(10):
                guess += differences[i][0] + "\t" + str(differences[i][1]) + "\t" + str(differences[i][2]) + "\n"
            guess += "\n"
        dgl.output.setPlainText(guess)
        dgl.exec()
        
    
class ElementColorDialog(QDialog):
    def __init__(self, parent=None):
        super(ElementColorDialog, self).__init__(parent)
        self.setWindowTitle("XRF Element Color Dialog")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("XRFElementLines"):
            self.ElementLines = self.settings.value("XRFElementLines")
        else:
            self.ElementLines = json.load(open("ElementLines.json"))
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        
        self.elementListWidget = QListWidget(self)
        self.layout.addWidget(self.elementListWidget)
        for element in self.ElementLines:
            if element.startswith("("):
                continue
            pix = QPixmap(QSize(32,32))
            pix.fill(QColor.fromString(self.ElementLines[element]['Display Color']))
            self.elementListWidget.addItem(QListWidgetItem(QIcon(pix), element))
        self.elementListWidget.itemDoubleClicked.connect(self.chooseColor)
                
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
    
    def chooseColor(self, item):
        element = item.text()
        dgl = QColorDialog()
        dgl.setCurrentColor(QColor.fromString(self.ElementLines[element]['Display Color']))
        if dgl.exec():
            color = dgl.currentColor()
            pix = QPixmap(QSize(32,32))
            pix.fill(color)
            item.setIcon(QIcon(pix))
            self.ElementLines[element]['Display Color'] = color.name()
    
    def getData(self):
        return self.ElementLines

class XrfElementGuessDialog(QDialog):
    def __init__(self, parent=None):
        super(XrfElementGuessDialog, self).__init__(parent)
        self.setWindowTitle("XRF Element Guess Dialog")
                
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("XRFElementLines"):
            self.ElementLines = self.settings.value("XRFElementLines")
        else:
            self.ElementLines = json.load(open("ElementLines.json"))
                
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        
        self.output = QTextEdit(self)
        self.layout.addWidget(self.output)
        
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)