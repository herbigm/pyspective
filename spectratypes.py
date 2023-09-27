#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:10:47 2023

@author: marcus
"""

import spectrum

import numpy as np

opticalUnitsX = ["1/CM", "MICROMETERS", "NANOMETERS"]
opticalUnitsY = ["TRANSMITTANCE", "REFLECTANCE", "ABSORBANCE"]

class opticalSpectrum(spectrum.Spectrum):
    def __init__(self):
        super(opticalSpectrum, self).__init__()
    
    def convertXUnit(self, toUnit, fullXlim = [0,0]):
        fromUnit = self.metadata["Spectral Parameters"]["X Units"]
        if fromUnit != toUnit:
            if toUnit == "NANOMETERS":
                if fromUnit == "1/CM":
                    self.x = 1e7 / self.x
                    fullXlim[0] = 1e7 / fullXlim[0]
                    fullXlim[1] = 1e7 / fullXlim[1]
                elif fromUnit == "MICROMETERS":
                    self.x = self.x * 1e3
                    fullXlim[0] *= 1e3
                    fullXlim[1] *= 1e3
            elif toUnit == "MICROMETERS":
                if fromUnit == "1/CM":
                    self.x = 1e4 / self.x
                    fullXlim[0] = 1e4 / fullXlim[0]
                    fullXlim[1] = 1e4 / fullXlim[1]
                elif fromUnit == "NANOMETERS":
                    self.x = self.x * 1e-3
                    fullXlim[0] *= 1e-3
                    fullXlim[1] *= 1e-3
            elif toUnit == "1/CM":
                if fromUnit == "MICROMETERS":
                    self.x = 1e4 / self.x
                    fullXlim[0] = 1e4 / fullXlim[0]
                    fullXlim[1] = 1e4 / fullXlim[1]
                elif fromUnit == "NANOMETERS":
                    self.x = 1e7 / self.x
                    fullXlim[0] = 1e7 / fullXlim[0]
                    fullXlim[1] = 1e7 / fullXlim[1]
            self.metadata["Spectral Parameters"]["X Units"] = toUnit
        return fullXlim
    
    def convertYUnit(self, toUnit, fullYlim = [0,0]):
        fromUnit = self.metadata["Spectral Parameters"]["Y Units"]
        if toUnit != fromUnit:
            if toUnit == "TRANSMITTANCE":
                if fromUnit == "REFLECTANCE":
                    pass
                elif fromUnit == "ABSORBANCE":
                    self.y = 10 ** -(self.y)*100
                    low, up = fullYlim
                    fullYlim[0] = 10 ** -(up)*100
                    fullYlim[1] = 10 ** -(low)*100
            elif toUnit == "REFLECTANCE":
                if fromUnit == "TRANSMITTANCE":
                    pass
                elif fromUnit == "ABSORBANCE":
                    self.y = 10 ** -(self.y)*100
                    low, up = fullYlim
                    fullYlim[0] = 10 ** -(up)*100
                    fullYlim[1] = 10 ** -(low)*100
            elif toUnit == "ABSORBANCE":
                if fromUnit == "TRANSMITTANCE":
                    self.y = -np.log10(self.y/100)
                    low, up = fullYlim
                    fullYlim[0] = -np.log10(up/100)
                    fullYlim[1] = -np.log10(low/100)
                elif fromUnit == "REFLECTANCE":
                    self.y = -np.log10(self.y/100)
                    low, up = fullYlim
                    fullYlim[0] = -np.log10(up/100)
                    fullYlim[1] = -np.log10(low/100)
            self.metadata["Spectral Parameters"]["Y Units"] = toUnit
        return fullYlim

class ramanSpectrum(opticalSpectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave number [cm⁻¹]"
        self.ylabel = "raman intensity"
        self.metadata["Core Data"]["Data Type"] = "RAMAN SPECTRUM"
        
    def calculateDerivative(self):
        spec = ramanSpectrum()
        spec.x = self.x[1:] + np.diff(self.x)
        spec.y = np.diff(self.y)
        spec.yaxis = 1
        spec.title = self.title + " derivative"
        spec.metadata["Core Data"]["Title"] = self.metadata["Core Data"]["Title"] + " derivative"
        spec.metadata["Core Data"]["Data Type"] = "RAMAN SPECTRUM DERIVATIVE"
        return spec

class infraredSpectrum(opticalSpectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave number [cm⁻¹]"
        self.ylabel = "%Transmittance"
        self.metadata["Core Data"]["Data Type"] = "INFRARED SPECTRUM"
        
    def calculateDerivative(self):
        spec = infraredSpectrum()
        spec.x = self.x[1:] + np.diff(self.x)
        spec.y = np.diff(self.y)
        spec.yaxis = 1
        spec.title = self.title + " derivative"
        spec.metadata["Core Data"]["Title"] = self.metadata["Core Data"]["Title"] + " derivative"
        spec.metadata["Core Data"]["Data Type"] = "INFRARED SPECTRUM DERIVATIVE"
        return spec

class ultravioletSpectrum(opticalSpectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "wave lenght [nm]"
        self.ylabel = "absorbance"
        self.metadata["Core Data"]["Data Type"] = "ULTRAVIOLET SPECTRUM"
        
    def calculateDerivative(self):
        spec = ultravioletSpectrum()
        spec.x = self.x[1:] + np.diff(self.x)
        spec.y = np.diff(self.y)
        spec.yaxis = 1
        spec.title = self.title + " derivative"
        spec.metadata["Core Data"]["Title"] = self.metadata["Core Data"]["Title"] + " derivative"
        spec.metadata["Core Data"]["Data Type"] = "ULTRAVIOLET SPECTRUM DERIVATIVE"
        return spec

class xrfSpectrum(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "energy [keV]"
        self.ylabel = "counts per secound"
        self.metadata["Core Data"]["Data Type"] = "X-RAY FLUORESCENCE SPECTRUM"
        
class powderXRD(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "° 2 $\Theta$"
        self.ylabel = "counts per secound"
        self.metadata["Core Data"]["Data Type"] = "POWDER X-RAY DIFFRACTION"