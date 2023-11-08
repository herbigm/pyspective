#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 13:42:51 2023

@author: marcus
"""

import json

from spectrum import checkLength

class spectiveDocument:
    def __init__(self, title = ""):
        self.pages = []
        self.currentPage = None
        self.fileName = None
        self.title = title
        
    def addPage(self):
        self.pages.append(spectivePage())
        self.pages[-1].title = "Page " + str(len(self.pages))
        self.currentPage = self.pages[-1]
        return self.currentPage
    
    def goToPage(self, index):
        self.currentPage = self.pages[index]
        return self.currentPage
    
    def deletePage(self, row):
        deletedPage = self.pages.pop(row)
        if len(self.pages) == 0: # no page left, return 0
            return None
        if deletedPage == self.currentPage and row == 0: # first page was deleted, make the new first page the currentPage
            self.currentPage = self.pages[0]
        elif deletedPage == self.currentPage and row > 0: # a middle page was deleted, make the previous page the currentPage
            self.currentPage = self.pages[row - 1]
        return self.currentPage # return the current page as pointer
        
        
    def saveDocument(self, fileName = None):
        if not fileName:
            fileName = self.fileName
        if fileName:
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
                            c += "\r\n##$PAGE TITLE=" + self.pages[p].figureData['PageTitle']
                            c += "\r\n##$PLOT TITLE=" + self.pages[p].figureData['PageTitle']
                            c += "\r\n##$XLABEL=" + s.xlabel
                            c += "\r\n##$YLABEL=" + s.ylabel
                            c += "\r\n##$XLIM=" + json.dumps(self.pages[p].plotWidget.ax.get_xlim())
                            c += "\r\n##$YLIM=" + json.dumps(self.pages[p].plotWidget.ax.get_ylim())
                            c += "\r\n##$LEGEND=" + self.pages[p].plotWidget.legend
                            pageInfoSet = True
                        f.write(s.getAsJCAMPDX(c))
                f.write("\r\n")
                f.write(checkLength("\r\n##END= $$" + self.title))
        
    def saveSpectrum(self, spectrumIndex, fileName):
        if fileName:
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            with open(fileName, "w") as f:
                f.write(self.currentPage.currentSpectrum.getAsJCAMPDX())
    
    def savePage(self, fileName):
        if fileName:
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            with open(fileName, "w") as f:
                page = self.currentPage
                if page.title=="":
                    page.title = "untitled"
                f.write(checkLength("##TITLE=" + page.figureData['PageTitle']))
                f.write(checkLength("\r\n##JCAMP-DX=5.01"))
                f.write(checkLength("\r\n##DATA TYPE=LINK"))
                f.write(checkLength("\r\n##BLOCKS=" + str(len(page.spectra) + 1)))
                f.write(checkLength("\r\n##SAMPLE DESCRIPTION="))
                f.write("\r\n")
                for s in page.spectra:
                    f.write("\r\n")
                    f.write(s.getAsJCAMPDX())
                f.write("\r\n")
                f.write(checkLength("\r\n##END= $$" + page.figureData['PageTitle']))
        
    def getFigureData(self):
        return self.currentPage.getFigureData()
    
    def setFigureData(self, data):
        self.currentPage.setFigureData(data)     
    
    def getCurrentPageIndex(self):
        return self.pages.index(self.currentPage)

        

class spectivePage:
    def __init__(self):
        self.spectra = []
        self.figureData = {}
        self.figureData['PageTitle'] = ""
        self.figureData['PlotTitle'] = ""
        self.figureData['XLabel'] = ""
        self.figureData['YLabel'] = ""
        self.figureData['XUnit'] = ""
        self.figureData['YUnit'] = ""
        self.figureData['XLim'] = [0,0]
        self.figureData['YLim'] = [0,0]
        self.figureData['Legend'] = ""
        self.figureData['fullXLim'] = [0,0]
        self.figureData['fullYLim'] = [0,0]
        self.icon = None
        self.currentSpectrum = None
        
    def _calculateFullLim(self):
        # reset xlim and ylim
        self.figureData['fullXLim'] = [0,0]
        self.figureData['fullYLim'] = [0,0]
        for spectrum in self.spectra:
            if spectrum == self.spectra[0]:
                # for the first spectrum on this page
                self.figureData['fullXLim'] = spectrum.xlim.copy()
                self.figureData['fullYLim'] = spectrum.ylim.copy()
            else:
                # update xlim if necessary
                if self.figureData['fullXLim'][0] > self.figureData['fullXLim'][1]:
                    if spectrum.xlim[0] < spectrum.xlim[1]: # Spectrum has not the same x-axis orientation as the plot! -> flip it!
                        spectrum.x = spectrum.x.flip()
                        spectrum.y = spectrum.y.flip()
                        spectrum.xlim = spectrum.xlim.flip()
                    if self.figureData['fullXLim'][0] < spectrum.xlim[0]:
                        self.figureData['fullXLim'][0] = spectrum.xlim[0]
                    if self.figureData['fullXLim'][1] > spectrum.xlim[1]:
                        self.figureData['fullXLim'][1] = spectrum.xlim[1]
                else:
                    if spectrum.xlim[0] > spectrum.xlim[1]: # Spectrum has not the same x-axis orientation as the plot! -> flip it!
                        spectrum.x = spectrum.x.flip()
                        spectrum.y = spectrum.y.flip()
                        spectrum.xlim = spectrum.xlim.flip()
                    if self.figureData['fullXLim'][0] > spectrum.xlim[0]:
                        self.figureData['fullXLim'][0] = spectrum.xlim[0]
                    if self.figureData['fullXLim'][1] < spectrum.xlim[1]:
                        self.figureData['fullXLim'][1] = spectrum.xlim[1]
                # update ylim if necessary
                if self.figureData['fullYLim'][0] > self.figureData['fullYLim'][1]:
                    if spectrum.ylim[0] < spectrum.ylim[1]: # Spectrum has not the same x-axis orientation as the plot! -> flip it!
                        spectrum.x = spectrum.x.flip()
                        spectrum.y = spectrum.y.flip()
                        spectrum.xlim = spectrum.xlim.flip()
                    if self.figureData['fullYLim'][0] < spectrum.ylim[0]:
                        self.figureData['fullYLim'][0] = spectrum.ylim[0]
                    if self.figureData['fullYLim'][1] > spectrum.ylim[1]:
                        self.figureData['fullYLim'][1] = spectrum.ylim[1]
                else:
                    if spectrum.ylim[0] > spectrum.ylim[1]: # Spectrum has not the same x-axis orientation as the plot! -> flip it!
                        spectrum.x = spectrum.x.flip()
                        spectrum.y = spectrum.y.flip()
                        spectrum.xlim = spectrum.xlim.flip()
                    if self.figureData['fullYLim'][0] > spectrum.ylim[0]:
                        self.figureData['fullYLim'][0] = spectrum.ylim[0]
                    if self.figureData['fullYLim'][1] < spectrum.ylim[1]:
                        self.figureData['fullYLim'][1] = spectrum.ylim[1]
        
    def addSpectrum(self, spectrum):
        self.spectra.append(spectrum)
        self._calculateFullLim()
        if len(self.spectra) == 1:
            # only for the first spectrum
            self.figureData['XLim'] = self.figureData['fullXLim'].copy()
            self.figureData['YLim'] = self.figureData['fullYLim'].copy()
        if spectrum.displayData['Plot Title'] != "":
            self.figureData['PlotTitle'] = spectrum.displayData['Plot Title']
        if spectrum.displayData['Page Title'] != "":
            self.figureData['PageTitle'] = spectrum.displayData['Page Title']
        if spectrum.xlabel != "":
            self.figureData['XLabel'] = spectrum.xlabel
        else:
            self.figureData['XLabel'] = spectrum.metadata["Spectral Parameters"]["X Units"]
        if spectrum.ylabel != "":
            self.figureData['YLabel'] = spectrum.ylabel
        else:
            self.figureData['YLabel'] = spectrum.metadata["Spectral Parameters"]["Y Units"]
        if spectrum.displayData['xlim']:
            self.figureData['XLim'] = spectrum.displayData['xlim'].copy()
        if spectrum.displayData['ylim']:
            self.figureData['YLim'] = spectrum.displayData['ylim'].copy()
        if spectrum.displayData['Legend']:
            self.figureData['Legend'] = spectrum.displayData['Legend']
        if spectrum.metadata["Spectral Parameters"]["X Units"] and self.figureData['XUnit'] == "":
            self.figureData['XUnit'] = spectrum.metadata["Spectral Parameters"]["X Units"]
        if spectrum.metadata["Spectral Parameters"]["Y Units"] and self.figureData['YUnit'] == "":
            self.figureData['YUnit'] = spectrum.metadata["Spectral Parameters"]["Y Units"]
        self.currentSpectrum = self.spectra[-1]
        return self.currentSpectrum
    
    def spectrumDown(self, row):
        self.spectra[row], self.spectra[row + 1] = self.spectra[row + 1], self.spectra[row]
        return self.spectra[row+1]
    
    def spectrumUp(self, row):
        self.spectra[row], self.spectra[row - 1] = self.spectra[row - 1], self.spectra[row]
        return self.spectra[row-1]
    
    def deleteSpectrum(self, row):
        deletedSpectrum = self.spectra.pop(row)
        self._calculateFullLim()
        if len(self.spectra) == 0:
            return 0
        if deletedSpectrum == self.currentSpectrum and row == 0:
            self.currentSpectrum = self.spectra[0]
        elif deletedSpectrum == self.currentSpectrum and row > 0:
            self.currentSpectrum = self.spectra[row - 1]
        return self.currentSpectrum
    
    def setCurrentSpectrum(self, index):
        self.currentSpectrum = self.spectra[index]
        return self.currentSpectrum
    
    def doIntegration(self, x1, x2):
        self.currentSpectrum.integrate(x1, x2)
    
    def getCurrentSpectrumIndex(self):
        return self.spectra.index(self.currentSpectrum)
    
    def setFigureData(self, data):
        if data['invertX']:
            for s in self.spectra:
                s.x = s.x.flip()
                s.y = s.y.flip()
                s.peaks = len(s.x) - s.peaks - 1
        self.figureData['XLabel'] = data["XLabel"]
        self.figureData['YLabel'] = data["YLabel"]
        self.figureData['XUnit'] = data["XUnit"]
        self.figureData['YUnit'] = data["YUnit"]
        self.figureData['XLim'] = data["XLim"]
        self.figureData['YLim'] = data["YLim"]
        self.figureData['PlotTitle'] = data["PlotTitle"]
        self.figureData['PageTitle'] = data["PageTitle"]
        self.figureData['Legend'] = data['Legend']
