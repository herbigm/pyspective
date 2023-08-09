#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QVBoxLayout
)

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle

import numpy as np

import specplot

class spectiveDocument:
    def __init__(self):
        self.pages = []
        
    def addPage(self, pageType):
        if pageType == "plot":
            page = spectivePlotPage()
        
        self.pages.append(page)
        self.pages[-1].title = "Page " + str(len(self.pages))

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
        
        