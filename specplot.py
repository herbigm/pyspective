#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 15:12:04 2023

@author: marcus
"""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtCore import pyqtSignal

import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle

import numpy as np

class specplot(FigureCanvas):
    #Signals
    positionChanged = pyqtSignal(float, float)
    
    def __init__(self, parent = None):        
        self.parent = parent
        self.figure = Figure(figsize=(10, 6), dpi=100, layout="constrained")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.canvas.figure.subplots()
        super(specplot, self).__init__(self.figure)
        self.fullXlim = [0,0]
        self.fullYlim = [0,0]
        
        # events
        self.plotMouseMove = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.plotScrollEvent = self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.plotKeyDown = self.canvas.mpl_connect('button_press_event', self.on_button_down)
        self.plotKeyUp = self.canvas.mpl_connect('button_release_event', self.on_button_up)
        
        # variables used in event handling
        self.zoomXButtonStart = None # where was the first click for the X-Zoom
        self.zoomrect = None # holds the rect of the zoom region (pale blue region on zooming)
        
        self.spectraData = []
        self.spectraLines = []
        self.currentSpectrumIndex = None
        
        self.fileName = None
        self.supTitle = ""
    
    ## Event handling
    
    def on_mouse_move(self, event):
        """
        If the mouse is inside the matplotlib canvas: show the position in spectrum coordinates in the statusbar
        """
        if not event.inaxes:
            return
        self.positionChanged.emit(round(event.xdata, 2), round(event.ydata, 2))
        if self.zoomXButtonStart:
            self.zoomrect.set(width=event.xdata- self.zoomXButtonStart)
            self.ax.figure.canvas.draw_idle() # self.canvas cannot be accessed properly, so got this way to use it
    
    def on_scroll(self, event):
        """
        Scrolling inside matplotlib canvas is used for zooming vertically
        """
        if not event.inaxes:
            return
        yZoomUnit = np.abs(self.fullYlim[1] - self.fullYlim[0]) / 10
        currentYpos = event.ydata
        currentYmin, currentYmax = self.ax.get_ylim()
        currentRange = currentYmax - currentYmin
        
        if event.button == "up":
            # zoom in
            if currentRange <= yZoomUnit:
                return
            newRange = currentRange - yZoomUnit
            newYmax = currentYpos + ((currentYmax - currentYpos) / currentRange * newRange)
            newYmin = currentYpos - ((currentYpos - currentYmin) / currentRange * newRange)
            self.ax.set_ylim(newYmin, newYmax)
            self.ax.figure.canvas.draw_idle()
        else:
            # zoom out
            if currentRange >= 10 * yZoomUnit:
                return
            newRange = currentRange + yZoomUnit
            newYmax = currentYpos + ((currentYmax - currentYpos) / currentRange * newRange)
            if newYmax > self.fullYlim[1]:
                currentYpos -= newYmax - self.fullYlim[1]
                newYmax = self.fullYlim[1]
            newYmin = currentYpos - ((currentYpos - currentYmin) / currentRange * newRange)
            if newYmin < self.fullYlim[0]:
                newYmin = self.fullYlim[0]
                newYmax = newYmin + newRange
            self.ax.set_ylim(newYmin, newYmax)
            self.ax.figure.canvas.draw_idle()
    
    def on_button_down(self, event):
        """
        What to do if the user clicks into the matplotlib-canvas:
            Button1 (left) and double-Click -> reset zoom
            Button 1 (left) simple click -> start zoom region and print it into matplotlib-canvas

        """
        if not event.inaxes:
            return
        if event.button == 1 and event.dblclick: # double click resets the x zoom
            # reset to full spectrum
            self.ax.set_xlim(self.fullXlim)
            self.zoomXButtonStart = None
            if self.zoomrect:
                self.zoomrect.remove()
                self.zoomrect = None
            self.ax.figure.canvas.draw_idle()
        elif event.button == 1: # start the x zooming
            self.zoomXButtonStart = event.xdata
            self.zoomrect = self.ax.add_patch(Rectangle((self.zoomXButtonStart, self.fullYlim[0]), 0, (self.fullYlim[1]-self.fullYlim[0]), alpha=0.2, color="red"))
            self.ax.figure.canvas.draw_idle()
        
    def on_button_up(self, event):
        """
        What to do, if the mouse button is released:
            if it was on the same poit as the button_down-event -> reset zoom-rect to nothing
            if it was an another point: zomm into region by setting xlim and remove zoomrect to nothing

        """
        if not event.inaxes:
            return
        if event.button == 1 and self.zoomXButtonStart == event.xdata: # start and stop at the same position -> do nothing but reset
            self.zoomXButtonStart = None
            self.zoomrect.remove()
            self.zoomrect = None
            self.ax.figure.canvas.draw_idle()
        elif event.button == 1 and self.zoomXButtonStart != None and self.zoomXButtonStart != event.xdata: # stop position other than start position -> do the zoom
            # be carefull with the right range for the x-axis. the use can define the zoom region from up to down and the other way round....
            if (self.fullXlim[0] > self.fullXlim[1] and self.zoomXButtonStart > event.xdata) or (self.fullXlim[0] < self.fullXlim[1] and self.zoomXButtonStart < event.xdata):
                self.ax.set_xlim(self.zoomXButtonStart, event.xdata)
            elif (self.fullXlim[0] > self.fullXlim[1] and self.zoomXButtonStart < event.xdata) or (self.fullXlim[0] < self.fullXlim[1] and self.zoomXButtonStart > event.xdata):
                self.ax.set_xlim(event.xdata, self.zoomXButtonStart)
            self.zoomXButtonStart = None
            self.zoomrect.remove()
            self.zoomrect = None
            self.ax.figure.canvas.draw_idle()
    
    def addSpectrum(self, spec):
        self.spectraData.append(spec)
        (l,) = self.ax.plot(spec.x, spec.y)
        self.spectraLines.append(l)
        if len(self.spectraData) == 1:
            self.ax.set_xlim(self.spectraData[0].xlim)
            self.ax.set_ylim(self.spectraData[0].ylim)
            self.ax.set_xlabel(self.spectraData[0].xlabel)
            self.ax.set_ylabel(self.spectraData[0].ylabel)
            # save the xlim and ylim of the plot
            self.fullXlim = self.spectraData[0].xlim
            self.fullYlim = self.spectraData[0].ylim
        else:
            # check if the xlim and ylim are still the maximum of all spectra
            if spec.xlim[0] < spec.xlim[1]: # from lower to upperon the x axis
                if spec.xlim[0] < self.fullXlim[0]:
                    self.fullXlim[0] = spec.xlim[0]
                if spec.xlim[1] > self.fullXlim[1]:
                    self.fullXlim[1] = spec.xlim[1]
            else: # from upper to lower on x axis (e. g. IR and Raman)
                if spec.xlim[0] > self.fullXlim[0]:
                    self.fullXlim[0] = spec.xlim[0]
                if spec.xlim[1] < self.fullXlim[1]:
                    self.fullXlim[1] = spec.xlim[1]
            if spec.ylim[0] < self.fullYlim[0]:
                self.fullYlim[0] = spec.ylim[0]
            if spec.ylim[1] > self.fullYlim[1]:
                self.fullYlim[1] = spec.ylim[1]
        self.ax.figure.canvas.draw_idle()
    
    def saveSpectra(self):
        if len(self.spectraData) > 1:
            # multiple spectra file
            pass
        else:
            content = self.spectraData[0].getAsJCAMPDX()
            with open(self.fileName, "w") as f:
                f.write(content)
    
    def getFigureData(self):
        data = {}
        data["XLabel"] = self.ax.get_xlabel()
        data["YLabel"] = self.ax.get_ylabel()
        data["XUnit"] = self.spectraData[0].metadata["Spectral Parameters"]["X Units"] # ToDo: Other than the first Spectrum!
        data["YUnit"] = self.spectraData[0].metadata["Spectral Parameters"]["Y Units"]
        data["Xlim"] = self.ax.get_xlim()
        data["Ylim"] = self.ax.get_ylim()
        data["Title"] = self.supTitle
        return data
    
    def setFigureData(self, data):
        if data["XUnit"] != self.spectraData[0].metadata["Spectral Parameters"]["X Units"]:
            if data["XUnit"] == "NANOMETERS":
                if self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "1/CM":
                    self.spectraData[0].x = 1e7 / np.array(self.spectraData[0].x)
                    self.fullXlim[0] = 1e7 / self.fullXlim[0]
                    self.fullXlim[1] = 1e7 / self.fullXlim[1]
                elif self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "MICROMETERS":
                    self.spectraData[0].x = np.array(self.spectraData[0].x) * 1e3
                    self.fullXlim[0] *= 1e3
                    self.fullXlim[1] *= 1e3
            elif data["XUnit"] == "MICROMETERS":
                if self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "1/CM":
                    self.spectraData[0].x = 1e4 / np.array(self.spectraData[0].x)
                    self.fullXlim[0] = 1e4 / self.fullXlim[0]
                    self.fullXlim[1] = 1e4 / self.fullXlim[1]
                elif self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "NANOMETERS":
                    self.spectraData[0].x = np.array(self.spectraData[0].x) * 1e-3
                    self.fullXlim[0] *= 1e-3
                    self.fullXlim[1] *= 1e-3
            elif data["XUnit"] == "1/CM":
                if self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "MICROMETERS":
                    self.spectraData[0].x = 1e4 / np.array(self.spectraData[0].x)
                    self.fullXlim[0] = 1e4 / self.fullXlim[0]
                    self.fullXlim[1] = 1e4 / self.fullXlim[1]
                elif self.spectraData[0].metadata["Spectral Parameters"]["X Units"] == "NANOMETERS":
                    self.spectraData[0].x = 1e7 / np.array(self.spectraData[0].x)
                    self.fullXlim[0] = 1e7 / self.fullXlim[0]
                    self.fullXlim[1] = 1e7 / self.fullXlim[1]
            self.spectraData[0].metadata["Spectral Parameters"]["X Units"] = data["XUnit"]
            self.spectraLines[0].set_xdata(self.spectraData[0].x)
        
        if data["invertX"]:
            self.fullXlim[0], self.fullXlim[1] = self.fullXlim[1], self.fullXlim[0]

        if data["YUnit"] != self.spectraData[0].metadata["Spectral Parameters"]["Y Units"]:
            if data["YUnit"] == "TRANSMITTANCE":
                if self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "REFLECTANCE":
                    pass
                elif self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "ABSORBANCE":
                    self.spectraData[0].y = 10 ** -(np.array(self.spectraData[0].y))*100
                    low, up = self.fullYlim
                    self.fullYlim[0] = 10 ** -(up)*100
                    self.fullYlim[1] = 10 ** -(low)*100
            elif data["YUnit"] == "REFLECTANCE":
                if self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "TRANSMITTANCE":
                    pass
                elif self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "ABSORBANCE":
                    self.spectraData[0].y = 10 ** -(np.array(self.spectraData[0].y))*100
                    low, up = self.fullYlim
                    self.fullYlim[0] = 10 ** -(up)*100
                    self.fullYlim[1] = 10 ** -(low)*100
            elif data["YUnit"] == "ABSORBANCE":
                if self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "TRANSMITTANCE":
                    self.spectraData[0].y = -np.log10(np.array(self.spectraData[0].y)/100)
                    low, up = self.fullYlim
                    self.fullYlim[0] = -np.log10(up/100)
                    self.fullYlim[1] = -np.log10(low/100)
                elif self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] == "REFECTANCE":
                    self.spectraData[0].y = -np.log10(np.array(self.spectraData[0].y)/100)
                    low, up = self.fullYlim
                    self.fullYlim[0] = -np.log10(up/100)
                    self.fullYlim[1] = -np.log10(low/100)
            self.spectraData[0].metadata["Spectral Parameters"]["Y Units"] = data["YUnit"]
            self.spectraLines[0].set_ydata(self.spectraData[0].y)
        
        self.ax.set_xlabel(data["XLabel"])
        self.ax.set_ylabel(data["YLabel"])
        self.ax.set_xlim(data["Xlim"])
        self.ax.set_ylim(data["Ylim"])
        self.ax.figure.suptitle(data["Title"])
        self.ax.figure.canvas.draw_idle()
            
