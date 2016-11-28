import sys
from interface import *
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import numpy as np
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

######################################################################
class Mayavi(HasTraits):

    # The scene model.
    scene = Instance(MlabSceneModel, ())

    # The current selection in the engine tree view.
    current_selection = Property


    ######################
    view = View(HSplit(VSplit(
                              Item(name='current_selection',
                                   editor=InstanceEditor(),
                                   enabled_when='current_selection is not None',
                                   style='custom',
                                   springy=True,
                                   show_label=False),
                                   ),
                               Item(name='scene',
                                    editor=SceneEditor(scene_class=MayaviScene),
                                    show_label=False,
                                    resizable=True,
                                    height=500,
                                    width=500),
                        ),
                resizable=True,
                scrollable=True
                )

    def __init__(self, Self, **traits):
        HasTraits.__init__(self, **traits)

        self.generate_data_mayavi(Self)



    def generate_data_mayavi(self,Self):
        e = self.scene

        i_db = Self.calc["normalizado"]
        az_el_windows = Self.calc["az_el_windows"][:, Self.calc["peaks"]]
        time = Self.calc["time"][Self.calc["peaks"]]
        grilla = True


        self.scene.mlab.figure(bgcolor=(0, 0, 0), fgcolor=(1, 1, 1),size=(700,700))

        # Lo cambio a coordenadas polares
        x, y, z = self.sph2cart(az_el_windows[0], az_el_windows[1], i_db)

        # Creo los valores del origen 0,0,0 para todos los vectores
        u = v = w = np.zeros(len(x))

        # Grilla
        if grilla:
            surf = self.scene.mlab.pipeline.surface(self.image_data(), opacity=0)
            obj3 = self.scene.mlab.pipeline.surface(mlab.pipeline.extract_edges(surf),
                                  color=(.1, .1, .1), line_width=.001)

        # Grafico los vectores

        obj1 = self.scene.mlab.quiver3d(u[0], v[0], w[0], x[0], y[0], z[0], scalars=time[0], scale_mode="vector", mode="2ddash",
                      line_width=10)
        obj = self.scene.mlab.quiver3d(u[1:], v[1:], w[1:], x[1:], y[1:], z[1:], scalars=time[1:], scale_mode="vector",
                            mode="2ddash",
                            line_width=2)

        obj.glyph.color_mode = 'color_by_scalar'
        obj.module_manager.vector_lut_manager.reverse_lut = True
        # Agrego el colorbar, los ejes, y el cuadrado
        self.scene.mlab.colorbar(obj, orientation="vertical")
        self.scene.mlab.axes(obj)
        self.scene.mlab.outline(obj)
        self.scene.mlab.show()


    def _selection_change(self, old, new):
        self.trait_property_changed('current_selection', old, new)

    def sph2cart(self, azimuth, elevation, r):
        x = r * np.cos(elevation) * np.cos(azimuth)
        y = r * np.cos(elevation) * np.sin(azimuth)
        z = r * np.sin(elevation)
        return x, y, z

    def image_data(self):
        data = np.random.random((5, 5, 5))
        i = tvtk.ImageData(spacing=(.5, .5, .5), origin=(-1, -1, -1))
        i.point_data.scalars = data.ravel()
        i.point_data.scalars.name = 'scalars'
        i.dimensions = data.shape

        return i





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

        Self.ui.plotSpectrogram.figure.clear()

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

            ax = Self.ui.plotSpectrogram.figure.add_subplot(411 + channel)
            plt.title(title[channel])
            plt.subplots_adjust(hspace=1)
            Pxx, freqs, bins, im = ax.specgram(x, NFFT=NFFT, Fs=fs, noverlap=10)

        Self.ui.plotSpectrogram.draw()

    def plotFilter(self,Self):

        filterFrequency = Self.dataProcceser.filterFrequency
        filterAmplitudeResponse=Self.dataProcceser.filterAmplitudeResponse

        Self.ui.plotFilter.figure = plt.figure()
        Self.ui.plotFilter.figure.add_subplot(111)
        plt.semilogx(filterFrequency, 20 * np.log10(abs(filterAmplitudeResponse)))
        plt.title('Respuesta en frecuencia de fitro pasa-bajos Butterworth')
        plt.xlabel('Frecuencia [Radianes / segundo]')
        plt.ylabel('Amplitud [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green')  # cutoff frequency
        plt.draw()


    def plotIR3D(self,Self):
        m = Mayavi(Self)

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
        Self.ui.progressBar.setValue(100)
        self.plotIR3D(Self)


