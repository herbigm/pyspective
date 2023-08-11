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
from spectrum import checkLength

class spectiveDocument(QWidget):
    def __init__(self, title = "", parent = None):
        super(spectiveDocument, self).__init__(parent)
        self.pages = []
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.currentPageIndex = None
        self.fileName = None
        
        self.settings = QSettings('TUBAF', 'pySpective')
        self.title = title
        
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
        if not fileName:
            fileName = self.fileName
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
            if numOfSpectra > 1:
                with open(fileName, "w") as f:
                    if self.title=="":
                        self.title = "untitled"
                    f.write(checkLength("##TITLE=" + self.title))
                    f.write(checkLength("\r\n##JCAMP-DX=5.01"))
                    f.write(checkLength("\r\n##DATA TYPE=LINK"))
                    f.write(checkLength("\r\n##BLOCKS=" + str(numOfSpectra + 1)))
                    f.write(checkLength("\r\n##$PAGES=" + str(len(self.pages))))
                    f.write(checkLength("\r\n##SAMPLE DESCRIPTION="))
                    f.write("\r\n")
                    for p in range(len(self.pages)):
                        for s in self.pages[p].spectra:
                            f.write("\r\n")
                            c = "##$ON PAGE=" + str(p+1)
                            f.write(s.getAsJCAMPDX(c))
                    f.write("\r\n")
                    f.write(checkLength("\r\n##END= $$" + self.title))
            else:
                with open(fileName, "w") as f:
                    for p in self.pages:
                        for s in p.spectra:
                            f.write(s.getAsJCAMPDX())
        
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
        
        