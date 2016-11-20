import sys
from interface import *
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import numpy as np
from mayavi import mlab
from tvtk.api import tvtk

class PlotWidget():
    time_window = 1  # Longitud de cada ventana temporal en ms
    number_of_windows = 256
    cutoff_frequency = 5000
    trucate_value = None


    def ploterOriginal(self,Self):
        data = Self.calc["data"]
        fs = Self.calc["fs"]
        peaks = None

        Self.ui.plotPressure.figure = plt.figure()
        theFigure = Self.ui.plotPressure.figure
        theFigure.clear()
        n_window_frames = self.time_window * fs / 1000
        time = np.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)
        for channel in range(len(data)):
            ax1f1 = Self.ui.plotPressure.figure.add_subplot(len(data) * 100 + 11 + channel)
            if peaks is not None:
                window_of_ds = range(peaks[0] - n_window_frames / 2, peaks[0] + n_window_frames / 2, 1)
                ax1f1.plot(time, data.tolist()[channel], "b-",
                        time[peaks[1:]], data[:, peaks[1:]].tolist()[channel], "g*",
                        time[window_of_ds], data[:, window_of_ds].tolist()[channel], "r")
            else:
                ax1f1.plot(time, data.tolist()[channel])
        plt.subplots_adjust(hspace=1)

    def ploterReflections(self,Self):
        data = Self.calc["data"]
        fs = Self.calc["fs"]
        peaks = Self.calc["peaks"]

        Self.ui.plotPressure.figure = plt.figure()
        Self.ui.plotPressure.figure.clear()

        n_window_frames = self.time_window * fs / 1000
        time = np.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)
        for channel in range(len(data)):
            ax1f1 = Self.ui.plotPressure.figure.add_subplot(len(data) * 100 + 11 + channel)
            if peaks is not None:
                window_of_ds = range(peaks[0] - n_window_frames / 2, peaks[0] + n_window_frames / 2, 1)
                ax1f1.plot(time, data.tolist()[channel], "b-",
                        time[peaks[1:]], data[:, peaks[1:]].tolist()[channel], "g*",
                        time[window_of_ds], data[:, window_of_ds].tolist()[channel], "r")
            else:
                ax1f1.plot(time, data.tolist()[channel])
        plt.subplots_adjust(hspace=1)

    def plot_spectrogram(self, Self):
        data = Self.calc["data"]
        fs = Self.calc["fs"]

        Self.ui.plotSpectrogram.figure = plt.figure()
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

            Self.ui.plotSpectrogram.figure.add_subplot(411 + channel)
            plt.title(title[channel])
            plt.subplots_adjust(hspace=1)
            Pxx, freqs, bins, im = plt.specgram(x, NFFT=NFFT, Fs=fs, noverlap=10)

    def plot3D(self,Self):
        i_db = Self.calc["normalizado"]
        az_el_windows = Self.calc["az_el_windows"][:, Self.calc["peaks"]]
        time = Self.calc["time"][Self.calc["peaks"]]
        grilla = True
        print

        mlab.figure(bgcolor=(0, 0, 0), fgcolor=(1, 1, 1))

        # Lo cambio a coordenadas polares
        print az_el_windows
        print "======"
        print i_db
        x, y, z = self.sph2cart(az_el_windows[0], az_el_windows[1], i_db)

        # Creo los valores del origen 0,0,0 para todos los vectores
        u = v = w = np.zeros(len(x))

        # Grilla
        if grilla:
            surf = mlab.pipeline.surface(self.image_data(), opacity=0)
            mlab.pipeline.surface(mlab.pipeline.extract_edges(surf),
                                  color=(.1, .1, .1), line_width=.001)

        # Grafico los vectores
        mlab.quiver3d(u[0], v[0], w[0], x[0], y[0], z[0], scalars=time[0], scale_mode="vector", mode="2ddash",
                            line_width=10)
        obj = mlab.quiver3d(u[1:], v[1:], w[1:], x[1:], y[1:], z[1:], scalars=time[1:], scale_mode="vector", mode="2ddash",
                            line_width=2)
        obj.glyph.color_mode = 'color_by_scalar'
        obj.module_manager.scalar_lut_manager.reverse_lut = True

        # Agrego el colorbar, los ejes, y el cuadrado
        mlab.colorbar(obj, orientation="vertical")
        mlab.axes(obj)
        mlab.outline(obj)


        # Agrego el colorbar, los ejes, y el cuadrado
        mlab.colorbar(obj, orientation="vertical")
        mlab.axes(obj)
        mlab.outline(obj)

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

    def ploter(self,Self):
        self.ploterOriginal(Self)
        "self.plot_spectrogram(Self)"
        self.plot3D(Self)