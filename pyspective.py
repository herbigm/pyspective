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
from PyQt6.QtGui import QAction, QIcon, QKeySequence
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
    QAbstractScrollArea
)

import spectivedocument
import spectrum
import spectratypes
import opendialog
import metadatadock
import exportdialog
import figuredialog
import pageview

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
        self.metadataAction.setChecked(not self.metadataDock.isHidden())
    
    def closeEvent(self, evt):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        self.settings.setValue("metadataDockGeometry", self.metadataDock.saveGeometry())
        super(ApplicationWindow, self).closeEvent(evt)
        
    def createMainWidgets(self):
        # create Toolbar and Statusbar
        self.toolBar = self.addToolBar('Main')
        self.toolBar.setObjectName("MainToolBar")
        self.toolBarTabWidget = QTabWidget(self.toolBar)
        self.toolBarTabWidget.setFixedHeight(100)
        self.toolBar.addWidget(self.toolBarTabWidget)
        
        self.statusBar = self.statusBar()
        
        self.metadataDock = metadatadock.metadataDock(self)
        self.metadataDock.setObjectName("metadataDock")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.metadataDock)
        self.metadataDock.visibilityChanged.connect(self.showMetadataAction)
        
        self.pageDock = QDockWidget(self)
        self.pageDock.setWindowTitle(self.tr("Pages"))
        self.pageDock.setObjectName("pagesDock")
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pageDock)
        self.pageView = pageview.pageView(self)
        self.pageView.currentRowChanged.connect(self.pageChanged)
        self.pageDock.setWidget(self.pageView)
        
    def createActions(self):
        self.closeAction = QAction(self.tr('Quit'))
        self.closeAction.setIcon(QIcon.fromTheme("application-exit", QIcon("icons/application-exit.avg")))
        self.closeAction.triggered.connect(self.close)
        
        self.openNew = QAction(self.tr('Open Spectrum'))
        self.openNew.setIcon(QIcon.fromTheme("document-open", QIcon("icons/document-open.svg")))
        self.openNew.triggered.connect(lambda: self.openFile())
        
        self.imageSaveAction = QAction(self.tr('Export Current View to Image File'))
        self.imageSaveAction.setIcon(QIcon.fromTheme("image-png", QIcon("icons/image-png.svg")))
        self.imageSaveAction.triggered.connect(self.saveImage)
        self.imageSaveAction.setEnabled(False)
        
        self.metadataAction = QAction(self.tr('Show and Edit Metadata'))
        self.metadataAction.setCheckable(True)
        self.metadataAction.triggered.connect(self.showMetadataDock)
        
        self.figureAction = QAction(self.tr('Edit Figure Options'))
        self.figureAction.triggered.connect(self.showFigureDialog)
        self.figureAction.setEnabled(False)
        
        self.saveAction = QAction(self.tr('&Save File as JCAMP-DX'))
        self.saveAction.setIcon(QIcon.fromTheme("document-save", QIcon("icons/document-save.svg")))
        self.saveAction.setShortcut(QKeySequence("Ctrl+S"))
        self.saveAction.setEnabled(False)
        self.saveAction.triggered.connect(self.saveFile)
        
    def createMenuBar(self):
        self.menuBar = self.menuBar()
        self.fileMenu = QMenu(self.tr("&File"), self.menuBar)
        self.spectrumMenu = QMenu(self.tr("&Spectrum"), self.menuBar)
        self.viewMenu = QMenu(self.tr("&View"), self.menuBar)
        
        # create file menu
        self.fileMenu.addAction(self.openNew)
        self.fileMenu.addAction(self.imageSaveAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        
        # create spectrum menu
        self.spectrumMenu.addAction(self.figureAction)
        
        # create view menu
        self.viewMenu.addAction(self.metadataAction)
        
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.spectrumMenu)
        self.menuBar.addMenu(self.viewMenu)
    
    def close(self):
        super().close()
        
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
                for b in blocks:
                    if "INFRARED SPECTRUM" in b.upper():
                        # it is an infrared spectrum!
                        newSpectrum = spectratypes.infraredSpectrum()
                        print("infrared")
                        
                    elif "RAMAN SPECTRUM" in b.upper():
                        # it is a Raman Spectrum!
                        print("raman")
                        newSpectrum = spectratypes.ramanSpectrum()
                    elif "ULTRAVIOLET SPECTRUM" in b.upper():
                        # it is an UV-VIS spectrum!
                        newSpectrum = spectratypes.ultravioletSpectrum()
                        print("ultraviolet")
                    if newSpectrum.openJCAMPDXfromString(b):
                        if data['open as'] == "document":
                            document = spectivedocument.spectiveDocument()
                            document.addPage("plot")
                            document.pages[-1].addSpectrum(newSpectrum)
                            self._mainWidget.currentChanged.disconnect()
                            self._mainWidget.addTab(document, os.path.basename(data["File Name"]))
                            self.documents.append(document)
                            self.currentDocumentIndex = len(self.documents)-1
                            self.currentPageIndex = len(document.pages) - 1
                            self._mainWidget.setCurrentIndex(self.currentDocumentIndex)
                            self._mainWidget.currentChanged.connect(self.documentChanged)
                        elif data['open as'] == "page":
                            document = self.documents[self.currentDocumentIndex]
                            document.addPage("plot")
                            document.pages[-1].addSpectrum(newSpectrum)
                            self.currentPageIndex = len(document.pages) - 1
                        else:
                            document = self.documents[self.currentDocumentIndex]
                            document.pages[self.currentPageIndex].addSpectrum(newSpectrum)
                        self.currentSpectrumIndex = len(document.pages[self.currentPageIndex].spectra) - 1
                        self.documents[self.currentDocumentIndex].pages[self.currentPageIndex].plotWidget.positionChanged.connect(self.showPositionInStatusBar)
                        self.documents[self.currentDocumentIndex].pages[self.currentPageIndex].plotWidget.plotChanged.connect(self.showPagesInDock)
                        self.showPagesInDock()
                        self.figureAction.setEnabled(True)
                        self.saveAction.setEnabled(True)
                        self.imageSaveAction.setEnabled(True)
                        
    
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
            
    def showMetadataAction(self, show):
        self.metadataAction.setChecked(show)

    def saveFile(self):
        if not self.documents[self.currentDocumentIndex].fileName:
            if self.settings.value("LastSaveDir"):
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", self.settings.value("LastSaveDir"), "JCAMP-DX File (*.dx)")
            else:
                fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        if fileName:
            self.settings.setValue("LastSaveDir", os.path.dirname(fileName))
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.documents[self.currentDocumentIndex].fileName = fileName
            self.documents[self.currentDocumentIndex].saveDocument()
    
    def showFigureDialog(self):
        dgl = figuredialog.figureDialog()
        dgl.setData(self.documents[self.currentDocumentIndex].getFigureData())
        if dgl.exec():
            data = dgl.getData()
            self.documents[self.currentDocumentIndex].setFigureData(data)
    
    def showPagesInDock(self):
        if self.currentDocumentIndex > len(self.documents) or self.currentDocumentIndex < 0:
            return
        self.pageView.clear()
        for page in self.documents[self.currentDocumentIndex].pages:
            newItem = QListWidgetItem(page.plotWidget.getIcon(), page.title)
            self.pageView.addItem(newItem)
    
    def documentChanged(self, index):
        self.currentDocumentIndex = index
        self.showPagesInDock()
    
    def pageChanged(self, index):
        self.currentPageIndex = index
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
        
if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    sys.exit(qapp.exec())
