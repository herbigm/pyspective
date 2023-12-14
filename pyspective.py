#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:46:12 2023

@author: marcus
"""

import sys
import os
import re
import copy

import numpy as np

from PyQt6 import QtCore
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QColor, QActionGroup
from PyQt6.QtCore import QDir, Qt, QSize, QSettings
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QToolBar,
    QMenu,
    QFileDialog,
    QDockWidget,
    QListWidget,
    QListWidgetItem,
    QListView,
    QAbstractScrollArea,
    QInputDialog,
    QLineEdit,
    QGridLayout
)

import spectivedocument
import spectrum
import spectratypes
import specplot
import opendialog
import metadatadock
import exportdialog
import pagedialog
import spectiveview
import spectrumdialog
import processdocks

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySpective")
        self.setWindowIcon(QIcon("icons/Logo.svg"))
        self._mainWidget = QTabWidget(self)
        self._mainWidget.currentChanged.connect(self.documentChanged)
        self._mainWidget.tabCloseRequested.connect(self.closeDocument)
        self._mainWidget.setTabsClosable(True)
        self.setCentralWidget(self._mainWidget)
        self.createActions()
        self.createMenuBar()
        self.createMainWidgets()
        
        self.documents = []
        self.currentDocument = None
        self.currentPage = None
        self.currentSpectrum = None
        self.currentMode = "ZoomMode"
        
        # settings
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("windowState"):
            self.restoreState(self.settings.value("windowState"))

        
        # init checkable actions
        self.metadataDockAction.setChecked(not self.metadataDock.isHidden())
        self.pageDockAction.setChecked(not self.pageDock.isHidden())
        self.spectraDockAction.setChecked(not self.spectraDock.isHidden())
    
    def closeEvent(self, evt):
        self.settings.setValue("geometry", QtCore.QVariant(self.saveGeometry()))
        self.settings.setValue("windowState", QtCore.QVariant(self.saveState()))
        super(ApplicationWindow, self).closeEvent(evt)
        self.close()
        
    def createMainWidgets(self):
        # create Toolbar and Statusbar
        self.toolBar = self.addToolBar('Main')
        self.toolBar.setObjectName("MainToolBar")
        self.toolBar.addAction(self.openAction)
        self.toolBar.addAction(self.saveDocumentAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.pageDockAction)
        self.toolBar.addAction(self.spectraDockAction)
        self.toolBar.addAction(self.metadataDockAction)
        self.toolBar.addAction(self.peakpickingDockAction)
        self.toolBar.addAction(self.calculateDerivativeAction)
        self.toolBar.addAction(self.zoomAction)
        self.toolBar.addAction(self.integrationAction)
        self.toolBar.addAction(self.substractionAction)
        
        self.statusBar = self.statusBar()
        
        self.metadataDock = metadatadock.metadataDock(self)
        self.metadataDock.setWindowIcon(QIcon("icons/Metadata.png"))
        self.metadataDock.setObjectName("metaDataDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.metadataDock)
        self.metadataDock.visibilityChanged.connect(lambda show: self.metadataDockAction.setChecked(show))
        self.metadataDock.dataChanged.connect(self.updateMetadata)
        
        self.pageDock = QDockWidget(self.tr("pages"), self)
        self.pageDock.setWindowIcon(QIcon("icons/Pages.png"))
        self.pageDock.setObjectName("Dock of Pages")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pageDock)
        self.pageDock.visibilityChanged.connect(lambda show: self.pageDockAction.setChecked(show))
        self.pageView = spectiveview.pageView()
        self.pageDock.setWidget(self.pageView)
        self.pageView.currentRowChanged.connect(self.pageChanged)
        self.pageView.itemDoubleClicked.connect(self.pageEdit)
        self.pageView.pageUpRequest.connect(self.pageUp)
        self.pageView.pageDownRequest.connect(self.pageDown)
        self.pageView.pageEditRequest.connect(self.pageEdit)
        self.pageView.pageDeleteRequest.connect(self.pageDelete)
        
        self.spectraDock = QDockWidget(self.tr("Spectra"), self)
        self.spectraDock.setWindowIcon(QIcon("icons/Spectra.png"))
        self.spectraDock.setObjectName("spectraDock")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.spectraDock)
        self.spectraDock.visibilityChanged.connect(lambda show: self.spectraDockAction.setChecked(show))
        self.spectraList = spectiveview.spectraView(self)
        self.spectraDock.setWidget(self.spectraList)
        self.spectraList.itemDoubleClicked.connect(self.spectrumEdit)
        self.spectraList.currentRowChanged.connect(self.currentSpectrumChanged)
        self.spectraList.spectrumUpRequest.connect(self.spectrumUp)
        self.spectraList.spectrumDownRequest.connect(self.spectrumDown)
        self.spectraList.spectrumEditRequest.connect(self.spectrumEdit)
        self.spectraList.spectrumDeleteRequest.connect(self.spectrumDelete)
        
        self.peakpickingDock = processdocks.peakpickingDock(self)
        self.peakpickingDock.setWindowIcon(QIcon("icons/Peakpicking.png"))
        self.peakpickingDock.setObjectName("PeakPickingDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.peakpickingDock)
        self.peakpickingDock.visibilityChanged.connect(lambda show: self.peakpickingDockAction.setChecked(show))
        self.peakpickingDock.peaksChanged.connect(self.updatePlot)
        
        self.integralDock = processdocks.integralDock(self)
        self.integralDock.setWindowIcon(QIcon("icons/Integration.png"))
        self.integralDock.setObjectName("IntegralDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.integralDock)
        self.integralDock.visibilityChanged.connect(lambda show: self.integralDockAction.setChecked(show))
        self.integralDock.integralsChanged.connect(self.updatePlot)
        
        self.xrdDock = processdocks.XrdDock(self)
        self.xrdDock.setObjectName("XRD Dock")
        self.xrdDock.referenceChanged.connect(self.updatePlot)
        self.xrdDock.visibilityChanged.connect(lambda show: self.xrdReferenceDockAction.setChecked(show))
        
        self.xrfDock = processdocks.XrfDock(self)
        self.xrfDock.setObjectName("XRF Dock")
        self.xrfDock.referenceChanged.connect(self.updatePlot)
        self.xrfDock.visibilityChanged.connect(lambda show: self.xrfReferenceDockAction.setChecked(show))
        
    def createActions(self):
        self.closeAction = QAction(self.tr('Quit'))
        self.closeAction.setIcon(QIcon.fromTheme("application-exit", QIcon("icons/application-exit.svg")))
        self.closeAction.triggered.connect(self.close)
        
        self.openAction = QAction(self.tr('Open Spectrum'))
        self.openAction.setIcon(QIcon("icons/Open.png"))
        self.openAction.triggered.connect(self.openFile)
        
        self.documentTitleAction = QAction(self.tr("Edit Document Title"))
        self.documentTitleAction.setEnabled(False)
        self.documentTitleAction.triggered.connect(self.setDocumentTitle)
        
        self.savePageAction = QAction(self.tr("Save Current Page"))
        self.savePageAction.setEnabled(False)
        self.savePageAction.triggered.connect(self.savePage)
        
        self.saveSpectrumAction = QAction(self.tr("Save Current Spectrum"))
        self.saveSpectrumAction.setEnabled(False)
        self.saveSpectrumAction.triggered.connect(self.saveSpectrum)
        
        self.saveImageAction = QAction(self.tr('Export Current View to Image File'))
        self.saveImageAction.setIcon(QIcon("icons/Image.png"))
        self.saveImageAction.triggered.connect(self.saveImage)
        self.saveImageAction.setEnabled(False)
        
        self.metadataDockAction = QAction(self.tr('Show and Edit Metadata'))
        self.metadataDockAction.setIcon(QIcon("icons/Metadata.png"))
        self.metadataDockAction.setCheckable(True)
        self.metadataDockAction.triggered.connect(self.showMetadataDock)
        
        self.pageDockAction = QAction(self.tr('Show Page Dock'))
        self.pageDockAction.setIcon(QIcon("icons/Pages.png"))
        self.pageDockAction.setCheckable(True)
        self.pageDockAction.triggered.connect(self.showPageDock)
        
        self.spectraDockAction = QAction(self.tr('Show Spectra Dock'))
        self.spectraDockAction.setIcon(QIcon("icons/Spectra.png"))
        self.spectraDockAction.setCheckable(True)
        self.spectraDockAction.triggered.connect(self.showSpectraDock)
        
        self.peakpickingDockAction = QAction(self.tr('Show Peakpicking Dock'))
        self.peakpickingDockAction.setIcon(QIcon("icons/Peakpicking.png"))
        self.peakpickingDockAction.setCheckable(True)
        self.peakpickingDockAction.triggered.connect(self.showPeakpickingDock)
        
        self.integralDockAction = QAction(self.tr('Show Integrals Dock'))
        self.integralDockAction.setIcon(QIcon("icons/Integration.png"))
        self.integralDockAction.setCheckable(True)
        self.integralDockAction.triggered.connect(self.showIntegralDock)
        
        self.xrdReferenceDockAction = QAction(self.tr('Show XRD reference Dock'))
        self.xrdReferenceDockAction.setCheckable(True)
        self.xrdReferenceDockAction.triggered.connect(self.showXrdReferenceDock)
        
        self.xrfReferenceDockAction = QAction(self.tr('Show XRF reference Dock'))
        self.xrfReferenceDockAction.setCheckable(True)
        self.xrfReferenceDockAction.triggered.connect(self.showXrfReferenceDock)
        
        self.pageEditAction = QAction(self.tr('Edit Page'))
        self.pageEditAction.setIcon(QIcon("icons/Edit.png"))
        self.pageEditAction.triggered.connect(self.pageEdit)
        self.pageEditAction.setEnabled(False)
        
        self.zoomAction = QAction(self.tr('Zoom Mode'))
        self.zoomAction.setIcon(QIcon("icons/Zoom.png"))
        self.zoomAction.setCheckable(True)
        self.zoomAction.setChecked(True)
        self.integrationAction = QAction(self.tr('Integration Mode'))
        self.integrationAction.setIcon(QIcon("icons/Integration.png"))
        self.integrationAction.setCheckable(True)
        
        self.modeActionGroup = QActionGroup(self)
        self.modeActionGroup.triggered.connect(self.changeMode)
        self.modeActionGroup.addAction(self.zoomAction)
        self.modeActionGroup.addAction(self.integrationAction)
        
        self.saveDocumentAction = QAction(self.tr('&Save Document as JCAMP-DX'))
        self.saveDocumentAction.setIcon(QIcon("icons/Save.png"))
        self.saveDocumentAction.setShortcut(QKeySequence("Ctrl+S"))
        self.saveDocumentAction.setEnabled(False)
        self.saveDocumentAction.triggered.connect(self.saveFile)
        
        self.calculateDerivativeAction = QAction(self.tr("Calculate Derivative"))
        self.calculateDerivativeAction.setIcon(QIcon("icons/Derivative.png"))
        self.calculateDerivativeAction.triggered.connect(self.calculateDerivative)
        self.calculateDerivativeAction.setEnabled(False)
        
        self.substractionAction = QAction(self.tr("Substract Spectra"))
        self.substractionAction.setIcon(QIcon("icons/Derivative.png"))
        self.substractionAction.triggered.connect(self.substractSpectra)
        
    def createMenuBar(self):
        self.menuBar = self.menuBar()
        self.fileMenu = QMenu(self.tr("&File"), self.menuBar)
        self.documentMenu = QMenu(self.tr("&Document"), self.menuBar)
        self.viewMenu = QMenu(self.tr("&View"), self.menuBar)
        
        # create file menu
        self.fileMenu.addAction(self.openAction)
        self.fileMenu.addAction(self.saveDocumentAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        
        # create document menu
        self.documentMenu.addSection(QIcon.fromTheme("document-edit", QIcon("icons/document-edit.svg")), self.tr("Edit"))
        self.documentMenu.addAction(self.documentTitleAction)
        self.documentMenu.addAction(self.pageEditAction)
        self.documentMenu.addSection(QIcon.fromTheme("document-save", QIcon("icons/document-save.svg")), self.tr("Save"))
        self.documentMenu.addAction(self.savePageAction)
        self.documentMenu.addAction(self.saveSpectrumAction)
        self.documentMenu.addAction(self.saveImageAction)
        
        # create view menu
        self.viewMenu.addAction(self.metadataDockAction)
        self.viewMenu.addAction(self.pageDockAction)
        self.viewMenu.addAction(self.spectraDockAction)
        self.viewMenu.addAction(self.peakpickingDockAction)
        self.viewMenu.addAction(self.integralDockAction)
        self.viewMenu.addAction(self.xrdReferenceDockAction)
        self.viewMenu.addAction(self.xrfReferenceDockAction)
        
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.documentMenu)
        self.menuBar.addMenu(self.viewMenu)
    
    def close(self):
        super().close()
        
    def enableDocumentActions(self, enabled):
        self.pageEditAction.setEnabled(enabled)
        self.saveDocumentAction.setEnabled(enabled)
        self.saveImageAction.setEnabled(enabled)
        self.documentTitleAction.setEnabled(enabled)
        self.savePageAction.setEnabled(enabled)
        self.saveSpectrumAction.setEnabled(enabled)
        self.calculateDerivativeAction.setEnabled(enabled)
        
    def openFile(self):
        dgl = opendialog.openDialog(self)
        dgl.setOpenOptions(self.currentDocument, self.currentPage)
        if dgl.exec():
            data = dgl.getData()
            if not os.path.exists(data["File Name"]):
                return
            self.settings.setValue("lastOpenDir", os.path.dirname(data["File Name"]))
            if data["File Type"] == "Any Text Format" or data["File Type"] == "MCA - DESY XRF File Format" or data["File Type"] == "pyXrfa-JSON" or data["File Type"] == "AMETEK-XRF TXT-Export":
                print(data['File Name'])
                if data["File Type"] == "Any Text Format":
                    if data["Free Text Settings"]["Spectrum Type"] == self.tr("Raman"):
                        newSpectrum = spectratypes.ramanSpectrum()
                        print("Raman")
                    elif data["Free Text Settings"]["Spectrum Type"] == self.tr("Infrared"):
                        newSpectrum = spectratypes.infraredSpectrum()
                        print("infrared")
                    elif data["Free Text Settings"]["Spectrum Type"] == self.tr("UV/VIS"):
                        newSpectrum = spectratypes.ultravioletSpectrum()
                        print("ultraviolett")
                    elif data["Free Text Settings"]["Spectrum Type"] == self.tr("Powder XRD"):
                        newSpectrum = spectratypes.powderXRD()
                        self.xrdDock.setSpectrum(newSpectrum)
                        print("Powder XRD")
                    elif data["Free Text Settings"]["Spectrum Type"] == self.tr("XRF"):
                        newSpectrum = spectratypes.xrfSpectrum()
                        self.xrfDock.setSpectrum(newSpectrum)
                        print("XRF")
                    else:
                        print("Spectrum type not implemented, yet.")
                    if not newSpectrum:
                        return
                    
                    print(newSpectrum.openFreeText(data["File Name"], data["Free Text Settings"]))
                elif data["File Type"] == "MCA - DESY XRF File Format":
                    newSpectrum = spectratypes.xrfSpectrum()
                    print("XRF - MCA")
                    print(newSpectrum.openMCA(data['File Name']))
                    self.xrfDock.setSpectrum(newSpectrum)
                elif data["File Type"] == "pyXrfa-JSON":
                    newSpectrum = spectratypes.xrfSpectrum()
                    print("XRF - pyXrfa-JSON")
                    print(newSpectrum.openPyXrfaJSON(data['File Name']))
                    self.xrfDock.setSpectrum(newSpectrum)
                elif data["File Type"] == "AMETEK-XRF TXT-Export":
                    print("AMETEK-XRF TXT-Export")
                    newSpectrum = []
                    with open(data['File Name']) as f:
                        lines = f.readlines()
                        kalib1 = [float(z.replace(",", ".")) for z in lines[0].split("\t")[1:-1]]
                        kalib2 = [float(z.replace(",", ".")) for z in lines[1].split("\t")[1:-1]]
                        x = [[] for i in range(4)]
                        y = [[] for i in range(4)]
                        
                        for i in range(7, len(lines)):
                            p = lines[i].split("\t")
                            for s in range(1, 5):
                                if (i-6) < 2049 or s == 2:
                                    x[s-1].append(kalib1[s-1] + kalib2[s-1] * (i-6))
                                    y[s-1].append(float(p[s]))
                        for i in range(4):
                            ns = spectratypes.xrfSpectrum()
                            ns.openAndSetXY(np.array(x[i]), np.array(y[i]))
                            ns.title = "Spectrum with filter " + str(i+1)
                            ns.metadata["Core Data"]["Title"] = "Spectrum with filter " + str(i+1)
                            newSpectrum.append(ns)
                
                if data['open as'] == "document":
                    document = spectivedocument.spectiveDocument(os.path.basename(data["File Name"]))
                    document.fileName = data["File Name"]
                    self._mainWidget.currentChanged.disconnect()
                    plotWidget = specplot.specplot()
                    plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                    plotWidget.plotChanged.connect(self.showPagesInDock)
                    self._mainWidget.addTab(plotWidget, os.path.basename(data["File Name"]))
                    self._mainWidget.setCurrentIndex(len(self.documents))
                    self._mainWidget.currentChanged.connect(self.documentChanged)
                    self.documents.append(document)
                    self.currentDocument = self.documents[-1]
                    if type(newSpectrum) == list:
                        for ns in newSpectrum:
                            self.currentPage = document.addPage()
                            self.currentSpectrum = self.currentPage.addSpectrum(ns)
                        if type(ns).__name__ == "xrfSpectrum":
                            self.xrfDock.setSpectrum(ns)
                    else:
                        self.currentPage = document.addPage()
                        self.currentSpectrum = self.currentPage.addSpectrum(newSpectrum)
                    
                elif data['open as'] == "page":
                    self.currentPage = self.currentDocument.addPage()
                    self.currentSpectrum = self.currentPage.addSpectrum(newSpectrum)
                else:
                    self.currentSpectrum = self.currentPage.addSpectrum(newSpectrum)
            elif data["File Type"] == "JCAMP-DX":
                blocks = spectrum.getJCAMPblockFromFile(data["File Name"])
                linkBlock = {}
                linkBlock['Title'] = os.path.basename(data["File Name"])
                linkBlock['Pages'] = 1
                linkBlock['Blocks'] = 2 # redundant
                if len(blocks) > 1:
                    # there are more then one spectrum in this file.
                    #the last block will always be the LINK block!
                    linkBlock = spectrum.loadJCAMPlinkBlock(blocks[-1])
                    blocks.pop()
                pageOffset = 0
                numPages = 0
                if 'Pages' in linkBlock:
                    numPages = linkBlock['Pages']
                else:
                    numPages = linkBlock['Blocks'] - 1
                if data['open as'] == "document":
                    document = spectivedocument.spectiveDocument(linkBlock['Title'])
                    document.fileName = data["File Name"]
                    self._mainWidget.currentChanged.disconnect()
                    plotWidget = specplot.specplot()
                    plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                    plotWidget.plotChanged.connect(self.showPagesInDock)
                    self._mainWidget.addTab(plotWidget, linkBlock['Title'])
                    self._mainWidget.setCurrentIndex(len(self.documents))
                    self._mainWidget.currentChanged.connect(self.documentChanged)
                    self.documents.append(document)
                    self.currentDocument = self.documents[-1]
                    for i in range(numPages):
                        self.currentPage = document.addPage()
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        if s.displayData['Page']:
                            self.currentSpectrum = document.pages[s.displayData['Page'] - 1].addSpectrum(s)
                        else:
                            self.currentSpectrum = document.pages[i-1].addSpectrum(s)
                elif data['open as'] == "page":
                    pageOffset = len(self.currentDocument.pages)
                    for i in range(numPages):
                        self.currentPage = self.currentDocument.addPage()
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        if s.displayData['Page']:
                            self.currentSpectrum = self.currentDocument.pages[pageOffset + s.displayData['Page'] - 1].addSpectrum(s)
                        else:
                            self.currentSpectrum = self.currentDocument.pages[pageOffset + i-1].addSpectrum(s)
                    self.currentPage = self.currentDocument.currentPage
                    self.currentSpectrum = self.currentPage.currentSpectrum
                else:
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        self.currentSpectrum = self.currentPage.addSpectrum(s)
            for p in self.currentDocument.pages:
                self._mainWidget.currentWidget().setPage(p)
                p.icon = self._mainWidget.currentWidget().getIcon()
            self.enableDocumentActions(True)
            self.showPagesInDock()
            self.pageView.setCurrentRow(self.currentDocument.getCurrentPageIndex())
            self.showSpectraInDock()
            self.enableDocks()
                        
    def openSpectrum(self, block):
        """
        Opens a Spectrum from a JCAMP-DX Block

        Parameters
        ----------
        block : String
            DESCRIPTION.

        Returns
        -------
        None.

        """
        if "INFRARED SPECTRUM" in block.upper():
            # it is an infrared spectrum!
            newSpectrum = spectratypes.infraredSpectrum()
            print("infrared")
        elif "RAMAN SPECTRUM" in block.upper():
            # it is a Raman Spectrum!
            print("raman")
            newSpectrum = spectratypes.ramanSpectrum()
        elif "ULTRAVIOLET SPECTRUM" in block.upper():
            # it is an UV-VIS spectrum!
            newSpectrum = spectratypes.ultravioletSpectrum()
            print("ultraviolet")
        elif "POWDER X-RAY DIFFRACTION" in block.upper():
            # it is a powder XRD spectrum!
            newSpectrum = spectratypes.powderXRD()
            print("pXRD")
        elif "X-RAY FLUORESCENCE SPECTRUM" in block.upper():
            # it is a powder XRF spectrum!
            newSpectrum = spectratypes.xrfSpectrum()
            print("XRF")
        if newSpectrum.openJCAMPDXfromString(block):
            return newSpectrum
        return False
    
    def saveImage(self):
        dgl = exportdialog.exportDialog()
        if dgl.exec():
            data = dgl.getData()
            if self.settings.value("lastImageSavePath"):
                fileName, filterType = QFileDialog.getSavepenFileName(None, "Save Image", self.settings.value("lastImageSavePath"), self.tr("Portable Network Graphic (*.png)"))
            else:
                fileName, filterType = QFileDialog.getSaveFileName(None, "Save Image", QDir.homePath(), self.tr("Portable Network Graphic (*.png)"))
            if fileName:
                if not fileName.endswith(".png"):
                    fileName += ".png"
                self.settings.setValue("lastImageSavePath", os.path.dirname(fileName))
                self._mainWidget.currentWidget().saveAsImage(fileName, data['dpi'])
    
    def changeMode(self, a):
        if a == self.zoomAction:
            self.currentMode = "ZoomMode"
            
        elif a == self.integrationAction:
            self.currentMode = "IntegrationMode"
            
        if self.currentDocument:
            self.currentDocument.setMode(self.currentMode)
    
    def keyPressEvent(self, evt):
        if evt.key() == Qt.Key.Key_Shift:
            self.integrationAction.trigger()
        
        super(ApplicationWindow, self).keyPressEvent(evt)
        
    
    def keyReleaseEvent(self, evt):
        if evt.key() == Qt.Key.Key_Shift:
            self.zoomAction.trigger()
            
        super(ApplicationWindow, self).keyReleaseEvent(evt)
    
    def showPositionInStatusBar(self, x, y):
        self.statusBar.showMessage(f"Position: {x}, {y}")
    
    def showMetadataDock(self, show):
        if show:
            self.metadataDock.show()
        else: 
            self.metadataDock.hide()
            
    def showPageDock(self, show):
        if show:
            self.pageDock.show()
        else: 
            self.pageDock.hide()
            
    def showSpectraDock(self, show):
        if show:
            self.spectraDock.show()
        else: 
            self.spectraDock.hide()
            
    def showPeakpickingDock(self, show):
        if show:
            self.peakpickingDock.show()
        else: 
            self.peakpickingDock.hide()
            
    def showIntegralDock(self, show):
        if show:
            self.integralDock.show()
        else: 
            self.integralDock.hide()
            
    def showXrdReferenceDock(self, show):
        if show:
            self.xrdDock.show()
        else: 
            self.xrdDock.hide()
            
    def showXrfReferenceDock(self, show):
        if show:
            self.xrfDock.show()
        else: 
            self.xrfDock.hide()

    def enableDocks(self):
        if type(self.currentSpectrum).__name__ == "powderXRD":
            self.xrdDock.setSpectrum(self.currentSpectrum)
            self.xrdDock.setEnabled(True)
        else: 
            self.xrdDock.setEnabled(False)
        if type(self.currentSpectrum).__name__ == "xrfSpectrum":
            self.xrfDock.setSpectrum(self.currentSpectrum)
            self.xrfDock.setEnabled(True)
        else:
            self.xrfDock.setEnabled(False)
        
    def saveFile(self):
        if not self.currentDocument.fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        else:
            fileName = self.currentDocument.fileName
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.currentDocument.fileName = fileName
            self.currentDocument.saveDocument()
    
    def showPagesInDock(self):
        self.pageView.currentRowChanged.disconnect()
        if not self.currentDocument:
            return
        self.pageView.clear()
        self.currentPage.icon = self._mainWidget.currentWidget().getIcon()
        for page in self.currentDocument.pages:
            if page.icon:
                newItem = QListWidgetItem(page.icon, page.figureData['PageTitle'])
            else:
                newItem = QListWidgetItem(page.figureData['PageTitle'])
            self.pageView.addItem(newItem)
        self.pageView.setCurrentRow(self.currentDocument.getCurrentPageIndex())
        self.pageView.currentRowChanged.connect(self.pageChanged)
        if self.currentSpectrum:
            self.integralDock.setSpectrum(self.currentSpectrum)
    
    def showSpectraInDock(self):
        if not self.currentDocument:
            return
        if not self.currentPage:
            return
        self.spectraList.currentRowChanged.disconnect()
        self.spectraList.clear()
        for s in self.currentPage.spectra:
            pix = QPixmap(QSize(32,32))
            pix.fill(QColor.fromString(s.color))
            icon = QIcon(pix)
            item = QListWidgetItem(icon, s.title)
            self.spectraList.addItem(item)
        self.spectraList.currentRowChanged.connect(self.currentSpectrumChanged)
        if self.currentPage and self.currentSpectrum:
            self.spectraList.setCurrentRow(self.currentPage.getCurrentSpectrumIndex())
    
    def documentChanged(self, index):
        if index < 0:
            self.currentDocument = None
            return 
        self.currentDocument = self.documents[index]
        self.currentPage = self.currentDocument.currentPage
        self.currentSpectrum = self.currentPage.currentSpectrum
        self.showPagesInDock()
        self.pageView.setCurrentRow(self.currentDocument.getCurrentPageIndex())
        self.showSpectraInDock()
        self.spectraList.setCurrentRow(self.currentPage.getCurrentSpectrumIndex())
        self.enableDocks()
    
    def pageChanged(self, index):
        self.currentPage = self.currentDocument.goToPage(index)
        self.currentSpectrum = self.currentPage.currentSpectrum
        self._mainWidget.currentWidget().setPage(self.currentPage)
        self.currentPage.icon = self._mainWidget.currentWidget().getIcon()
        self.showPagesInDock()        
        self.showSpectraInDock()
        self.spectraList.setCurrentRow(self.currentPage.getCurrentSpectrumIndex())
        self.enableDocks()
        
    def closeDocument(self, index):
        if index == self.documents.index(self.currentDocument):
            self.pageView.clear()
            self.spectraView.clear()
            self.xrdDock.setEnabled(False)
            self.xrfDock.setEnabled(False)
        del self.documents[index]
        self._mainWidget.removeTab(index)
        if self._mainWidget.currentIndex() < 0:
            # no documents open
            self.enableDocumentActions(False)
    
    def setDocumentTitle(self):
        if not self.currentDocument:
            return
        title, ok = QInputDialog.getText(self, self.tr("Set Document Title"), self.tr("New Document Title"), QLineEdit.EchoMode.Normal, self.currentDocument.title)
        if ok and  title != "":
            self.currentDocument.title = title
            self._mainWidget.setTabText(self._mainWidget.currentIndex(), title)
    
    def saveSpectrum(self):
        if self.settings.value("LastSaveDir"):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
        else:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.currentDocument.saveSpectrum(self.currentSpectrumIndex, fileName)
            
    def savePage(self):
        if self.settings.value("LastSaveDir"):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
        else:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.currentDocument.savePage(fileName)
    
    def pageEdit(self, row = -1):
        if row == -1 or not row:
            return
        dgl = pagedialog.pageDialog()
        if type(row) != int:
            row = self.pageView.row(row)
        if row != self.pageView.currentRow():
            self.pageView.setCurrentRow(row)
        dgl.setData(self.currentPage.figureData)
        if dgl.exec():
            data = dgl.getData()
            self.currentPage.setFigureData(data)
            self.updatePlot()
            self.showPagesInDock()
    
    def pageUp(self, row):
        if row < 1:
            return
        self.currentDocument.pages[row], self.currentDocument.pages[row - 1] = self.currentDocument.pages[row - 1], self.currentDocument.pages[row]
        self.currentPage = self.currentDocument.pages[self.currentDocument.pages.index(self.currentPage) - 1]
        self.showPagesInDock()
    
    def pageDown(self, row):
        maxRow = len(self.currentDocument.pages) - 1
        if row > maxRow - 1:
            return
        self.currentDocument.pages[row], self.currentDocument.pages[row + 1] = self.currentDocument.pages[row + 1], self.currentDocument.pages[row]
        self.currentPage = self.currentDocument.pages[self.currentDocument.pages.index(self.currentPage) + 1]
        self.showPagesInDock()
    
    def pageDelete(self, row):
        delP = self.currentDocument.deletePage(row)
        print(delP)
        if delP:
            self.pageChanged(delP)
        self.showPagesInDock()
        
    
    def spectrumEdit(self, row):
        if type(row) != int:
            row = self.spectraList.row(row)
        self.currentSpectrum = self.currentPage.setCurrentSpectrum(row)
        dgl = spectrumdialog.spectrumDialog()
        dgl.setData(self.currentSpectrum.getDisplayData())
        if dgl.exec():
            self.currentSpectrum.setDisplayData(dgl.getData())
            self._mainWidget.currentWidget().updatePlot()
            self.showSpectraInDock()
    
    def spectrumUp(self, row):
        if row < 1:
            return
        self.currentSpectrum = self.currentPage.spectrumUp(row)
        self.showSpectraInDock()
        
    def spectrumDown(self, row):
        maxRow = len(self.currentPage.spectra) - 1
        if row > maxRow - 1:
            return
        self.currentSpectrum = self.currentPage.spectrumDown(row)
        self.showSpectraInDock()
    
    def spectrumDelete(self, row):
        self.currentSpectrum = self.currentPage.deleteSpectrum(row)
        self.showSpectraInDock()
            
    def currentSpectrumChanged(self, index):
        self.currentSpectrum = self.currentPage.setCurrentSpectrum(index)
        self.metadataDock.dataChanged.disconnect()
        self.metadataDock.setData(self.currentSpectrum.metadata)
        self.metadataDock.dataChanged.connect(self.updateMetadata)
        self.peakpickingDock.setSpectrum(self.currentSpectrum)
        self.integralDock.setSpectrum(self.currentSpectrum)
        self.enableDocks()
    
    def updateMetadata(self, data):
        self.currentSpectrum.metadata = data
        self.currentSpectrum.title = data["Core Data"]["Title"]
        self.showSpectraInDock()
    
    def updatePlot(self):
        self._mainWidget.currentWidget().updatePlot()
        
    def calculateDerivative(self):
        spec = self.currentSpectrum.calculateDerivative()
        self.currentSpectrum = self.currentPage.addSpectrum(spec)
        self.updatePlot()
        self.showSpectraInDock()
        
    def substractSpectra(self):
        dgl = processdocks.substractionDialog(self.currentDocument)
        if dgl.exec():
            data = dgl.getData()
            data['Target Page'] -= 1
            minuend = None
            subtrahend = None
            for s in self.currentPage.spectra:
                if s.title == data['Minuend']:
                    minuend = s
                if s.title == data['Subtrahend']:
                    subtrahend = s
            if not minuend or not subtrahend:
                return
            if type(minuend).__name__ == "ramanSpectrum":
                newSpectrum = spectratypes.ramanSpectrum()
                newSpectrum.metadata = copy.deepcopy(minuend.metadata)
            else:
                return
            scale = 1.0
            if data['Scaled']:
                maxX = subtrahend.x[np.argmax(subtrahend.y)]
                maxY = np.max(subtrahend.y)
                for i in range(1, len(minuend.x)):
                    if minuend.x[i-1] < maxX and minuend.x[i] > maxX:
                        m = (minuend.y[i] - minuend.y[i-1]) / (minuend.x[i] - minuend.x[i-1])
                        n = minuend.y[i] - m * minuend.x[i]
                        scale = (m * maxX + n) / maxY
                        break
                    elif minuend.x[i-1] == maxX:
                        scale = minuend.y[i-1] / maxY
                        break
                    elif minuend.x[i] == maxX:
                        scale = minuend.y[i] / maxY
                        break
                if scale > 1:
                    scale = 1
                
            if data['Abscissa'] == "Minuend":
                newSpectrum.x = minuend.x.copy()
                for x in range(len(minuend.x)):
                    for i in range(1, len(subtrahend.x)):
                        if (subtrahend.x[i-1] < minuend.x[x] and subtrahend.x[i] > minuend.x[x]) or (subtrahend.x[i-1] > minuend.x[x] and subtrahend.x[i] < minuend.x[x]):
                            m = (subtrahend.y[i] - subtrahend.y[i-1]) / (subtrahend.x[i] - subtrahend.x[i-1])
                            n = subtrahend.y[i] - m * subtrahend.x[i]
                            newSpectrum.y.append(minuend.x[x] - (m*minuend.x[x]+n) * scale)
                            break
                        if subtrahend.x[i-1] == minuend.x[x]:
                            newSpectrum.y.append(minuend.y[x] - subtrahend.y[i-1] * scale)
                            break
                        if subtrahend.x[i] == minuend.x[x]:
                            newSpectrum.y.append(minuend.y[x] - subtrahend.y[i] * scale)
                            break
            if data['Abscissa'] == "Subtrahend":
                newSpectrum.x = subtrahend.x.copy()
                for x in range(len(subtrahend.x)):
                    for i in range(1, len(minuend.x)):
                        if (minuend.x[i-1] < subtrahend.x[x] and minuend.x[i] > subtrahend.x[x]) or (minuend.x[i-1] > subtrahend.x[x] and minuend.x[i] < subtrahend.x[x]):
                            m = (minuend.y[i] - minuend.y[i-1]) / (minuend.x[i] - minuend.x[i-1])
                            n = minuend.y[i] - m * minuend.x[i]
                            newSpectrum.y.append((m*subtrahend.x[x]+n) - subtrahend.x[x] * scale)
                            break
                        if minuend.x[i-1] == subtrahend.x[x]:
                            newSpectrum.y.append(minuend.y[i-1] - subtrahend.y[x] * scale)
                            break
                        if minuend.x[i] == subtrahend.x[x]:
                            newSpectrum.y.append(minuend.y[i] - subtrahend.y[x] * scale)
                            break
            newSpectrum.y = np.array(newSpectrum.y)
            newSpectrum.title = data['Minuend'] + " - " + data['Subtrahend']
            if data['Scaled']:
                newSpectrum.title += " (scaled)"
            
            newSpectrum.metadata["Core Data"]["Title"] = newSpectrum.title
            newSpectrum.metadata["Sampling Information"]["Data Processing"] += "\r\ņSubstraction of " + newSpectrum.title
            newSpectrum.metadata["Sampling Information"]["Data Processing"] = newSpectrum.metadata["Sampling Information"]["Data Processing"].strip()
            if data['Target Page'] == -1:
                self.currentPage = self.currentDocument.addPage()

            newSpectrum.xlim = [np.min(newSpectrum.x), np.max(newSpectrum.x)]
            newSpectrum.ylim = [np.min(newSpectrum.y), np.max(newSpectrum.y)]
            self.currentSpectrum = self.currentPage.addSpectrum(newSpectrum)
            self.showSpectraInDock()
            self.showPagesInDock()
            
                
if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    sys.exit(qapp.exec())
