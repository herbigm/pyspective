#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 07:59:29 2023

@author: marcus
"""

from PyQt6 import QtCore, QtGui
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QWidget,
    QPushButton,
    QFileDialog,
    QComboBox,
    QGroupBox,
    QSpinBox
)
import json
import os.path

class exportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        
        Buttons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(Buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QGridLayout()
        
        self.layout.addWidget(QLabel(self.tr("Resolution: ")), 0,0)
        self.layout.addWidget(QLabel(self.tr("Dots Per Inch (dpi)")), 0,2)
        self.dpiEdit = QSpinBox()
        self.dpiEdit.setMaximum(2400)
        self.dpiEdit.setMinimum(91)
        self.dpiEdit.setValue(300)
        self.layout.addWidget(self.dpiEdit, 0,1)
        
        self.layout.addWidget(self.buttonBox, 3, 0, 1, 3)
        self.setLayout(self.layout)
        
        if self.settings.value("lastExportOptions"): # load old settings if present
            lastExportOptions = self.settings.value("lastExportOptions")
            self.dpiEdit.setValue(lastExportOptions["dpi"])

  
    def getData(self):
        data = {}
        data["dpi"] = self.dpiEdit.value()
        self.settings.setValue("lastExportOptions", data)
        return data