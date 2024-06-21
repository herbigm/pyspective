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
        # currently reads only the last diffractogram (last range)
        varInfo = {}
        hwInfo = {}
        
        fp = open(fileName, "rb")
        fileSize = os.path.getsize(fileName)

        fp.seek(0)

        bruker_version = str(fp.read(7).decode("iso-8859-1"))

        fp.seek(12)
        bruker_date = str(fp.read(12).decode("iso-8859-1")).strip('\x00')

        fp.seek(24)
        bruker_time = str(fp.read(12).decode("iso-8859-1")).strip('\x00')

        bruker_datetime = datetime.datetime.strptime(bruker_date + "H" + bruker_time, "%m/%d/%YH%H:%M:%S")
        
        fp.seek(40)
        iNoOfRanges = struct.unpack('i', fp.read(4))[0]
        fp.seek(44)
        iNoOfMeasuredRanges = struct.unpack('i', fp.read(4))[0]
        fp.seek(56)
        iExtraRecordSize = struct.unpack('i', fp.read(4))[0]
        fp.seek(60)
        szFurther_dql_reading = int.from_bytes(struct.unpack('c', fp.read(1))[0], 'big')
        if szFurther_dql_reading != 0:
            fp.seek(61)
            pos = struct.unpack('i', fp.read(4))[0]
            pos += 61
        else:
            pos = 61
        while pos < 61 + iExtraRecordSize:
            if pos >= fileSize - 8:
                break
            fp.seek(pos)
            iRecordType = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+4)
            iRecordLength = struct.unpack('i', fp.read(4))[0]
            
            if iRecordType == 10:
                fp.seek(pos+8)
                iFlags = struct.unpack('i', fp.read(4))[0]
                fp.seek(pos+12)
                szType = str(fp.read(12).decode("iso-8859-1")).strip('\x00')
                if iFlags == 0:
                    fp.seek(pos+36)
                    sz = str(fp.read(iRecordLength - 36).decode("iso-8859-1")).strip('\x00')
                    varInfo[szType] = sz
            elif iRecordType == 30:
                fp.seek(pos+8)
                iGoniomModel = struct.unpack('i', fp.read(4))[0]
                flagsGoniomModel = [False for x in range(32)]
                
                lGoniomModel = []
                for b in range(32):
                    flagsGoniomModel[b] = bool(0 != (iGoniomModel & (1 << b)))
                if flagsGoniomModel[0]:
                    lGoniomModel.append("D5000_TYPE");
                if flagsGoniomModel[1]:
                    lGoniomModel.append("D5005_TYPE");
                if flagsGoniomModel[2]:
                    lGoniomModel.append("D8_TYPE");
                if flagsGoniomModel[3]:
                    lGoniomModel.append("D500_TYPE");
                if flagsGoniomModel[4]:
                    lGoniomModel.append("OTHER_TYPE");
                if flagsGoniomModel[5]:
                    lGoniomModel.append("D4_TYPE");
                if flagsGoniomModel[8]:
                    lGoniomModel.append("THETA_2THETA");
                if flagsGoniomModel[9]:
                    lGoniomModel.append("THETA_THETA");
                if flagsGoniomModel[10]:
                    lGoniomModel.append("ALPHA_THETA");
                if flagsGoniomModel[11]:
                    lGoniomModel.append("MATIC");
                if flagsGoniomModel[16]:
                    lGoniomModel.append("GADDS");
                if flagsGoniomModel[17]:
                    lGoniomModel.append("SAXS");
                if flagsGoniomModel[18]:
                    lGoniomModel.append("SMART");
                if flagsGoniomModel[19]:
                    lGoniomModel.append("OTHER_SYSTEM");
                hwInfo['iGoniomModel'] = lGoniomModel
                
                fp.seek(pos+12)
                iGoniomStage = struct.unpack('i', fp.read(4))[0]
                if iGoniomStage == 0:
                    hwInfo['iGoniomStage'] = "STANDARD_STAGE"
                elif iGoniomStage == 1:
                    hwInfo['iGoniomStage'] = "SYNCHR_ROT"
                elif iGoniomStage == 2:
                    hwInfo['iGoniomStage'] = "ROT_REFLECTION"
                elif iGoniomStage == 3:
                    hwInfo['iGoniomStage'] = "ROT_TRANSMISSION"
                elif iGoniomStage == 4:
                    hwInfo['iGoniomStage'] = "OPEN_CRADLE"
                elif iGoniomStage == 5:
                    hwInfo['iGoniomStage'] = "CLOSED_CRADLE"
                elif iGoniomStage == 6:
                    hwInfo['iGoniomStage'] = "QUARTER_CRADLE"
                elif iGoniomStage == 7:
                    hwInfo['iGoniomStage'] = "PHI_STAGE"
                elif iGoniomStage == 8:
                    hwInfo['iGoniomStage'] = "CHI_STAGE"
                elif iGoniomStage == 9:
                    hwInfo['iGoniomStage'] = "XYZ_STAGE"
                elif iGoniomStage == 10:
                    hwInfo['iGoniomStage'] = "LOW_TEMP"
                elif iGoniomStage == 11:
                    hwInfo['iGoniomStage'] = "HIGH_TEMP"
                elif iGoniomStage == 12:
                    hwInfo['iGoniomStage'] = "EXTERNAL_TEMP"
                elif iGoniomStage == 13:
                    hwInfo['iGoniomStage'] = "PHI_AT_FIXED_CHI"
                elif iGoniomStage == 14:
                    hwInfo['iGoniomStage'] = "FOUR_CYCLE"
                elif iGoniomStage == 15:
                    hwInfo['iGoniomStage'] = "SMALL_XYZ_STAGE"
                elif iGoniomStage == 16:
                    hwInfo['iGoniomStage'] = "LARGE_XYZ_STAGE"
                elif iGoniomStage == 17:
                    hwInfo['iGoniomStage'] = "UNKNOWN"
                    
                fp.seek(pos + 16)
                iSampleChanger= struct.unpack('i', fp.read(4))[0]
                if iSampleChanger == 0:
                    hwInfo['iSampleChanger'] = "NONE"
                elif iSampleChanger == 1:
                    hwInfo['iSampleChanger'] = "FOURTY_POSITION"
                elif iSampleChanger == 2:
                    hwInfo['iSampleChanger'] = "Y_MATIC"
                elif iSampleChanger == 3:
                    hwInfo['iSampleChanger'] = "XY_MATIC"
                elif iSampleChanger == 4:
                    hwInfo['iSampleChanger'] = "MANUAL"
                elif iSampleChanger == 5:
                    hwInfo['iSampleChanger'] = "UNKNOWN"
                
                fp.seek(pos+20)
                iGoniomCtrl = struct.unpack('i', fp.read(4))[0]
                flagsGoniomCtrl = [False for x in range(32)]
                
                lGoniomCtrl = []
                for b in range(32):
                    flagsGoniomCtrl[b] = bool(0 != (iGoniomCtrl & (1 << b)))
                if flagsGoniomCtrl[0]:
                    lGoniomCtrl.append("DIFF_CONT");
                if flagsGoniomCtrl[1]:
                    lGoniomCtrl.append("TC_SOC");
                if flagsGoniomCtrl[2]:
                    lGoniomCtrl.append("FDC_SOC");
                if flagsGoniomCtrl[3]:
                    lGoniomCtrl.append("TC_OTHER");
                if flagsGoniomCtrl[4]:
                    lGoniomCtrl.append("FDC_OTHER");
                if flagsGoniomCtrl[5]:
                    lGoniomCtrl.append("GGCS");
                if flagsGoniomCtrl[8]:
                    lGoniomCtrl.append("UNKNOWN");
                hwInfo['iGoniomCtrl'] = lGoniomCtrl
                
                fp.seek(pos+24)
                hwInfo['fGoniomDiameter'] = struct.unpack('f', fp.read(4))[0]
                
                fp.seek(pos+28)
                iSyncAxis = struct.unpack('i', fp.read(4))[0]
                if iSyncAxis == 0:
                    hwInfo['iSyncAxis'] = "NONE"
                elif iSyncAxis == 1:
                    hwInfo['iSyncAxis'] = "REFLECTION_PHI"
                elif iSyncAxis == 2:
                    hwInfo['iSyncAxis'] = "TRANSMISSION_PHI"
                elif iSyncAxis == 3:
                    hwInfo['iSyncAxis'] = "X_CLOSED_CRADLE"
                
                fp.seek(pos+32)
                iBeamOpticsFlags = struct.unpack('i', fp.read(4))[0]
                flagsBeamOpticsFlags = [False for x in range(32)]
                
                lBeamOpticsFlags = []
                for b in range(32):
                    flagsBeamOpticsFlags[b] = bool(0 != (iBeamOpticsFlags & (1 << b)))
                if flagsBeamOpticsFlags[0]:
                    lBeamOpticsFlags.append("DIVSLIT_SET");
                if flagsBeamOpticsFlags[1]:
                    lBeamOpticsFlags.append("NEAR_SAMPLE_SLIT_SET");
                if flagsBeamOpticsFlags[2]:
                    lBeamOpticsFlags.append("PRIM_SOLLER_SLIT_SET");
                if flagsBeamOpticsFlags[3]:
                    lBeamOpticsFlags.append("ANTISC_SLIT_SET");
                if flagsBeamOpticsFlags[4]:
                    lBeamOpticsFlags.append("DET_SLIT_SET");
                if flagsBeamOpticsFlags[5]:
                    lBeamOpticsFlags.append("SEC_SOLLER_SLIT_SET");
                if flagsBeamOpticsFlags[6]:
                    lBeamOpticsFlags.append("THINFILM_ATT_SET");
                if flagsBeamOpticsFlags[7]:
                    lBeamOpticsFlags.append("BETA_FILTER_SET");
                if flagsBeamOpticsFlags[8]:
                    lBeamOpticsFlags.append("MOT_SLIT_CHANGER_SET");
                if flagsBeamOpticsFlags[9]:
                    lBeamOpticsFlags.append("MOT_ABS_CHANGER_SET");
                if flagsBeamOpticsFlags[10]:
                    lBeamOpticsFlags.append("MOT_ROTARY_ABSORBER_SET");
                hwInfo['iBeamOpticsFlags'] = lBeamOpticsFlags
                
                fp.seek(pos+36)
                hwInfo['fDivSlit'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+40)
                hwInfo['fNearSampleSlit'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+44)
                hwInfo['fPrimSollerSlit'] = struct.unpack('f', fp.read(4))[0]
                
                fp.seek(pos+48)
                iMonochromator = struct.unpack('i', fp.read(4))[0]
                if iMonochromator == 0:
                    hwInfo['iMonochromator'] = "NONE"
                elif iMonochromator == 1:
                    hwInfo['iMonochromator'] = "TRANSMISSION_MONO"
                elif iMonochromator == 2:
                    hwInfo['iMonochromator'] = "REFLECTION_MONO"
                elif iMonochromator == 3:
                    hwInfo['iMonochromator'] = "GE220_2_BOUNCE"
                elif iMonochromator == 4:
                    hwInfo['iMonochromator'] = "GE220_4_BOUNCE"
                elif iMonochromator == 5:
                    hwInfo['iMonochromator'] = "GE440_4_BOUNCE"
                elif iMonochromator == 6:
                    hwInfo['iMonochromator'] = "FLAT_GRAPHITE_MONO"
                elif iMonochromator == 7:
                    hwInfo['iMonochromator'] = "SINGLE_GOEBEL_MIRROR"
                elif iMonochromator == 8:
                    hwInfo['iMonochromator'] = "CROSSED_GOEBEL_MIRROR"
                elif iMonochromator == 9:
                    hwInfo['iMonochromator'] = "FLAT_GERMANIUM_111"
                elif iMonochromator == 10:
                    hwInfo['iMonochromator'] = "FLAT_SILICON_111"
                elif iMonochromator == 11:
                    hwInfo['iMonochromator'] = "GE_REFLECTION"
                elif iMonochromator == 12:
                    hwInfo['iMonochromator'] = "ASYM_GE_4_BOUNCE"
                elif iMonochromator == 13:
                    hwInfo['iMonochromator'] = "UNKNOWN"
                
                fp.seek(pos+52)
                hwInfo['fAntiScSlit'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+56)
                hwInfo['fDetSlit'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+60)
                hwInfo['fSecondSollerSlit'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+64)
                hwInfo['fThinFilmAtt'] = struct.unpack('f', fp.read(4))[0]
                
                fp.seek(pos+68)
                iAnalyzer = struct.unpack('i', fp.read(4))[0]
                if iAnalyzer == 0:
                    hwInfo['iAnalyzer'] = "NONE"
                elif iAnalyzer == 1:
                    hwInfo['iAnalyzer'] = "GRAPHITE_ANALYZER"
                elif iAnalyzer == 2:
                    hwInfo['iAnalyzer'] = "LIF_ANALYZER"
                elif iAnalyzer == 3:
                    hwInfo['iAnalyzer'] = "GE220_CHANNEL_CUT"
                elif iAnalyzer == 4:
                    hwInfo['iAnalyzer'] = "GOEBEL_MIRROR_ANALYZER"
                elif iAnalyzer == 5:
                    hwInfo['iAnalyzer'] = "UNKNOWN"
                    
                fp.seek(pos+72)
                hwInfo['fAlphaAverage'] = struct.unpack('d', fp.read(8))[0]
                fp.seek(pos+80)
                hwInfo['fAlpha1'] = struct.unpack('d', fp.read(8))[0]
                fp.seek(pos+88)
                hwInfo['fAlpha2'] = struct.unpack('d', fp.read(8))[0]
                fp.seek(pos+96)
                hwInfo['fBeta'] = struct.unpack('d', fp.read(8))[0]
                fp.seek(pos+104)
                hwInfo['fAlphaRatio'] = struct.unpack('d', fp.read(8))[0]
                fp.seek(pos+112)
                hwInfo['fBetaRelInt'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+116)
                hwInfo['szAnode'] = str(fp.read(4).decode("iso-8859-1")).strip('\x00')
                fp.seek(pos+120)
                hwInfo['szWaveUnit'] = str(fp.read(4).decode("iso-8859-1")).strip('\x00')
                fp.seek(pos+124)
                hwInfo['fActivateAbsorber'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+128)
                hwInfo['fDeactivateAbsorber'] = struct.unpack('f', fp.read(4))[0]
                fp.seek(pos+132)
                hwInfo['fAbsFactor'] = struct.unpack('f', fp.read(4))[0]
                
            pos += iRecordLength
        
        if iNoOfRanges > iNoOfMeasuredRanges:
            NumberOfRanges = iNoOfMeasuredRanges
        else:
            NumberOfRanges = iNoOfRanges
        
        for r in range(NumberOfRanges):
            if pos + 160 >= fileSize:
                break
            rangeHeader = {}
            fp.seek(pos)
            rangeHeader['iDataLength'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos + 4)
            rangeHeader['iNoOfMeasuredData'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos + 8)
            rangeHeader['iNoOfCompletedData'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos + 12)
            rangeHeader['iNoOfConfDrives'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos + 16)
            iMotSlitChangerIn = struct.unpack('i', fp.read(4))[0]
            if iMotSlitChangerIn == 0:
                rangeHeader['iMotSlitChangerIn'] = "MOT_CHANGER_OUT"
            elif iMotSlitChangerIn == 1:
                rangeHeader['iMotSlitChangerIn'] = "MOT_CHANGER_IN"
            elif iMotSlitChangerIn == 2:
                rangeHeader['iMotSlitChangerIn'] = "MOT_CHANGER_AUTO"
            fp.seek(pos + 20)
            rangeHeader['iNoOfDetectors'] = struct.unpack('i', fp.read(4))[0]
            
            fp.seek(pos + 24)
            iAdditionalDetectorFlags = struct.unpack('i', fp.read(4))[0]
            flagsAdditionalDetectorFlags = [False for x in range(32)]
            
            lAdditionalDetectorFlags = []
            for b in range(32):
                flagsAdditionalDetectorFlags[b] = bool(0 != (iAdditionalDetectorFlags & (1 << b)))
            if flagsAdditionalDetectorFlags[0]:
                lAdditionalDetectorFlags.append("PSD_SET")
            if flagsAdditionalDetectorFlags[1]:
                lAdditionalDetectorFlags.append("AD_SET")
            if flagsAdditionalDetectorFlags[2]:
                lAdditionalDetectorFlags.append("PSD_MEASURED")
            if flagsAdditionalDetectorFlags[3]:
                lAdditionalDetectorFlags.append("AD_MEASURED")
            if flagsAdditionalDetectorFlags[4]:
                lAdditionalDetectorFlags.append("PSD_SAVED")
            if flagsAdditionalDetectorFlags[5]:
                lAdditionalDetectorFlags.append("AD_SAVED")
            if flagsAdditionalDetectorFlags[6]:
                lAdditionalDetectorFlags.append("NONE")
            rangeHeader['iAdditionalDetectorFlags'] = lAdditionalDetectorFlags
            
            fp.seek(pos + 28)
            iScanMode = struct.unpack('i', fp.read(4))[0]
            if iScanMode == 0:
                rangeHeader['iScanMode'] = "STEPSCAN"
            elif iScanMode == 1:
                rangeHeader['iScanMode'] = "CONTINUOUSSCAN"
            elif iScanMode == 2:
                rangeHeader['iScanMode'] = "CONTINUOUSSTEPSCAN"
            
            fp.seek(pos+32)
            rangeHeader['szScanType'] = str(fp.read(24).decode("iso-8859-1")).strip('\x00')
            fp.seek(pos+56)
            rangeHeader['iSynchRotation'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+60)
            rangeHeader['fMeasDelayTime'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+64)
            rangeHeader['iEstScanTime'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+68)
            rangeHeader['fRangeSampleStarted'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+72)
            rangeHeader['fStart'] = struct.unpack('d', fp.read(8))[0]
            fp.seek(pos+80)
            rangeHeader['fIncrement'] = struct.unpack('d', fp.read(8))[0]
            fp.seek(pos+88)
            rangeHeader['iSteps'] =  struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+92)
            rangeHeader['fStepTime'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+96)
            rangeHeader['fRotationSpeed'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+100)
            rangeHeader['fGeneratorVoltage'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+104)
            rangeHeader['fGeneratorCurrent'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+108)
            rangeHeader['iDisplayPlaneNumber'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+112)
            rangeHeader['fActUsedLambda'] = struct.unpack('d', fp.read(8))[0]
            fp.seek(pos+120)
            rangeHeader['iNoOfVaryingParams'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+124)
            rangeHeader['iNoCounts'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+128)
            rangeHeader['iNoEncoderDrives'] = struct.unpack('i', fp.read(4))[0]
            
            fp.seek(pos+132)
            iExtraParamFlags = struct.unpack('i', fp.read(4))[0]
            flagsExtraParamFlags = [False for x in range(32)]
            
            lAdditionalDetectorFlags = []
            for b in range(32):
                flagsExtraParamFlags[b] = bool(0 != (iExtraParamFlags & (1 << b)))
            lExtraParamFlags = []
            if flagsExtraParamFlags[0]:
                lExtraParamFlags.append("VARIABLE_TIME_PER_STEP")
            rangeHeader['iExtraParamFlags'] = lExtraParamFlags
            
            fp.seek(pos+136)
            rangeHeader['iDataRecordLength'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+140)
            rangeHeader['iExtraRecordSize'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+144)
            rangeHeader['fSmoothingWidth'] = struct.unpack('f', fp.read(4))[0]
            fp.seek(pos+148)
            rangeHeader['iSimMeasCond'] = struct.unpack('i', fp.read(4))[0]
            fp.seek(pos+152)
            rangeHeader['fIncrement_3'] = struct.unpack('d', fp.read(8))[0]
            
            pos += 160 + rangeHeader['iExtraRecordSize']
            
            start = rangeHeader['fStart']
            steps = rangeHeader['iSteps']
            increment = rangeHeader['fIncrement']
            end = start + steps * increment
            stepTime = rangeHeader['fStepTime']
            iNoCounts = rangeHeader['iNoCounts']

            x = []
            y = []
            for j in range(steps):
                for k in range(iNoCounts):
                    fp.seek(pos)
                    x.append(start + (j/(steps - 1)) * (end - start))
                    y.append(struct.unpack('f', fp.read(4))[0] / stepTime)
                    pos += 4
        
        self.x = np.array(x)
        self.y = np.array(y)
        self.metadata["Notes"]["Date Time"] = bruker_datetime
        self.metadata["Comments"] += "Bruker Version: " + bruker_version
        self.metadata["Comments"] += "\n\n" + json.dumps(rangeHeader, indent=2)
        self.metadata["Comments"] += "\n\n" + json.dumps(hwInfo, indent=2)
        self.metadata["Comments"] += "\n\n" + json.dumps(varInfo, indent=2)
        self.metadata["Core Data"]["Title"] = os.path.basename(fileName)
        self.title = os.path.basename(fileName)
        self.xlim = [min(self.x), max(self.x)]
        self.ylim = [min(self.y), max(self.y)]
        return True