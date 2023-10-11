#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:46:12 2023

@author: marcus
"""

import sys
import os
import re

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
        self.currentDocumentIndex = -1
        self.currentPageIndex = -1
        self.currentSpectrumIndex = -1
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
        
    def enableDocumentActions(self):
        self.pageEditAction.setEnabled(True)
        self.saveDocumentAction.setEnabled(True)
        self.saveImageAction.setEnabled(True)
        self.documentTitleAction.setEnabled(True)
        self.savePageAction.setEnabled(True)
        self.saveSpectrumAction.setEnabled(True)
        self.calculateDerivativeAction.setEnabled(True)
        
    def openFile(self):
        dgl = opendialog.openDialog(self)
        dgl.setOpenOptions(self.currentDocumentIndex, self.currentPageIndex)
        if dgl.exec():
            data = dgl.getData()
            if not os.path.exists(data["File Name"]):
                return
            self.settings.setValue("lastOpenDir", os.path.dirname(data["File Name"]))
            if data["File Type"] == "Any Text Format" or data["File Type"] == "MCA - DESY XRF File Format" or data["File Type"] == "pyXrfa-JSON":
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
                
                if data['open as'] == "document":
                    document = spectivedocument.spectiveDocument(os.path.basename(data["File Name"]))
                    self._mainWidget.currentChanged.disconnect()
                    self._mainWidget.addTab(document, os.path.basename(data["File Name"]))
                    self._mainWidget.setCurrentIndex(len(self.documents))
                    self._mainWidget.currentChanged.connect(self.documentChanged)
                    self.documents.append(document)
                    self.currentDocumentIndex = len(self.documents)-1
                    document.addPage("plot")
                    document.pages[0].plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                    document.pages[0].plotWidget.plotChanged.connect(self.showPagesInDock)
                    self.currentPageIndex = 0
                    document.pages[0].addSpectrum(newSpectrum)
                    
                elif data['open as'] == "page":
                    document = self.documents[self.currentDocumentIndex]
                    document.addPage("plot")
                    document.pages[-1].plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                    document.pages[-1].plotWidget.plotChanged.connect(self.showPagesInDock)
                    self.currentPageIndex = len(document.pages) - 1
                    document.pages[-1].addSpectrum(newSpectrum)
                else:
                    document = self.documents[self.currentDocumentIndex]
                    document.pages[self.currentPageIndex].addSpectrum(newSpectrum)
                    self.currentSpectrumIndex += 1 
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
                    self._mainWidget.currentChanged.disconnect()
                    self._mainWidget.addTab(document, linkBlock['Title'])
                    self._mainWidget.setCurrentIndex(len(self.documents))
                    self._mainWidget.currentChanged.connect(self.documentChanged)
                    self.documents.append(document)
                    self.currentDocumentIndex = len(self.documents)-1
                    for i in range(numPages):
                        document.addPage("plot")
                        document.pages[-1].plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                        document.pages[-1].plotWidget.plotChanged.connect(self.showPagesInDock)
                        self.currentPageIndex = i
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        if type(s).__name__ == "powderXRD":
                            self.xrdDock.setSpectrum(s)
                        elif type(s).__name__ == "xrfSpectrum":
                            self.xrfDock.setSpectrum(s)
                        if s.displayData['Page']:
                            document.pages[s.displayData['Page'] - 1].addSpectrum(s)
                        else:
                            document.pages[i-1].addSpectrum(s)
                    self.currentSpectrumIndex = 0
                elif data['open as'] == "page":
                    document = self.documents[self.currentDocumentIndex]
                    pageOffset = len(document.pages)
                    for i in range(numPages):
                        document.addPage("plot")
                        document.pages[-1].plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                        document.pages[-1].plotWidget.plotChanged.connect(self.showPagesInDock)
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        if type(s).__name__ == "powderXRD":
                            self.xrdDock.setSpectrum(s)
                        elif type(s).__name__ == "xrfSpectrum":
                            self.xrfDock.setSpectrum(s)
                        if s.displayData['Page']:
                            document.pages[pageOffset + s.displayData['Page'] - 1].addSpectrum(s)
                        else:
                            document.pages[pageOffset + i-1].addSpectrum(s)
                    self.currentPageIndex = pageOffset
                    self.currentSpectrumIndex = 0
                else:
                    document = self.documents[self.currentDocumentIndex]
                    for i in range(len(blocks)):
                        s = self.openSpectrum(blocks[i])
                        if not s:
                            continue
                        if type(s).__name__ == "powderXRD":
                            self.xrdDock.setSpectrum(s)
                        elif type(s).__name__ == "xrfSpectrum":
                            self.xrfDock.setSpectrum(s)
                        document.pages[self.currentPageIndex].addSpectrum(s)
                    self.currentSpectrumIndex += 1 
            self.showPagesInDock()
            self.showSpectraInDock()
            self.enableDocumentActions()
                        
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
            fileName, fileTypeFilter = QFileDialog.getSaveFileName(self, "Export Current View", QDir.homePath(), self.tr("Portable Network Graphic (*.png);;Portable Document Format (*.pdf);;Scalable Vector Graphics (*.svg);; Encapsulated PostScript (*.eps);;Tagged Image File Format (*.tif)"))
            if fileName:
                m = re.search(r"\*(\.\w{3})", fileTypeFilter, re.IGNORECASE)
                if not fileName.endswith(m.group(1)):
                    fileName += m.group(1)
                w = self._mainWidget.currentWidget()
                w.figure.savefig(fileName, dpi=data["dpi"])
    
    def changeMode(self, a):
        if a == self.zoomAction:
            self.currentMode = "ZoomMode"
            
        elif a == self.integrationAction:
            self.currentMode = "IntegrationMode"
            
        if self.currentDocumentIndex < len(self.documents) and self.currentDocumentIndex >= 0:
            document = self.documents[self.currentDocumentIndex]
            document.setMode(self.currentMode)
    
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

    def saveFile(self):
        if not self.documents[self.currentDocumentIndex].fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        else:
            fileName = self.documents[self.currentDocumentIndex].fileName
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.documents[self.currentDocumentIndex].fileName = fileName
            self.documents[self.currentDocumentIndex].saveDocument()
    
    def showPagesInDock(self):
        self.pageView.currentRowChanged.disconnect()
        if self.currentDocumentIndex > len(self.documents) or self.currentDocumentIndex < 0:
            return
        self.pageView.clear()
        for page in self.documents[self.currentDocumentIndex].pages:
            newItem = QListWidgetItem(page.plotWidget.getIcon(), page.title)
            self.pageView.addItem(newItem)
        self.pageView.setCurrentRow(self.currentPageIndex)
        self.pageView.currentRowChanged.connect(self.pageChanged)
        if self.currentSpectrumIndex >= 0 and self.currentSpectrumIndex < len(page.spectra):
            self.integralDock.setSpectrum(page.spectra[self.currentSpectrumIndex])
    
    def showSpectraInDock(self):
        if self.currentDocumentIndex >= len(self.documents) or self.currentDocumentIndex < 0:
            return
        document = self.documents[self.currentDocumentIndex]
        if self.currentPageIndex >= len(document.pages) or self.currentPageIndex < 0:
            return
        self.spectraList.currentRowChanged.disconnect()
        page = document.pages[self.currentPageIndex]
        self.spectraList.clear()
        for s in page.spectra:
            pix = QPixmap(QSize(32,32))
            pix.fill(QColor.fromString(s.color))
            icon = QIcon(pix)
            item = QListWidgetItem(icon, s.title)
            self.spectraList.addItem(item)
        self.spectraList.currentRowChanged.connect(self.currentSpectrumChanged)
        if self.currentSpectrumIndex >= 0 and self.currentSpectrumIndex < len(page.spectra):
            self.spectraList.setCurrentRow(self.currentSpectrumIndex)
        else:
            self.spectraList.setCurrentRow(len(page.spectra)-1)
            self.currentSpectrumIndex = len(page.spectra)-1
    
    def documentChanged(self, index):
        self.currentDocumentIndex = index
        self.showPagesInDock()
        self.showSpectraInDock()
    
    def pageChanged(self, index):
        self.currentPageIndex = index
        self.showSpectraInDock()
        self.documents[self.currentDocumentIndex].goToPage(index)
        
    def closeDocument(self, index):
        if index == self.currentDocumentIndex:
            self.pageView.clear()
        del self.documents[index]
        self._mainWidget.removeTab(index)
        if self._mainWidget.currentIndex() < 0:
            # no documents open
            self.figureAction.setEnabled(False)
            self.saveAction.setEnabled(False)
            self.imageSaveAction.setEnabled(False)
    
    def setDocumentTitle(self):
        document = self.documents[self.currentDocumentIndex]
        if not document:
            return
        title, ok = QInputDialog.getText(self, self.tr("Set Document Title"), self.tr("New Document Title"), QLineEdit.EchoMode.Normal, document.title)
        if ok and  title != "":
            document.title = title
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
            self.documents[self.currentDocumentIndex].saveSpectrum(self.currentSpectrumIndex, fileName)
            
    def savePage(self):
        if self.settings.value("LastSaveDir"):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
        else:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.documents[self.currentDocumentIndex].savePage(fileName)
    
    def pageEdit(self, row = -1):
        dgl = pagedialog.pageDialog()
        if row == -1 or not row:
            row = self.currentPageIndex
        if type(row) != int:
            row = self.pageView.row(row)
        if row != self.currentPageIndex:
            self.pageView.setCurrentRow(row)
        dgl.setData(self.documents[self.currentDocumentIndex].getFigureData())
        if dgl.exec():
            data = dgl.getData()
            self.documents[self.currentDocumentIndex].setFigureData(data)
            self.currentSpectrumChanged(self.currentSpectrumIndex)
    
    def pageUp(self, row):
        document = self.documents[self.currentDocumentIndex]
        if row < 1:
            return
        document.pages[row], document.pages[row - 1] = document.pages[row - 1], document.pages[row]
        self.currentPageIndex -= 1
        self.showPagesInDock()
    
    def pageDown(self, row):
        document = self.documents[self.currentDocumentIndex]
        maxRow = len(document.pages) - 1
        if row > maxRow - 1:
            return
        document.pages[row], document.pages[row + 1] = document.pages[row + 1], document.pages[row]
        self.currentPageIndex += 1
        self.showPagesInDock()
    
    def pageDelete(self, row):
        document = self.documents[self.currentDocumentIndex]
        self.currentPageIndex = document.deletePage(row)
        self.showPagesInDock()
        
    
    def spectrumEdit(self, row):
        if type(row) != int:
            row = self.spectraList.row(row)
        self.currentSpectrumIndex = row
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        spectrum = page.spectra[row]
        dgl = spectrumdialog.spectrumDialog()
        dgl.setData(spectrum.getDisplayData())
        if dgl.exec():
            spectrum.setDisplayData(dgl.getData())
            page.updatePlot()
            self.showSpectraInDock()
    
    def spectrumUp(self, row):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        if row < 1:
            return
        page.spectrumUp(row)
        self.currentSpectrumIndex -= 1
        self.showSpectraInDock()
        
    def spectrumDown(self, row):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        maxRow = len(page.spectra) - 1
        if row > maxRow - 1:
            return
        page.spectrumDown(row)
        self.currentSpectrumIndex += 1
        self.showSpectraInDock()
    
    def spectrumDelete(self, row):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        self.currentSpectrumIndex = page.deleteSpectrum(row)
        self.showSpectraInDock()
            
    def currentSpectrumChanged(self, index):
        self.currentSpectrumIndex = index
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        page.setCurrentSpectrum(index)
        spectrum = page.spectra[index]
        self.metadataDock.dataChanged.disconnect()
        self.metadataDock.setData(spectrum.metadata)
        self.metadataDock.dataChanged.connect(self.updateMetadata)
        self.peakpickingDock.setSpectrum(spectrum)
        self.integralDock.setSpectrum(page.spectra[self.currentSpectrumIndex])
    
    def updateMetadata(self, data):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        spectrum = page.spectra[self.currentSpectrumIndex]
        spectrum.metadata = data
        spectrum.title = data["Core Data"]["Title"]
        self.showSpectraInDock()
    
    def updatePlot(self):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        page.updatePlot()
        
    def calculateDerivative(self):
        document = self.documents[self.currentDocumentIndex]
        page = document.pages[self.currentPageIndex]
        spectrum = page.spectra[self.currentSpectrumIndex]
        spec = spectrum.calculateDerivative()
        page.addSpectrum(spec)
        self.showSpectraInDock()
            
                
if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    sys.exit(qapp.exec())
