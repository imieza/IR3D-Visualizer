import sys
from interface import *
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image

from mayavi import mlab
from tvtk.api import tvtk

from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)


# Authors: Prabhu Ramachandran <prabhu [at] aero.iitb.ac.in>
# Copyright (c) 2007, Enthought, Inc.
# License: BSD Style.

# Standard imports.
from numpy import sqrt, sin, mgrid

# Enthought imports.
from traits.api import HasTraits, Instance, Property, Enum
from traitsui.api import View, Item, HSplit, VSplit, InstanceEditor
from mayavi.core.ui.engine_view import EngineView

from traits.api import HasTraits, Instance
from traitsui.api import View, Item, ModelView
from tvtk.pyface.scene_editor import SceneEditor
from mayavi.tools.mlab_scene_model import MlabSceneModel
from mayavi.core.ui.mayavi_scene import MayaviScene

# ========================================================

class PlotWidget():
    time_window = 1  # Longitud de cada ventana temporal en ms
    number_of_windows = 256
    cutoff_frequency = 5000
    trucate_value = None


    def plot1D(self,Self,figureWidget,layoutWidget,data,show_peaks=False):

        fs = Self.calc["fs"]

        if show_peaks:
            peaks=None
        else:
            peaks=Self.calc["peaks"]

        #figureWidget.figure = plt.figure()
        theFigure = figureWidget.figure
        theFigure.clear()

        n_window_frames = self.time_window * fs / 1000
        time = np.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)
        for channel in range(len(data)):
            ax1f1 = theFigure.add_subplot(len(data) * 100 + 11 + channel)
            plt.subplots_adjust(hspace=1)

            if peaks is not None:
                window_of_ds = range(peaks[0] - n_window_frames / 2, peaks[0] + n_window_frames / 2, 1)
                ax1f1.plot(time, data.tolist()[channel], "b-",
                        time[peaks[1:]], data[:, peaks[1:]].tolist()[channel], "g*",
                        time[window_of_ds], data[:, window_of_ds].tolist()[channel], "r")
            else:
                ax1f1.plot(time, data.tolist()[channel])

        figureWidget.draw()

    def plotSpectrogram(self, Self):
        data = Self.calc["data"]
        fs = Self.calc["fs"]
        figureWidget = Self.ui.plotSpectrogram
        figureWidget.figure.clear()

        title = ["W Spectrogram", "X Spectrogram", "Y Spectrogram", "Z Spectrogram"]
        NFFT = 2048

        for channel in range(len(data)):
            x = data[channel]
            x = np.array(x.tolist()[0])

            for index in range(len(x)):
                if abs(x[index]) < 0.00001:
                    x[index] = 0.00001
                else:
                    x[index] = (x[index])

            ax = figureWidget.figure.add_subplot(411 + channel)
            plt.title(title[channel])
            plt.subplots_adjust(hspace=1)
            Pxx, freqs, bins, im = ax.specgram(x, NFFT=NFFT, Fs=fs, noverlap=10)

        figureWidget.draw()

    def plotFilter(self,Self):

        filterFrequency = Self.dataProcceser.filterFrequency
        filterAmplitudeResponse=Self.dataProcceser.filterAmplitudeResponse

        figureWidget = Self.ui.plotFilter
        figureWidget.figure.clear()
        ax = figureWidget.figure.add_subplot(111)
        ax.semilogx(filterFrequency, 20 * np.log10(abs(filterAmplitudeResponse)))
        plt.title('Respuesta en frecuencia de fitro pasa-bajos Butterworth')
        plt.xlabel('Frecuencia [Radianes / segundo]')
        plt.ylabel('Amplitud [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green')  # cutoff frequency
        figureWidget.draw()

    def plotFloorplan(self,Self):
        figureWidget = Self.ui.plotFloorplan
        figureWidget.figure.clear()
        ax = figureWidget.figure.add_subplot(111)

        FloorplanImage = plt.imread(Self.floorplanFile)
        ax.imshow(FloorplanImage)
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        for num in range(Self.ui.listMeasurements.rowCount()):
            try:
                Self.measurements[num]["location"]
                [xcenter,ycenter] = Self.measurements[num]["location"]
                size = 100
                extent = xcenter-size, xcenter+size, ycenter-size, ycenter+size
                ir3dImage = plt.imread("images/floorplan_"+Self.measurements[num]["name"]+".png")
                ax.imshow(ir3dImage,extent=extent)
            except:
                pass
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])

        figureWidget.draw()

    def ploter(self,Self):
        self.plot1D(Self,Self.ui.plotPressure,Self.ui.tabLayoutPressureLevel,Self.calc["data"],False)
        Self.ui.progressBar.setValue(55)
        self.plot1D(Self,Self.ui.plotWindowLevel,Self.ui.tabLayoutIntensityLevel,Self.calc["intensity_windows"],False)
        Self.ui.progressBar.setValue(60)
        self.plot1D(Self,Self.ui.plotIntensity,Self.ui.tabLayoutLevel,Self.calc["intensity"],False)
        Self.ui.progressBar.setValue(65)
        self.plotFilter(Self)
        Self.ui.progressBar.setValue(70)
        self.plotSpectrogram(Self)
        Self.ui.progressBar.setValue(80)
        Self.mayavi_widget.update_plot(Self)
        Self.ui.progressBar.setValue(100)




