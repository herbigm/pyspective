#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

import os
import json

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
                    pageInfoSet = False
                    for s in self.pages[p].spectra:
                        f.write("\r\n")
                        c = "##$ON PAGE=" + str(p+1)
                        if not pageInfoSet:
                            c += "\r\n##$PAGE TITLE=" + self.pages[p].title
                            c += "\r\n##$PLOT TITLE=" + self.pages[p].plotTitle
                            c += "\r\n##$XLABEL=" + s.xlabel
                            c += "\r\n##$YLABEL=" + s.ylabel
                            c += "\r\n##$XLIM=" + json.dumps(self.pages[p].plotWidget.ax.get_xlim())
                            c += "\r\n##$YLIM=" + json.dumps(self.pages[p].plotWidget.ax.get_ylim())
                            pageInfoSet = True
                        f.write(s.getAsJCAMPDX(c))
                f.write("\r\n")
                f.write(checkLength("\r\n##END= $$" + self.title))
        
    def saveSpectrum(self, spectrumIndex, fileName = None):
        if not fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            with open(fileName, "w") as f:
                page = self.pages[self.currentPageIndex]
                f.write(page.spectra[spectrumIndex].getAsJCAMPDX())
    
    def savePage(self, fileName = None):
        if not fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            with open(fileName, "w") as f:
                page = self.pages[self.currentPageIndex]
                if page.title=="":
                    page.title = "untitled"
                f.write(checkLength("##TITLE=" + page.title))
                f.write(checkLength("\r\n##JCAMP-DX=5.01"))
                f.write(checkLength("\r\n##DATA TYPE=LINK"))
                f.write(checkLength("\r\n##BLOCKS=" + str(len(page.spectra) + 1)))
                f.write(checkLength("\r\n##SAMPLE DESCRIPTION="))
                f.write("\r\n")
                for s in page.spectra:
                    f.write("\r\n")
                    f.write(s.getAsJCAMPDX())
                f.write("\r\n")
                f.write(checkLength("\r\n##END= $$" + page.title))
        
    def getFigureData(self):
        page = self.pages[self.currentPageIndex]
        return page.getFigureData()
    
    def setFigureData(self, data):
        self.pages[self.currentPageIndex].setFigureData(data)        
        

class spectivePlotPage(QWidget):
    def __init__(self, parent = None):
        super(spectivePlotPage, self).__init__(parent)
        self.plotWidget = specplot.specplot(self)
        self.layout = QVBoxLayout(self)
        
        self.layout.addWidget(self.plotWidget)
        
        self.setLayout(self.layout)
        self.spectra = []
        self.title = ""
        self.plotTitle = ""
        
    def addSpectrum(self, spectrum):
        self.spectra.append(spectrum)
        self.spectra[-1].color = self.plotWidget.addSpectrum(spectrum)
        if spectrum.displayData['Plot Title'] != "":
            self.plotWidget.supTitle = spectrum.displayData['Plot Title']
            self.plotTitle = spectrum.displayData['Plot Title']
        if spectrum.displayData['Page Title'] != "":
            self.title = spectrum.displayData['Page Title']
        if spectrum.xlabel != "":
            self.plotWidget.ax.set_xlabel(spectrum.xlabel)
        if spectrum.ylabel != "":
            self.plotWidget.ax.set_ylabel(spectrum.ylabel)
        if spectrum.displayData['xlim']:
            self.plotWidget.ax.set_xlim(spectrum.displayData['xlim'])
        if spectrum.displayData['ylim']:
            self.plotWidget.ax.set_ylim(spectrum.displayData['ylim'])
        self.plotWidget.updatePlot()
    
    def getFigureData(self):
        data = {}
        data["XLabel"] = self.plotWidget.ax.get_xlabel()
        data["YLabel"] = self.plotWidget.ax.get_ylabel()
        data["XUnit"] = self.plotWidget.XUnit
        data["YUnit"] = self.plotWidget.YUnit
        data["Xlim"] = self.plotWidget.ax.get_xlim()
        data["Ylim"] = self.plotWidget.ax.get_ylim()
        data["Title"] = self.plotWidget.supTitle
        data["PageTitle"] = self.title
        return data

    def setFigureData(self, data):
        self.title = data["PageTitle"]
        for s in self.spectra:
            s.xlabel = data["XLabel"]
            s.ylabel = data["YLabel"]
            
            fullXlim = s.convertXUnit(data["XUnit"], self.plotWidget.fullXlim.copy())
            fullYlim = s.convertYUnit(data["YUnit"], self.plotWidget.fullYlim.copy())
                        
            if data["invertX"]:
                s.x = np.flip(s.x)
                s.y = np.flip(s.y)
        
        self.plotWidget.fullXlim = fullXlim
        self.plotWidget.fullYlim = fullYlim
        
        if data["invertX"]:
            self.plotWidget.fullXlim[0], self.plotWidget.fullXlim[1] = self.plotWidget.fullXlim[1], self.plotWidget.fullXlim[0]
        self.plotWidget.ax.set_xlabel(data["XLabel"])
        self.plotWidget.ax.set_ylabel(data["YLabel"])
        
        self.plotWidget.XUnit = data["XUnit"]
        self.plotWidget.YUnit = data["YUnit"]
        
        self.plotWidget.ax.set_xlim(data["Xlim"])
        self.plotWidget.ax.set_ylim(data["Ylim"])
        
        self.plotWidget.supTitle = data["Title"]
        self.plotTitle = data["Title"]
        
        self.plotWidget.updatePlot()
        