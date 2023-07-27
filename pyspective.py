#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 09:46:12 2023

@author: marcus
"""

import sys, os

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
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
import raman
import opendialog
import metadatadialog

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
        self.imageSaveAction = QAction(self.tr('Save Image of Current View'))
        self.imageSaveAction.setIcon(QIcon.fromTheme("image-png", QIcon("icons/image-png.svg")))
        self.imageSaveAction.triggered.connect(self.saveImage)
        self.metadataAction = QAction(self.tr('Show and Edit Metadata'))
        self.metadataAction.triggered.connect(self.showMetadata)
        
    def createMenuBar(self):
        self.menuBar = self.menuBar()
        self.fileMenu = QMenu(self.tr("&File"), self.menuBar)
        self.spectrumMenu = QMenu(self.tr("&Spectrum"), self.menuBar)
        
        # create file menu
        self.fileMenu.addAction(self.openNew)
        self.fileMenu.addAction(self.imageSaveAction)
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
            if data["File Type"] == "Any Text Format":
                if data["Free Text Settings"]["Spectrum Type"] == "Raman":
                    newSpectrum = raman.ramanSpectrum()
                    if newSpectrum.openFreeText(fileName=data["File Name"], options=data["Free Text Settings"]):
                        c = specplot.specplot()
                        c.addSpectrum(newSpectrum)
                        self._mainWidget.addTab(c, os.path.basename(data["File Name"]))
                        self.tabWidgets.append(c)
                else:
                    pass
            elif data["File Type"] == "JCAMP-DX":
                pass
    
    def saveImage(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Current View as Image", QDir.homePath(), "Portable Network Graphic (*.png)")
        if fileName:
            w = self._mainWidget.currentWidget()
            w.figure.savefig(fileName, dpi=300)
    
    def showPositionInStatusBar(self, x, y):
        self.statusBar.showMessage(f"Position: {x}, {y}")
    
    def showMetadata(self):
        dgl = metadatadialog.metadataDialog(self)
        if dgl.exec():
            pass
        self.settings.setValue("MetadataDialogGeometry", dgl.saveGeometry())

if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    app = ApplicationWindow()
    app.show()
    app.activateWindow()
    app.raise_()
    sys.exit(qapp.exec())
