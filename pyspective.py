#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:46:12 2023

@author: marcus
"""

import sys
import os
import re

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QPixmap, QColor
from PyQt6.QtCore import QDir, Qt, QSize
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
        self.setWindowTitle("Pyspective")
        self._mainWidget = QTabWidget(self)
        self._mainWidget.currentChanged.connect(self.documentChanged)
        self._mainWidget.tabCloseRequested.connect(self.closeDocument)
        self._mainWidget.setTabsClosable(True)
        self.setCentralWidget(self._mainWidget)
        self.createActions()
        self.createMenuBar()
        self.createMainWidgets()
        
        self.documents = []
        self.currentDocumentIndex = None
        self.currentPageIndex = None
        self.currentSpectrumIndex = None
        
        # settings
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("state"):
            self.restoreState(self.settings.value("state"))
        if self.settings.value("metadataDockGeometry"):
            self.metadataDock.restoreGeometry(self.settings.value("metadataDockGeometry"))
        
        # init checkable actions
        self.metadataDockAction.setChecked(not self.metadataDock.isHidden())
        self.pageDockAction.setChecked(not self.pageDock.isHidden())
        self.spectraDockAction.setChecked(not self.spectraDock.isHidden())
    
    def closeEvent(self, evt):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("metadataDockGeometry", self.metadataDock.saveGeometry())
        super(ApplicationWindow, self).closeEvent(evt)
        
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
        
        self.statusBar = self.statusBar()
        
        self.metadataDock = metadatadock.metadataDock(self)
        self.metadataDock.setObjectName("metaDataDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.metadataDock)
        self.metadataDock.visibilityChanged.connect(lambda show: self.metadataDockAction.setChecked(show))
        self.metadataDock.dataChanged.connect(self.updateMetadata)
        
        self.pageDock = QDockWidget(self.tr("Pages"), self)
        self.pageDock.setObjectName("pagesDock")
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
        self.peakpickingDock.setObjectName("PeakPickingDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.peakpickingDock)
        self.peakpickingDock.visibilityChanged.connect(lambda show: self.peakpickingDockAction.setChecked(show))
        self.peakpickingDock.peaksChanged.connect(self.updatePlot)
        #self.peakpickingDock.hide()
        
    def createActions(self):
        self.closeAction = QAction(self.tr('Quit'))
        self.closeAction.setIcon(QIcon.fromTheme("application-exit", QIcon("icons/application-exit.avg")))
        self.closeAction.triggered.connect(self.close)
        
        self.openAction = QAction(self.tr('Open Spectrum'))
        self.openAction.setIcon(QIcon.fromTheme("document-open", QIcon("icons/document-open.svg")))
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
        self.saveImageAction.setIcon(QIcon.fromTheme("image-png", QIcon("icons/image-png.svg")))
        self.saveImageAction.triggered.connect(self.saveImage)
        self.saveImageAction.setEnabled(False)
        
        self.metadataDockAction = QAction(self.tr('Show and Edit Metadata'))
        self.metadataDockAction.setCheckable(True)
        self.metadataDockAction.triggered.connect(self.showMetadataDock)
        
        self.pageDockAction = QAction(self.tr('Show Page Dock'))
        self.pageDockAction.setCheckable(True)
        self.pageDockAction.triggered.connect(self.showPageDock)
        
        self.spectraDockAction = QAction(self.tr('Show Spectra Dock'))
        self.spectraDockAction.setCheckable(True)
        self.spectraDockAction.triggered.connect(self.showSpectraDock)
        
        self.peakpickingDockAction = QAction(self.tr('Show Peakpicking Dock'))
        self.peakpickingDockAction.setCheckable(True)
        self.peakpickingDockAction.triggered.connect(self.showPeakpickingDock)
        
        self.pageEditAction = QAction(self.tr('Edit Page'))
        self.pageEditAction.triggered.connect(self.pageEdit)
        self.pageEditAction.setEnabled(False)
        
        self.saveDocumentAction = QAction(self.tr('&Save Document as JCAMP-DX'))
        self.saveDocumentAction.setIcon(QIcon.fromTheme("document-save", QIcon("icons/document-save.svg")))
        self.saveDocumentAction.setShortcut(QKeySequence("Ctrl+S"))
        self.saveDocumentAction.setEnabled(False)
        self.saveDocumentAction.triggered.connect(self.saveFile)
        
        self.calculateDerivativeAction = QAction(self.tr("Calculate Derivative"))
        self.calculateDerivativeAction.triggered.connect(self.calculateDerivative)
        
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
        
    def openFile(self):
        dgl = opendialog.openDialog(self)
        dgl.setOpenOptions(self.currentDocumentIndex, self.currentPageIndex)
        if dgl.exec():
            data = dgl.getData()
            if not os.path.exists(data["File Name"]):
                return
            self.settings.setValue("lastOpenDir", os.path.dirname(data["File Name"]))
            if data["File Type"] == "Any Text Format":
                if data["Free Text Settings"]["Spectrum Type"] == "Raman":
                    newSpectrum = spectratypes.ramanSpectrum()
                    if newSpectrum.openFreeText(fileName=data["File Name"], options=data["Free Text Settings"]):
                        pass
                else:
                    pass
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
            document = self.documents[self.currentDocumentIndex].saveSpectrum(self.currentSpectrumIndex, fileName)
            
    def savePage(self):
        if self.settings.value("LastSaveDir"):
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
        else:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            document = self.documents[self.currentDocumentIndex].savePage(fileName)
    
    def pageEdit(self, row = -1):
        dgl = pagedialog.pageDialog()
        if row == -1:
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
        spectrum = page.spectra[index]
        self.metadataDock.dataChanged.disconnect()
        self.metadataDock.setData(spectrum.metadata)
        self.metadataDock.dataChanged.connect(self.updateMetadata)
        self.peakpickingDock.setSpectrum(spectrum)
    
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
