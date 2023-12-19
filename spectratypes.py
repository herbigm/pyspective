#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:10:47 2023

@author: marcus
"""

import spectrum
import json
import os
import datetime
import struct

import numpy as np
from scipy import stats

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
        
        self.displayData["Legend"] = "best"
        
        self.references = []
        
    def getAsJCAMPDX(self, insert=None):
        if len(self.references) > 0:
            insert += "\r\n##$XRF REFERENCES=" + json.dumps(self.references)
        return super().getAsJCAMPDX(insert)
    
    def openMCA(self, fileName):
        """
        Opens an mca file (DESY file format)

        Parameters
        ----------
        filename : String
            The path to the file, which should be opened
            
        Returns
        -------
        None.

        """
        if not fileName:
            print("No file name given. ")
            return False
        if not os.path.exists(fileName):
            print("file does not exist!")
            return False
        
        f = open(fileName, "r", encoding="iso-8859-1")
        lines = f.readlines()
        f.close()

        counts = []
        currentLine = 0
        comments = ""
        while currentLine < len(lines):
            if lines[currentLine].strip() == "<<CALIBRATION>>": # Beide Punkte für die Energiekali auslesen
                currentLine += 2
                CaliLine1 = lines[currentLine]
                CaliChannel = []
                CaliEnergy = []
                Number = []
                for Z in CaliLine1:   # Das ist bissl umständlich aber passt sich an verschiedene Zahlenlängen der Kaliwerte an
                    if Z != " ":
                        Number.append(Z)
                    if Z == " ":
                        Number="".join(Number)
                        CaliChannel.append(float(str(Number)))
                        Number = []
                Number="".join(Number)
                CaliEnergy.append(float(str(Number[:-1])))
                Number = []
                currentLine += 1
                CaliLine2 = lines[currentLine]
                for Z in CaliLine2:
                    if Z != " ":
                        Number.append(Z)
                    if Z == " ":
                        Number="".join(Number)
                        CaliChannel.append(float(str(Number)))
                        Number = []
                Number="".join(Number)
                CaliEnergy.append(float(str(Number[:-1])))
            elif lines[currentLine].strip().startswith("START_TIME"):
                print(lines[currentLine][13:])
                self.metadata["Notes"]["Date Time"] = datetime.datetime.strptime(lines[currentLine][13:].strip(), "%m/%d/%Y %H:%M:%S")
                currentLine += 1
                
            elif lines[currentLine].strip() == "<<DATA>>":
                currentLine += 1
                while currentLine < len(lines):
                    if lines[currentLine].strip() == "<<END>>":
                        currentLine += 1
                        break
                    else:
                        counts.append(int(lines[currentLine].strip()))
                        currentLine += 1
            else:
                comments += lines[currentLine]
                currentLine += 1
                
        # Berechnen der Kalibrierdaten

        slope, intercept, r, p, std_err = stats.linregress(CaliChannel, CaliEnergy )
        Energy = []

        for i in range(len(counts)):
            y = slope * i + intercept
            Energy.append(y)

        # die Listen zu numpy array konvertieren
        self.x = np.array(Energy)
        self.y = np.array(counts)
        self.metadata["Comments"] = comments
        self.metadata["Core Data"]["Title"] = os.path.basename(fileName)
        self.title = os.path.basename(fileName)
        self.xlim = [min(self.x), max(self.x)]
        self.ylim = [min(self.y), max(self.y)]
        return True
    
    def openPyXrfaJSON(self, fileName):
        if not fileName:
            print("No file name given. ")
            return False
        if not os.path.exists(fileName):
            print("file does not exist!")
            return False
        
        data = json.load(open(fileName))
        self.x = np.array(data['energies'])
        self.y = np.array(data['counts'])
        self.metadata["Core Data"]["Title"] = os.path.basename(fileName)
        self.title = os.path.basename(fileName)
        self.xlim = [min(self.x), max(self.x)]
        self.ylim = [min(self.y), max(self.y)]
        self.references = []
        
        for element in data['elementsAndColor']:
            self.references.append(element[0])
            
        return True
    
    def openAndSetXY(self, x, y):
        self.x = x
        self.xlim = [min(x), max(x)]
        self.y = y
        self.ylim = [min(y), max(y)]
                
        
class powderXRD(spectrum.Spectrum):
    def __init__(self):
        super().__init__()
        self.xlabel = "° 2 $\Theta$"
        self.ylabel = "counts per secound"
        self.metadata["Core Data"]["Data Type"] = "POWDER X-RAY DIFFRACTION"
        
        self.displayData["Legend"] = "best"
        
        self.references = []
        self.wavelength = 1.5418
        
    def getAsJCAMPDX(self, insert=None):
        if len(self.references) > 0:
            insert += "\r\n##$XRD REFERENCES=" + json.dumps(self.references)
        return super().getAsJCAMPDX(insert)
    
    def openBrukerRaw4(self, fileName):
        fp = open(fileName, "rb")
        fileSize = os.path.getsize(fileName)

        fp.seek(0)

        bruker_version = str(fp.read(7).decode("iso-8859-1"))

        fp.seek(12)
        bruker_date = str(fp.read(10).decode("iso-8859-1"))

        fp.seek(24)
        bruker_time = str(fp.read(8).decode("iso-8859-1"))

        bruker_datetime = datetime.datetime.strptime(bruker_date + "H" + bruker_time, "%m/%d/%YH%H:%M:%S")

        fp.seek(471)
        n_points = struct.unpack('i', fp.read(4))[0]

        fp.seek(539)
        start, step = struct.unpack('dd', fp.read(16))

        x = np.linspace(start, start+n_points*step, num=n_points)

        fp.seek(fileSize - n_points*4)
        y = []
        while True:
            b = fp.read(4)
            if not b:
                break
            d = struct.unpack('f', b)[0]
            y.append(d /  171.0) # i do not know where the 171 comes from....
        
        self.x = np.array(x)
        self.y = np.array(y)
        self.metadata["Notes"]["Date Time"] = bruker_datetime
        self.metadata["Comments"] += "Bruker Version: " + bruker_version
        self.metadata["Core Data"]["Title"] = os.path.basename(fileName)
        self.title = os.path.basename(fileName)
        self.xlim = [min(self.x), max(self.x)]
        self.ylim = [min(self.y), max(self.y)]
        return True