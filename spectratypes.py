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
        self.xlabel = "wave number [cm⁻¹]"
        self.ylabel = "raman intensity"
        self.metadata["Core Data"]["Data Type"] = "RAMAN SPECTRUM"

class infraredSpectrum(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave number [cm⁻¹]"
        self.ylabel = "%Transmittance"
        self.metadata["Core Data"]["Data Type"] = "INFRARED SPECTRUM"

class ultravioletSpectrum(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave lenght [nm]"
        self.ylabel = "absorbance"
        self.metadata["Core Data"]["Data Type"] = "ULTRAVIOLET SPECTRUM"