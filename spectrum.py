#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 11:13:34 2023

@author: marcus

This module includes all standard functions of a spectrum.
It is the base calss of all other spectra types. 
"""

import re
import datetime

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QFileDialog,
)

import numpy as np
import json
from scipy.signal import find_peaks

class Spectrum:
    def __init__(self, xlim = [0,0], ylim = [0,0]):
        self.xlim = xlim
        self.ylim = ylim
        self.ylabel = ""
        self.xlabel = ""
        self.fileName = ""
        self.title = ""
        self.color = ""
        self.lineStyle = "-"
        self.markerStyle = ""
        self.x = []
        self.y = []
        self.yaxis = 0
        self.peaks = []
        self.peakString = ""
        self.peakParameter = {}
        self.peakParameter["Height"] = ""
        self.peakParameter["Threshold"] = ""
        self.peakParameter["Distance"] = 1
        self.peakParameter["Prominence"] = ""
        self.peakParameter["Width"] = ""
        self.peakParameter["Color"] = "#0064a8"
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
        self.metadata["Notes"]["Date Time"] = datetime.datetime.now()
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
        self.displayData = {}
        self.displayData['Page'] = None
        self.displayData['Page Title'] = ""
        self.displayData['Plot Title'] = ""
        self.displayData["xlim"] = None
        self.displayData["ylim"] = None
        self.displayData["Legend"] = ""
    
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
                self.x = np.array(self.x)
                self.y = np.array(self.y)
                return True
        return False
    
    def openJCAMPDXfromString(self, s):
        ldr = re.compile("##([\$\w\s/-]*)=(.*)$", re.IGNORECASE)
        lines = s.splitlines()
        # Definition of Factors and Delta for reading data block, may change due to file content
        xFactor = 1
        yFactor = 1
        deltaX = None
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line.startswith("##"):
                # It is an Labeled Data Record (LDR), which stops at the next LDR!
                m = ldr.match(line)
                if m:
                    label = m.group(1).upper()
                    data = m.group(2).strip()
                    if label != "XYDATA" and label != "END":
                        while not lines[i+1].startswith("##"):
                            data += "\r\n" + lines[i+1].strip()
                            i += 1
                    if label == "TITLE":
                        self.metadata["Core Data"]["Title"] = data
                        self.title = data
                    elif label == "JCAMP-DX":
                        pass # no nothing with the JCAMP-DX version...
                    elif label == "DATA TYPE" or label == "DATATYPE":
                        self.metadata["Core Data"]["Data Type"] = data
                    elif label == "BLOCKS":
                        pass # do nothing with the amount of blocks
                    elif label == "XUNITS":
                        self.metadata["Spectral Parameters"]["X Units"] = data
                        self.xlabel = data
                    elif label == "YUNITS":
                        self.metadata["Spectral Parameters"]["Y Units"] = data
                        self.ylabel = data
                    elif label == "FIRSTX":
                        firstx = float(data)
                        self.xlim[0] = float(data)
                    elif label == "LASTX":
                        lastx = float(data)
                        self.xlim[1] = float(data)
                    elif label == "FIRSTY":
                        pass # do nothing with the first Y value
                    elif label == "MAXX":
                        self.xlim[1] = float(data)
                    elif label == "MINX":
                        self.xlim[0] = float(data)
                    elif label == "MAXY":
                        self.ylim[1] = float(data)
                    elif label == "MINY":
                        self.ylim[0] = float(data)
                    elif label == "XFACTOR":
                        xFactor = float(data)
                    elif label == "YFACTOR":
                        yFactor = float(data)
                    elif label == "NPOINTS":
                        npoints = int(data)
                    elif label == "RESOLUTION":
                        self.metadata["Spectral Parameters"]["Resolution"] = data
                    elif label == "DELTAX":
                        deltaX = float(data)
                        self.metadata["Spectral Parameters"]["Delta X"] = data
                    elif label == "CLASS":
                        pass # do nothing with the COBLETZ Class of Sepctrum
                    elif label == "ORIGIN":
                        self.metadata["Core Data"]["Origin"] = data
                    elif label == "OWNER":
                        self.metadata["Core Data"]["Owner"] = data
                    elif label == "DATE":
                        date = datetime.datetime.strptime(data, "%y/%m/%d")
                    elif label == "TIME":
                        time = datetime.datetime.strptime(data, "%H:%M:%S")
                    elif label == "LONGDATE":
                        if len(data) < 11:
                            date = datetime.datetime.strptime(data, "%Y/%m/%d")
                        elif len(data) < 17:
                            date = datetime.datetime.strptime(data, "%Y/%m/%d %H:%M")
                        elif len(data) < 25:
                            date = datetime.datetime.strptime(data, "%Y/%m/%d %H:%M:%S")
                            date = date.replace(microsecond=int(data[20:25].lstrip("0")))
                        else:
                            date = datetime.datetime.strptime(data, "%Y/%m/%d %H:%M:%S.%f%z")
                    elif label == "SOURCE REFERENCE":
                        self.metadata["Notes"]["Source Reference"] = data
                    elif label == "CROSS REFERENCE":
                        self.metadata["Notes"]["Cross Reference"] = data
                    elif label == "SAMPLE DESCRIPTION":
                        self.metadata["Sample Information"]["Sample Description"] = data
                    elif label == "CAS NAME":
                        self.metadata["Sample Information"]["CAS Name"] = data
                    elif label == "IUPAC NAME":
                        self.metadata["Sample Information"]["IUPAC Name"] = data
                    elif label == "NAMES":
                        self.metadata["Sample Information"]["Names"] = data
                    elif label == "MOLFORM":
                        self.metadata["Sample Information"]["Molform"] = data
                    elif label == "CAS REGISTRY NO":
                        self.metadata["Sample Information"]["CAS Registry No"] = data
                    elif label == "WISWESSER":
                        self.metadata["Sample Information"]["Wiswesser"] = data
                    elif label == "BEILSTEIN LAWSON NO":
                        self.metadata["Sample Information"]["Beilstein Lawson No"] = data
                    elif label == "MP":
                        self.metadata["Sample Information"]["Melting Point"] = data
                    elif label == "BP":
                        self.metadata["Sample Information"]["Boiling Point"] = data
                    elif label == "REFRACTIVE INDEX":
                        self.metadata["Sample Information"]["Refractive Index"] = data
                    elif label == "DENSITY":
                        self.metadata["Sample Information"]["Density"] = data
                    elif label == "MW":
                        self.metadata["Sample Information"]["Molecular Weight"] = data
                    elif label == "CONCENTRATIONS":
                        self.metadata["Sample Information"]["Concentrations"] = data
                    elif label == "SPECTROMETER" or label == "DATA SYSTEM" or label == "SPECTROMETER/DATA SYSTEM":
                        self.metadata["Equipment Information"]["Spectrometer"] = data
                    elif label == "INSTRUMENTAL PARAMETERS":
                        self.metadata["Equipment Information"]["Instrumental Parameters"] = data
                    elif label == "SAMPLING PROCEDURE":
                        self.metadata["Sampling Information"]["Sampling Procedure"] = data
                    elif label == "STATE":
                        self.metadata["Sampling Information"]["State"] = data
                    elif label == "PATH LENGTH":
                        self.metadata["Sampling Information"]["Path Length"] = data
                    elif label == "PRESSURE":
                        self.metadata["Sampling Information"]["Pressure"] = data
                    elif label == "TEMPERATURE":
                        self.metadata["Sampling Information"]["Temperature"] = data
                    elif label == "DATA PROCESSING":
                        self.metadata["Sampling Information"]["Data Processing"] = data
                    elif label == "XYDATA":
                        # parse the data until ##END=
                        if not deltaX:
                            deltaX = (lastx - firstx) / (npoints - 1)
                        i += 1
                        while not lines[i].startswith("##"):
                            values = lines[i].split()
                            for v in range(1, len(values)):
                                self.x.append((float(values[0]) + (v-1)*deltaX) * xFactor)
                                self.y.append(float(values[v]) * yFactor)
                            i += 1
                        i -= 1
                        self.x = np.array(self.x)
                        self.y = np.array(self.y)
                    elif label == "END":
                        break
                    # Now starting display settings
                    elif label == "$ON PAGE":
                        self.displayData['Page'] = int(data)
                    elif label == "$PAGE TITLE":
                        self.displayData['Page Title'] = data
                    elif label == "$PLOT TITLE":
                        self.displayData['Plot Title'] = data
                    elif label == "$XLABEL":
                        self.xlabel = data
                    elif label == "$YLABEL":
                        self.ylabel = data
                    elif label == "$XLIM":
                        self.displayData['xlim'] = json.loads(data)
                    elif label == "$YLIM":
                        self.displayData['ylim'] = json.loads(data)
                    elif label == "$LEGEND":
                        self.displayData['Legend'] = data.replace("\r\n", "")
                    elif label == "$COLOR":
                        self.color = data.replace("\r\n", "")
                    elif label == "$LINE STYLE":
                        self.lineStyle = data.replace("\r\n", "")
                    elif label == "$MARKER STYLE":
                        self.markerStyle = data.replace("\r\n", "")
                    elif label == "$PEAK LIST":
                        self.peaks = np.array(json.loads(data.replace("\r\n", "")))
                    elif label == "$PEAK STRING":
                        self.peakString = data
                    elif label == "$PEAK PARAMETER":
                        self.peakParameter = json.loads(data.replace("\r\n", ""))
                    else: 
                        self.metadata["Comments"] += "\r\n" + data
                else:
                    self.metadata["Comments"] += "\r\n" + line.lstrip("$")
            else:
                self.metadata["Comments"] += "\r\n" + line.lstrip("$")
            i += 1
        if date and time:
            self.metadata["Notes"]["Date Time"] = datetime.datetime(date.year, date.month, date.day, time.hour, time.minute, time.second, time.microsecond, time.tzinfo)
        elif date:
            self.metadata["Notes"]["Date Time"] = date
        return True

    def getAsJCAMPDX(self, insert=None):
        c = checkLength("##TITLE=" + self.metadata["Core Data"]["Title"])
        c += checkLength("\r\n##JCAMP-DX=5.01")
        c += checkLength("\r\n##DATA TYPE=" + self.metadata["Core Data"]["Data Type"])
        c += checkLength("\r\n##ORIGIN=" + self.metadata["Core Data"]["Origin"])
        c += checkLength("\r\n##OWNER=" + self.metadata["Core Data"]["Owner"])
        if insert:
            c += checkLength("\r\n" + insert)
        c += checkLength("\r\n##$COLOR=" + self.color)
        c += checkLength("\r\n##$LINE STYLE=" + self.lineStyle)
        c += checkLength("\r\n##$MARKER STYLE=" + self.markerStyle)
        c += checkLength("\r\n##$PEAK PARAMETER=" + json.dumps(self.peakParameter))
        c += checkLength("\r\n##$PEAK STRING=" + self.peakString)
        c += checkLength("\r\n##$PEAK LIST=" + json.dumps(list(self.peaks), default=int))
        c += checkLength("\r\n##XUNITS=" + self.metadata["Spectral Parameters"]["X Units"])
        c += checkLength("\r\n##YUNITS=" + self.metadata["Spectral Parameters"]["Y Units"])
        c += checkLength("\r\n##MAXX=" + str(max(self.x)))
        c += checkLength("\r\n##MINX=" + str(min(self.x)))
        c += checkLength("\r\n##MAXY=" + str(max(self.y)))
        c += checkLength("\r\n##MINY=" + str(min(self.y)))
        c += checkLength("\r\n##FIRSTX=" + str(self.x[0]))
        c += checkLength("\r\n##LASTX=" + str(self.x[-1]))
        c += checkLength("\r\n##XFACTOR=1.000") # No factor, since no memory problems are present today!
        # yFactor = max(self.y)/32000
        c += checkLength("\r\n##YFACTOR=1.000") # No factor, since no memory problems are present today!
        c += checkLength("\r\n##NPOINTS=" + str(len(self.y)))
        c += checkLength("\r\n##FIRSTY=" + str(round(self.y[0])))
        if self.metadata["Spectral Parameters"]["Resolution"] != "":
            c += checkLength("\r\n##RESOLUTION=" + self.metadata["Spectral Parameters"]["Resolution"])
        if self.metadata["Spectral Parameters"]["Delta X"] != "":
            c += checkLength("\r\n##DELTAX=" + self.metadata["Spectral Parameters"]["Delta X"])
        else:
            c += checkLength("\r\n##DELTAX=" + str(round((max(self.x) - min(self.x)) / len(self.x), 6)))
        if self.metadata["Notes"]["Date Time"] != "":
            c += checkLength("\r\n##LONGDATE=" + self.metadata["Notes"]["Date Time"].strftime("%Y/%m/%d"))
            c += checkLength("\r\n##TIME=" + self.metadata["Notes"]["Date Time"].strftime("%H:%M:%S"))
        if self.metadata["Notes"]["Source Reference"] != "":
            c += checkLength("\r\n##SOURCE REFERENCE=" + self.metadata["Notes"]["Source Reference"])
        if self.metadata["Notes"]["Cross Reference"] != "":
            c += checkLength("\r\n##CROSS REFERENCE=" + self.metadata["Notes"]["Cross Reference"])
        if self.metadata["Sample Information"]["Sample Description"] != "":
            c += checkLength("\r\n##SAMPLE DESCRIPTION=" + self.metadata["Sample Information"]["Sample Description"])
        if self.metadata["Sample Information"]["CAS Name"] != "":
            c += checkLength("\r\n##CAS NAME=" + self.metadata["Sample Information"]["CAS Name"])
        if self.metadata["Sample Information"]["IUPAC Name"] != "":
            c += checkLength("\r\n##IUPAC NAME=" + self.metadata["Sample Information"]["IUPAC Name"])
        if self.metadata["Sample Information"]["Names"] != "":
            c += checkLength("\r\n##NAMES=" + self.metadata["Sample Information"]["Names"])
        if self.metadata["Sample Information"]["Molform"] != "":
            c += checkLength("\r\n##MOLFORM=" + self.metadata["Sample Information"]["Molform"])
        if self.metadata["Sample Information"]["CAS Registry No"] != "":
            c += checkLength("\r\n##CAS REGISTRY NO=" + self.metadata["Sample Information"]["CAS Registry No"])
        if self.metadata["Sample Information"]["Wiswesser"] != "":
            c += checkLength("\r\n##WISWESSER=" + self.metadata["Sample Information"]["Wiswesser"])
        if self.metadata["Sample Information"]["Beilstein Lawson No"] != "":
            c += checkLength("\r\n##BEILSTEIN LAWSON NO=" + self.metadata["Sample Information"]["Beilstein Lawson No"])
        if self.metadata["Sample Information"]["Melting Point"] != "":
            c += checkLength("\r\n##MP=" + self.metadata["Sample Information"]["Melting Point"])
        if self.metadata["Sample Information"]["Boiling Point"] != "":
            c += checkLength("\r\n##BP=" + self.metadata["Sample Information"]["Boiling Point"])
        if self.metadata["Sample Information"]["Refractive Index"] != "":
            c += checkLength("\r\n##REFRACTIVE INDEX=" + self.metadata["Sample Information"]["Refractive Index"])
        if self.metadata["Sample Information"]["Density"] != "":
            c += checkLength("\r\n##DENSITY=" + self.metadata["Sample Information"]["Density"])
        if self.metadata["Sample Information"]["Molecular Weight"] != "":
            c += checkLength("\r\n##MW=" + self.metadata["Sample Information"]["Molecular Weight"])
        if self.metadata["Sample Information"]["Concentrations"] != "":
            c += checkLength("\r\n##CONCENTRATIONS=" + self.metadata["Sample Information"]["Concentrations"])
        if self.metadata["Equipment Information"]["Spectrometer"] != "":
            c += checkLength("\r\n##SEPCTROMETER/DATA SYSTEM=" + self.metadata["Equipment Information"]["Spectrometer"])
        if self.metadata["Equipment Information"]["Instrumental Parameters"] != "":
            c += checkLength("\r\n##INSTRUMENTAL PARAMETERS=" + self.metadata["Equipment Information"]["Instrumental Parameters"])
        if self.metadata["Sampling Information"]["Sampling Procedure"] != "":
            c += checkLength("\r\n##SAMPLING PROCEDURE=" + self.metadata["Sampling Information"]["Sampling Procedure"])
        if self.metadata["Sampling Information"]["State"] != "":
            c += checkLength("\r\n##STATE=" + self.metadata["Sampling Information"]["State"])
        if self.metadata["Sampling Information"]["Path Length"] != "":
            c += checkLength("\r\n##PATH LENGTH=" + self.metadata["Sampling Information"]["Path Length"])
        if self.metadata["Sampling Information"]["Pressure"] != "":
            c += checkLength("\r\n##PRESSURE=" + self.metadata["Sampling Information"]["Pressure"])
        if self.metadata["Sampling Information"]["Temperature"] != "":
            c += checkLength("\r\n##TEMPERATURE=" + self.metadata["Sampling Information"]["Temperature"])
        if self.metadata["Sampling Information"]["Data Processing"] != "":
            c += checkLength("\r\n##DATA PROCESSING=" + self.metadata["Sampling Information"]["Data Processing"])
        if self.metadata["Comments"] != "":
            c += checkLength("\r\n##=" + self.metadata["Comments"])
        c += checkLength("\r\n##XYDATA=(XY)")
        for i in range(len(self.x)):
            c += "\r\n" + str(round(self.x[i], 6)) + " " + str(round(self.y[i], 6))
        c += checkLength("\r\n##END= $$" + self.metadata["Core Data"]["Title"] + "\r\n")
        
        return c
    
    def getDisplayData(self):
        data = {}
        data["Title"] = self.title
        data["Color"] = self.color
        data["Line Style"] = self.lineStyle
        data["Marker Style"] = self.markerStyle
        return data
    
    def setDisplayData(self, data):
        self.title = data["Title"]
        self.metadata["Core Data"]["Title"] = data["Title"]
        self.color = data["Color"]
        self.lineStyle = data["Line Style"]
        self.markerStyle = data["Marker Style"]
    
    def peakpicking(self, height=None, threshold=None, distance=None, prominence=None, width=None):
        self.peaks, _ = find_peaks(self.y, height, threshold, distance, prominence, width)
        self.peakString = ""
        peaksY = self.y[self.peaks]
        peaksX = self.x[self.peaks]
        maxY = np.max(self.y)
        peakStringList = []
        for i in range(len(self.peaks)):
            h = peaksY[i] * 100 / maxY
            if h >= 80:
                relHeight = "vs"
            elif h >= 60:
                relHeight = "s"
            elif h >= 40:
                relHeight = "m"
            elif h >= 20:
                relHeight = "w"
            elif h < 20:
                relHeight = "vw"
            peakStringList.append(str(round(peaksX[i], 1)) + " (" + relHeight + ")")
        self.peakString = ", ".join(peakStringList)
        return self.peakString

def getJCAMPblockFromFile(fileName):
    blocks = []
    tmpBlocks = [""]
    with open(fileName) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("##TITLE="):
                if "##TITLE=" in tmpBlocks[-1]:
                    tmpBlocks.append("")
            tmpBlocks[-1] += line
            if line.startswith("##END="):
                blocks.append(tmpBlocks.pop())
    
    return blocks

def loadJCAMPlinkBlock(s):
    res = {}
    ldr = re.compile("##([\$\w\s/-]*)=(.*)$", re.IGNORECASE)
    lines = s.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("##"):
            # It is an Labeled Data Record (LDR), which stops at the next LDR!
            m = ldr.match(line)
            if m:
                label = m.group(1).upper()
                data = m.group(2).strip()
                if label != "END":
                    while not lines[i+1].startswith("##"):
                        data += "\r\n" + lines[i+1].strip()
                        i += 1
                if label =="TITLE":
                    res['Title'] = data
                elif label == "BLOCKS":
                    res['Blocks'] = int(data)
                elif label == "$PAGES":
                    res['Pages'] = int(data)
                elif label == "SAMPLE DESCRIPTION":
                    res["Sample Description"] = data
                elif label == "END":
                    break
        i += 1
    return res

def checkLength(s):
    if len(s) < 80:
        return s
    lines = s.splitlines()
    print(lines)
    if len(lines) > 1:
        r = ""
        for l in lines:
            r += checkLength(l) + "\r\n"
    else:
        line = 0
        s = s.replace("\r\n", "")
        r = "\r\n" + s[78 * line: 78*line + 78] + "\r\n"
        while 78 * line < len(s):
            line += 1
            if 78*line + 78 > len(s):
                r += s[78*line:]
            else:
                r += s[78 * line: 78*line + 78] + "\r\n"
    return r.rstrip()
