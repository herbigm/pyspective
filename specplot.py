#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 15:12:04 2023

@author: marcus
"""

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QImage, QPixmap, QIcon

import matplotlib
matplotlib.use('QtAgg')

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import Rectangle, Polygon

import numpy as np
import json

class specplot(FigureCanvas):
    #Signals
    positionChanged = pyqtSignal(float, float)
    plotChanged = pyqtSignal()
    gotIntegrationRange = pyqtSignal(float, float)
    
    def __init__(self, parent = None):        
        self.parent = parent
        self.figure = Figure(figsize=(10, 6), dpi=100, layout="constrained")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.canvas.figure.subplots()
        super(specplot, self).__init__(self.figure)
        self.figureData = None
        self.selectionMode = "ZoomMode"
        
        self.settings = QtCore.QSettings('TUBAF', 'pySpective')
        if self.settings.value("XRFElementLines"):
            self.ElementLines = self.settings.value("XRFElementLines")
        else:
            self.ElementLines = json.load(open("ElementLines.json"))
            self.settings.setValue("XRFElementLines", self.ElementLines)
        
        # events
        self.plotMouseMove = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.plotScrollEvent = self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.plotKeyDown = self.canvas.mpl_connect('button_press_event', self.on_button_down)
        self.plotKeyUp = self.canvas.mpl_connect('button_release_event', self.on_button_up)
        
        # variables used in event handling -> Zooming
        self.zoomXButtonStart = None # where was the first click for the X-Zoom
        self.zoomrect = None # holds the rect of the zoom region (pale blue region on zooming)
        
        # variables used in event handling -> Integration
        self.integralXButtonStart = None # where was the first click for the integration range
        self.integralrect = None # holds the rect of the integration region (pale green)
        
        self.fileName = None
        self.page = None
    
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
        elif self.integralXButtonStart:
            self.integralrect.set(width=event.xdata- self.integralXButtonStart)
            self.ax.figure.canvas.draw_idle() # self.canvas cannot be accessed properly, so got this way to use it
    
    def on_scroll(self, event):
        """
        Scrolling inside matplotlib canvas is used for zooming vertically
        """
        if not event.inaxes:
            return
        yZoomUnit = np.abs(self.figureData['fullYLim'][1] - self.figureData['fullYLim'][0]) / 10
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
            self.figureData['YLim'] = [newYmin, newYmax]
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
        else:
            # zoom out
            if currentRange >= 10 * yZoomUnit:
                return
            newRange = currentRange + yZoomUnit
            newYmax = currentYpos + ((currentYmax - currentYpos) / currentRange * newRange)
            if newYmax > self.figureData['fullYLim'][1]:
                currentYpos -= newYmax - self.figureData['fullYLim'][1]
                newYmax = self.figureData['fullYLim'][1]
            newYmin = currentYpos - ((currentYpos - currentYmin) / currentRange * newRange)
            if newYmin < self.figureData['fullYLim'][0]:
                newYmin = self.figureData['fullYLim'][0]
                newYmax = newYmin + newRange
            self.ax.set_ylim(newYmin, newYmax)
            self.figureData['YLim'] = [newYmin, newYmax]
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
    
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
            self.ax.set_xlim(self.figureData['fullXLim'])
            self.figureData['XLim'] = self.figureData['fullXLim']
            self.zoomXButtonStart = None
            if self.zoomrect:
                self.zoomrect.remove()
                self.zoomrect = None
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
        elif event.button == 1: # start the x zooming or integration
            if self.selectionMode == "ZoomMode":
                self.zoomXButtonStart = event.xdata
                self.zoomrect = self.ax.add_patch(Rectangle((self.zoomXButtonStart, self.figureData['fullYLim'][0]), 0, (self.figureData['fullYLim'][1]-self.figureData['fullYLim'][0]), alpha=0.2, color="red"))
            elif self.selectionMode == "IntegrationMode":
                self.integralXButtonStart = event.xdata
                self.integralrect = self.ax.add_patch(Rectangle((self.integralXButtonStart, self.figureData['fullYLim'][0]), 0, (self.figureData['fullYLim'][1]-self.figureData['fullYLim'][0]), alpha=0.2, color="green"))
            self.ax.figure.canvas.draw_idle()
        
    def on_button_up(self, event):
        """
        What to do, if the mouse button is released:
            if it was on the same poit as the button_down-event -> reset zoom-rect to nothing
            if it was an another point: zomm into region by setting xlim and remove zoomrect to nothing

        """
        if not event.inaxes:
            self.zoomXButtonStart = None
            self.zoomrect.remove()
            self.zoomrect = None
            self.ax.figure.canvas.draw_idle()
        elif event.button == 1 and self.zoomXButtonStart == event.xdata : # start and stop at the same position -> do nothing but reset
            self.zoomXButtonStart = None
            self.zoomrect.remove()
            self.zoomrect = None
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
        elif event.button == 1 and self.integralXButtonStart == event.xdata : # start and stop at the same position -> do nothing but reset
            self.integralXButtonStart = None
            self.integralrect.remove()
            self.integralrect = None
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
        elif event.button == 1 and self.zoomXButtonStart != None and self.zoomXButtonStart != event.xdata: # stop position other than start position -> do the zoom
            # be carefull with the right range for the x-axis. the use can define the zoom region from up to down and the other way round....
            if (self.figureData['fullXLim'][0] > self.figureData['fullXLim'][1] and self.zoomXButtonStart > event.xdata) or (self.figureData['fullXLim'][0] < self.figureData['fullXLim'][1] and self.zoomXButtonStart < event.xdata):
                self.ax.set_xlim(self.zoomXButtonStart, event.xdata)
                self.figureData['XLim'] = [self.zoomXButtonStart, event.xdata]
            elif (self.figureData['fullXLim'][0] > self.figureData['fullXLim'][1] and self.zoomXButtonStart < event.xdata) or (self.figureData['fullXLim'][0] < self.figureData['fullXLim'][1] and self.zoomXButtonStart > event.xdata):
                self.ax.set_xlim(event.xdata, self.zoomXButtonStart)
                self.figureData['XLim'] = [event.xdata, self.zoomXButtonStart]
            self.zoomXButtonStart = None
            self.zoomrect.remove()
            self.zoomrect = None
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
        elif event.button == 1 and self.integralXButtonStart != None and self.integralXButtonStart != event.xdata: # stop position other than start position -> do the integration
            self.gotIntegrationRange.emit(self.integralXButtonStart, event.xdata)
            self.integralXButtonStart = None
            self.integralrect.remove()
            self.integralrect = None
            self.ax.figure.canvas.draw()
            self.plotChanged.emit()
    
    def getIcon(self):
        self.canvas.draw()
        width, height = self.figure.figbbox.width, self.figure.figbbox.height
        im = QImage(self.figure.canvas.buffer_rgba(), int(width), int(height), QImage.Format.Format_RGBA8888)
        return QIcon(QPixmap(im))
    
    def updatePlot(self):
        self.ax.figure.clear()
        if hasattr(self, 'ax2'):
            del self.ax2
        self.ax = self.canvas.figure.subplots()
        for spec in self.page.spectra:
            if spec.color == '':
                spec.color = "#0064a8"
            if spec.yaxis > 0:
                if not hasattr(self, 'ax2'):
                    self.ax2 = self.ax.twinx()
                    self.ax2.set_ylabel("derivative")
                self.ax2.plot(spec.x, spec.y, spec.markerStyle + spec.lineStyle, color=spec.color, label=spec.title)
                if len(spec.peaks) > 0:
                    self.ax2.plot(spec.x[spec.peaks], spec.y[spec.peaks], "+", color=spec.peakParameter['Color'], label="_Hidden")
            else:
                self.ax.plot(spec.x, spec.y, spec.markerStyle + spec.lineStyle, color=spec.color, label=spec.title)
                if len(spec.peaks) > 0:
                    self.ax.plot(spec.x[spec.peaks], spec.y[spec.peaks], "+", color=spec.peakParameter['Color'], label="_Hidden")
                for i in spec.integrals:
                    x1, x2 = spec.getIntegrationRangeByIndex(i['x1'], i['x2'])
                    poly = Polygon([*zip(spec.x[x1:x2], spec.y[x1:x2])], color=i['color'])
                    self.ax.add_patch(poly)
            if type(spec).__name__ == 'powderXRD':
                currentYlim = self.ax.get_ylim()
                ymin = currentYlim[0]
                for ref in spec.references:
                    if not ref['Display'] or ref['Display'] == "do not display":
                        spec.ylim[0] = np.min(spec.y)
                        self.ax.set_ylim(spec.ylim[0], currentYlim[1]) # remove space under the graph if no references are present
                        self.figureData['fullYLim'][0] = spec.ylim[0]
                    elif ref['Display'] == 'display without intenities':
                        if currentYlim[0] >= 0:
                            ymin = -(spec.ylim[1] - spec.ylim[0])/10
                            self.ax.set_ylim(ymin, currentYlim[1])
                            spec.ylim[0] = ymin
                            self.figureData['fullYLim'][0] = ymin
                        self.ax.vlines(ref['x'], ymin, 0, colors=ref['Color'], label=ref['Title'])
                    elif ref['Display'] == 'display with intensity':
                        # dispaly reference with intensity
                        maxY = max(ref['y'])
                        maxIndex = ref['y'].index(maxY)
                        XatMaxY = ref['x'][maxIndex]
                        measuredY = 1
                        # suche nach dem am Messwert möglichst nahe am Theoriewert
                        for idx in range(1, len(spec.x)):
                            if XatMaxY > spec.x[idx - 1] and XatMaxY < spec.x[idx]:
                                m = (spec.y[idx] - spec.y[idx-1])/(spec.x[idx] - spec.x[idx-1])
                                n = -m * spec.x[idx] + spec.y[idx]
                                measuredY = m * XatMaxY + n
                                break
                            elif XatMaxY == spec.x[idx - 1]:
                                measuredY = spec.y[idx - 1]
                                break
                            elif XatMaxY == spec.x[idx]:
                                measuredY = spec.y[idx]
                                break
                            
                        minHeight = 0.1 * np.max(spec.y)
                        if measuredY < minHeight:
                            print("rescaled")
                            measuredY = minHeight
                        # Skalierungsfaktor berechnen
                        factor = measuredY / maxY
                        # Alle Linien skalieren und anzeigen
                        self.ax.vlines(ref['x'], 0, np.array(ref['y']) * factor, colors=ref['Color'], label=ref['Title'])
            elif type(spec).__name__ == 'xrfSpectrum':
                self.ElementLines = self.settings.value("XRFElementLines")
                for ref in spec.references:
                    # get maximum counts at most intens line in spectrum range
                    # lines are sorted in reference list by intensity, so the first line inside the spectrum range is the most intens.
                    maxIntens = 0
                    linesX = []
                    linesYmax = []
                    for line in self.ElementLines[ref]['Lines']:
                        if line['Energy'] < spec.xlim[1] * 1000 and line['Energy'] > spec.xlim[0] * 1000:
                            if line['rel. Intensity'] > maxIntens:
                                maxIntens = line['rel. Intensity']
                                for i in range(1, len(spec.x)):
                                    if spec.x[i-1] * 1000 < line['Energy'] and spec.x[i] * 1000 > line['Energy']:
                                        m = (spec.y[i] - spec.y[i-1])/(spec.x[i] - spec.x[i-1]) / 1000
                                        n = -m * spec.x[i] * 1000 + spec.y[i]
                                        countsAtEnergy = m * line['Energy'] + n
                                        break
                                    elif spec.x[i-1] * 1000 == line['Energy']:
                                        countsAtEnergy = spec.y[i-1]
                                        break
                                    elif spec.x[i] * 1000 == line['Energy']:
                                        countsAtEnergy = spec.y[i]
                                        break
                                if countsAtEnergy < 0.1 * np.max(spec.y):
                                    countsAtEnergy = 0.1 * np.max(spec.y)
                            linesX.append(line['Energy'] / 1000)
                            linesYmax.append(line['rel. Intensity'] * countsAtEnergy / maxIntens)
                    self.ax.vlines(x=linesX, ymin=0, ymax=linesYmax, color=self.ElementLines[ref]['Display Color'], label=ref)

        
        self.ax.set_xlim(self.figureData['XLim'])
        self.ax.set_ylim(self.figureData['YLim'])
        self.ax.set_xlabel(self.figureData['XLabel'])
        self.ax.set_ylabel(self.figureData['YLabel'])
        if self.figureData['PlotTitle'] != "":
            self.ax.figure.suptitle(self.figureData['PlotTitle'])
        if self.figureData['Legend'] != "":
            self.ax.legend(loc=self.figureData['Legend'])
        self.ax.figure.canvas.draw()
        self.plotChanged.emit()
    
    def setPage(self, page):
        self.page = page
        self.figureData = page.figureData
        self.updatePlot()
        
    def saveAsImage(self, fileName, dpi=300):
        self.figure.savefig(fileName, dpi=dpi)
            