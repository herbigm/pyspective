#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:10:47 2023

@author: marcus
"""

import spectrum

from PyQt6.QtCore import QDir

from PyQt6.QtWidgets import (
    QFileDialog,
)

import numpy as np

class ramanSpectrum(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave lenght [cm⁻¹]"
        self.ylabel = "absorbance"
    
    def openFile(self, baseDir=None, fileName=None):
        if not fileName:
            if not baseDir:
                baseDir = QDir.homePath()
            fileName, _ = QFileDialog.getOpenFileName(None, "Open Raman spectrum", baseDir, "dpt files (*.dpt)")
            print(fileName)
        if fileName != "":
            self.fileName = fileName
            self.x, self.y = np.loadtxt(fileName, unpack=True, delimiter=",")
            if len(self.x) > 0:
                self.xlim = [max(self.x), min(self.x)]
                self.ylim = [min(self.y), max(self.y)]
                self.baseline = 0
                return True
            else: 
                return False
        return False