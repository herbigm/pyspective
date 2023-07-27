#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:13:34 2023

@author: marcus

This module includes all standard functions of a spectrum.
It is the base calss of all other spectra types. 
"""

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QFileDialog,
)

class Spectrum:
    def __init__(self, xlim = [], ylim = [], yBaseline=0):
        self.xlim = xlim
        self.ylim = ylim
        self.yBaseline = yBaseline
        self.ylabel = ""
        self.xlabel = ""
        self.fileName = ""
        self.x = []
        self.y = []
        self.metadata = {}
        self.metadata["Core Data"] = {}
        self.metadata["Core Data"]["Title"] = ""
        self.metadata["Core Data"]["Data Type"] = ""
        self.metadata["Core Data"]["Origin"] = ""
        self.metadata["Core Data"]["Owner"] = ""
        self.metadata["Spectral Parameters"] = {}
        self.metadata["Spectral Parameters"]["X Units"] = ""
        self.metadata["Spectral Parameters"]["Y Units"] = ""
        self.metadata["Spectral Parameters"]["Resolution"] = ""
        self.metadata["Spectral Parameters"]["Delta X"] = ""
        self.metadata["Notes"] = {}
        self.metadata["Notes"]["Date Time"] = ""
        self.metadata["Notes"]["Source Reference"] = ""
        self.metadata["Notes"]["Cross Reference"] = ""
        self.metadata["Sample Information"] = {}
        self.metadata["Sample Information"]["Sample Description"] = ""
        self.metadata["Sample Information"]["CAS Name"] = ""
        self.metadata["Sample Information"]["IUPAC Name"] = ""
        self.metadata["Sample Information"]["Names"] = ""
        self.metadata["Sample Information"]["Molform"] = ""
        self.metadata["Sample Information"]["CAS Registry No"] = ""
        self.metadata["Sample Information"]["Wiswesser"] = ""
        self.metadata["Sample Information"]["Beilstein Lawson No"] = ""
        self.metadata["Sample Information"]["Melting Point"] = ""
        self.metadata["Sample Information"]["Boiling Point"] = ""
        self.metadata["Sample Information"]["Refractive Index"] = ""
        self.metadata["Sample Information"]["Density"] = ""
        self.metadata["Sample Information"]["Molecular Weight"] = ""
        self.metadata["Sample Information"]["Concentrations"] = ""
        self.metadata["Equipment Information"] = {}
        self.metadata["Equipment Information"]["Spectrometer"] = ""
        self.metadata["Equipment Information"]["Instrumental Parameters"] = ""
        self.metadata["Sampling Information"] = {}
        self.metadata["Sampling Information"]["Sampling Procedure"] = ""
        self.metadata["Sampling Information"]["State"] = ""
        self.metadata["Sampling Information"]["Path Length"] = ""
        self.metadata["Sampling Information"]["Pressure"] = ""
        self.metadata["Sampling Information"]["Temperature"] = ""
        self.metadata["Sampling Information"]["Data Processing"] = ""
        self.metadata["Comments"] = ""
    
    def openFreeText(self, fileName=None, options=None, baseDir=QDir.homePath()):
        if not options:
            options = {}
            options["Spectrum Type"] = "undefined"
            options["File Encoding"] = "utf-8"
            options["Comment Character"] = "#"
            options["Column Delimiter"] = ""
            options["Decimal Separator"] = "."
            options["skip Rows"] = 0
            
        if not fileName:
            fileName, _ = QFileDialog.getOpenFileName(None, "Open new spectrum", baseDir, "all Files (*.*)")
        if not fileName:
            return False
        with open(fileName, encoding=options["File Encoding"]) as f:
            lines = f.readlines()
            linenumber = 0
            comments = ""
            for line in lines:
                line = line.strip()
                if linenumber < options["skip Rows"]:
                    comments += "\r\n" + line
                    linenumber += 1
                    continue
                if line.startswith(options['Comment Character']):
                    comments += "\r\n" + line
                    continue
                columns = line.split(options["Column Delimiter"])
                if len(columns) > 1:
                    try:
                        if not options["Decimal Separator"] == ".":
                            self.x.append(float(columns[0].replace(options["Decimal Separator"], ".")))
                            self.y.append(float(columns[1].replace(options["Decimal Separator"], ".")))
                        else:
                            self.x.append(float(columns[0]))
                            self.y.append(float(columns[1]))
                    except:
                        return False
            self.metadata["Comments"] = comments
            if len(self.x) > 0:
                self.xlim = [max(self.x), min(self.x)]
                self.ylim = [min(self.y), max(self.y)]
                return True
        return False
