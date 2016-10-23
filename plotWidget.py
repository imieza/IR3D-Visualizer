import matplotlib
import numpy as numpy
from PySide import QtGui
from mayavi import mlab
from tvtk.api import tvtk

from mayavi.sources.vtk_data_source import VTKDataSource


matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4'] = 'PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class PlotWidget(QtGui.QWidget):
    '''Clase para plotear la data obtenida en la clase Data Processing'''

    time_window = 1  # Longitud de cada ventana temporal en ms
    number_of_windows = 256
    cutoff_frequency = 5000
    trucate_value = None

    def __init__(self, parent=None):
        plt.clf()

        super(PlotWidget, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self, data, fs, title, peaks=None):
        self.figure.clear()
        n_window_frames = self.time_window * fs / 1000
        time = numpy.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)
        for channel in range(len(data)):
            ax = self.figure.add_subplot(len(data) * 100 + 11 + channel)
            if peaks is not None:
                window_of_ds = range(peaks[0]-n_window_frames/2, peaks[0]+n_window_frames/2, 1)
                ax.plot(time, data.tolist()[channel], "b-",
                         time[peaks[1:]], data[:, peaks[1:]].tolist()[channel], "g*",
                         time[window_of_ds], data[:, window_of_ds].tolist()[channel], "r")
            else:
                ax.plot(time, data.tolist()[channel])

        plt.subplots_adjust(hspace=1)
        self.canvas.draw()

    def ploter3d(self, i_db, az_el_windows,time,grilla = True):
        from mpl_toolkits.mplot3d import Axes3D

        self.figure.clear()
        mlab.figure(bgcolor=(0, 0, 0), fgcolor=(1, 1, 1))

        # Lo cambio a coordenadas polares
        [x, y, z] = self.sph2cart(az_el_windows[0], az_el_windows[1], i_db)

        # Creo los valores del origen 0,0,0 para todos los vectores
        u = v = w = numpy.zeros(len(x))

        # Grilla
        if grilla:
            surf = mlab.pipeline.surface(self.image_data(), opacity=0)
            mlab.pipeline.surface(mlab.pipeline.extract_edges(surf),
                                  color=(.1, .1, .1), line_width=.001)

        # Grafico los vectores
        obj = mlab.quiver3d(u[0], v[0], w[0], x[0], y[0], z[0], scalars=time[0], scale_mode="vector", mode="2ddash",
                            line_width=10)
        obj = mlab.quiver3d(u[1:], v[1:], w[1:], x[1:], y[1:], z[1:], scalars=time[1:], scale_mode="vector", mode="2ddash",
                            line_width=2)
        obj.glyph.color_mode = 'color_by_scalar'
        obj.module_manager.scalar_lut_manager.reverse_lut = True

        # Agrego el colorbar, los ejes, y el cuadrado
        mlab.colorbar(obj, orientation="vertical")
        mlab.axes(obj)
        mlab.outline(obj)
        self.canvas.draw()

    def image_data(self):
        data = numpy.random.random((5, 5, 5))
        i = tvtk.ImageData(spacing=(.5, .5, .5), origin=(-1, -1, -1))
        i.point_data.scalars = data.ravel()
        i.point_data.scalars.name = 'scalars'
        i.dimensions = data.shape

        return i

    def axisEqual3D(self, ax):
        extents = numpy.array([getattr(ax, 'get_{}lim'.format(dim))() for dim in 'xyz'])
        sz = extents[:, 1] - extents[:, 0]
        centers = numpy.mean(extents, axis=1)
        maxsize = max(abs(sz))
        r = maxsize / 2
        for ctr, dim in zip(centers, 'xyz'):
            getattr(ax, 'set_{}lim'.format(dim))(ctr - r, ctr + r)

    def plot_spectrogram(self, data, fs):
        self.figure.clear()

        title = ["W Spectrogram", "X Spectrogram", "Y Spectrogram", "Z Spectrogram"]
        NFFT = 2048

        for channel in range(len(data)):
            x = data[channel]
            x = numpy.array(x.tolist()[0])

            for index in range(len(x)):
                if abs(x[index]) < 0.00001:
                    x[index] = 0.00001
                else:
                    x[index] = (x[index])

            self.figure.add_subplot(411 + channel)
            plt.title(title[channel])
            plt.subplots_adjust(hspace=1)
            Pxx, freqs, bins, im = plt.specgram(x, NFFT=NFFT, Fs=fs, noverlap=10)

        self.canvas.draw()

    def plotLowFilteredSignals(self, filterFrequency, filterAmplitudeResponse):

        plt.figure()
        plt.subplot(111)
        plt.semilogx(filterFrequency, 20 * numpy.log10(abs(filterAmplitudeResponse)))
        plt.title('Respuesta en frecuencia de fitro pasa-bajos Butterworth')
        plt.xlabel('Frecuencia [Radianes / segundo]')
        plt.ylabel('Amplitud [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green')  # cutoff frequency
        plt.show()
        self.canvas.draw()

    def sph2cart(self, azimuth, elevation, r):
        x = r * numpy.cos(elevation) * numpy.cos(azimuth)
        y = r * numpy.cos(elevation) * numpy.sin(azimuth)
        z = r * numpy.sin(elevation)
        return x, y, z

