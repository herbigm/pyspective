#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

import os

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QDir, QSettings
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QFileDialog
)

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle

import numpy as np

import specplot

class spectiveDocument(QWidget):
    def __init__(self, parent = None):
        super(spectiveDocument, self).__init__(parent)
        self.pages = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.currentPageIndex = None
        self.fileName = None
        
        self.settings = QSettings('TUBAF', 'pySpective')
        
    def addPage(self, pageType):
        if pageType == "plot":
            page = spectivePlotPage()
        
        self.pages.append(page)
        self.pages[-1].title = "Page " + str(len(self.pages))
        if self.currentPageIndex != None:
            self.pages[self.currentPageIndex].plotWidget.hide()
        self.layout.addWidget(self.pages[-1].plotWidget)
        self.currentPageIndex = len(self.pages) - 1
    
    def goToPage(self, index):
        if self.currentPageIndex != None:
            self.pages[self.currentPageIndex].plotWidget.hide()
        self.pages[index].plotWidget.show()
        self.currentPageIndex = index
        
    def saveDocument(self, fileName = None):
        if not self.fileName and not fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
        self.fileName = fileName
        # save spectra here
        # get number of spectra
        numOfSpectra = 0
        for i in self.pages:
            numOfSpectra += len(i.spectra)
        print(numOfSpectra)
        
    def getFigureData(self):
        return self.pages[self.currentPageIndex].plotWidget.getFigureData()
    
    def setFigureData(self, data):
        self.pages[self.currentPageIndex].plotWidget.setFigureData(data)
        

class spectivePlotPage(QWidget):
    def __init__(self, parent = None):
        super(spectivePlotPage, self).__init__(parent)
        self.plotWidget = specplot.specplot(self)
        self.layout = QVBoxLayout(self)
        
        self.layout.addWidget(self.plotWidget)
        
        self.setLayout(self.layout)
        self.spectra = []
        self.title = ""
        
    def addSpectrum(self, spectrum):
        self.spectra.append(spectrum)
        self.plotWidget.addSpectrum(spectrum)
        
        