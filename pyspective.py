#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:46:12 2023

@author: marcus
"""

import sys, os

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QToolBar,
    QMenu,
    QFileDialog
)


import specplot
import spectrum
import spectratypes
import opendialog
import metadatadialog
import exportdialog

class ApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pyspective")
        self._mainWidget = QTabWidget(self)
        self.setCentralWidget(self._mainWidget)
        self.createActions()
        self.createMenuBar()
        self.createMainWidgets()
        
        self.tabWidgets = []
        
        # settings
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("geometry"):
            self.restoreGeometry(self.settings.value("geometry"))
        if self.settings.value("state"):
            self.restoreState(self.settings.value("state"))
    
    def closeEvent(self, evt):
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
    def createMainWidgets(self):
        # create Toolbar and Statusbar
        self.toolBar = self.addToolBar('Main')
        self.toolBar.setObjectName("MainToolBar")
        self.toolBarTabWidget = QTabWidget(self.toolBar)
        self.toolBarTabWidget.setFixedHeight(100)
        self.toolBar.addWidget(self.toolBarTabWidget)
        self.statusBar = self.statusBar()
        
    def createActions(self):
        self.closeAction = QAction(self.tr('Quit'))
        self.closeAction.setIcon(QIcon.fromTheme("application-exit", QIcon("icons/application-exit.avg")))
        self.closeAction.triggered.connect(self.close)
        self.openNew = QAction(self.tr('Open Spectrum'))
        self.openNew.setIcon(QIcon.fromTheme("document-open", QIcon("icons/document-open.svg")))
        self.openNew.triggered.connect(lambda: self.openFile())
        self.imageSaveAction = QAction(self.tr('SExport Current View to Image File'))
        self.imageSaveAction.setIcon(QIcon.fromTheme("image-png", QIcon("icons/image-png.svg")))
        self.imageSaveAction.triggered.connect(self.saveImage)
        self.metadataAction = QAction(self.tr('Show and Edit Metadata'))
        self.metadataAction.triggered.connect(self.showMetadata)
        self.saveAction = QAction(self.tr('&Save File as JCAMP-DX'))
        self.saveAction.setIcon(QIcon.fromTheme("document-save", QIcon("icons/document-save.svg")))
        self.saveAction.setShortcut(QKeySequence("Ctrl+S"))
        self.saveAction.setEnabled(False)
        self.saveAction.triggered.connect(self.saveFile)
        
    def createMenuBar(self):
        self.menuBar = self.menuBar()
        self.fileMenu = QMenu(self.tr("&File"), self.menuBar)
        self.spectrumMenu = QMenu(self.tr("&Spectrum"), self.menuBar)
        
        # create file menu
        self.fileMenu.addAction(self.openNew)
        self.fileMenu.addAction(self.imageSaveAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeAction)
        
        # create spectrum menu
        self.spectrumMenu.addAction(self.metadataAction)
        
        self.menuBar.addMenu(self.fileMenu)
        self.menuBar.addMenu(self.spectrumMenu)
    
    def close(self):
        super().close()
        
    def openFile(self):
        dgl = opendialog.openDialog(self)
        if dgl.exec():
            data = dgl.getData()
            if not os.path.exists(data["File Name"]):
                return
            self.settings.setValue("lastOpenDir", os.path.dirname(data["File Name"]))
            if data["File Type"] == "Any Text Format":
                if data["Free Text Settings"]["Spectrum Type"] == "Raman":
                    newSpectrum = spectratypes.ramanSpectrum()
                    if newSpectrum.openFreeText(fileName=data["File Name"], options=data["Free Text Settings"]):
                        c = specplot.specplot()
                        c.addSpectrum(newSpectrum)
                        self._mainWidget.addTab(c, os.path.basename(data["File Name"]))
                        self.tabWidgets.append(c)
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
                        c = specplot.specplot()
                        c.addSpectrum(newSpectrum)
                        self._mainWidget.addTab(c, os.path.basename(data["File Name"]))
                        self.tabWidgets.append(c)
                        self.saveAction.setEnabled(True)
                        
    
    def saveImage(self):
        dgl = exportdialog.exportDialog()
        if dgl.exec():
            data = dgl.getData()
            fileName, fileTypeFilter = QFileDialog.getSaveFileName(self, "Export Current View", QDir.homePath(), self.tr("Portable Network Graphic (*.png);;Portable Document Format (*.pdf);;Scalable Vector Graphics (*.svg);; Encapsulated PostScript (*.eps);;Tagged Image File Format (*.tif)"))
            if fileName:
                w = self._mainWidget.currentWidget()
                w.figure.savefig(fileName, dpi=data["dpi"])
    
    def showPositionInStatusBar(self, x, y):
        self.statusBar.showMessage(f"Position: {x}, {y}")
    
    def showMetadata(self):
        dgl = metadatadialog.metadataDialog(self)
        if dgl.exec():
            pass
        self.settings.setValue("MetadataDialogGeometry", dgl.saveGeometry())

    def saveFile(self):
        if not self.tabWidgets[-1].fileName:
            fileName, _ = QFileDialog.getSaveFileName(self, "Save File", QDir.homePath(), "JCAMP-DX File (*.dx)")
        if fileName:
            if not fileName.endswith(".dx"):
                fileName += ".dx"
            self.tabWidgets[-1].fileName = fileName
            self.tabWidgets[-1].saveSpectra()
        
if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    sys.exit(qapp.exec())