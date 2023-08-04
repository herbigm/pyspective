#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

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
        pass

class spectivePage(QWidget):
    def __init__(self, parent = None):
        super(spectivePage, self).__init__(parent)
        self.plotWidget = specplot.specplot(self)
        
        self.spectra = []
    
    def addSpectrum(self, spectrum):
        pass
        
        