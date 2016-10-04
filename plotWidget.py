import matplotlib
import numpy as numpy
from PySide import QtGui

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
        time = numpy.arange(0.0, float(len(data.tolist()[0])) / fs, 1.0 / fs)
        for channel in range(len(data)):
            ax = self.figure.add_subplot(len(data) * 100 + 11 + channel)
            if peaks is not None:
                ax.plot(time, data.tolist()[channel], "b-", time[peaks], data[:, peaks].tolist()[channel], "r*")
            else:
                ax.plot(time, data.tolist()[channel])

        plt.subplots_adjust(hspace=1)
        self.canvas.draw()

    def ploter3d(self, i_db, az_el_windows):
        from mpl_toolkits.mplot3d import Axes3D

        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='3d')
        self.figure._set_dpi(80)

        [x, y, z] = self.sph2cart(az_el_windows[0], az_el_windows[1], i_db)
        colors_of_red = 20
        color = iter(plt.cm.Spectral(numpy.linspace(0.2, 1, len(x) + colors_of_red)))
        for i in range(1, len(x)):
            c = next(color)
            ax.plot([0, x[i]], [0, y[i]], [0, z[i]], marker="_", c=c, linewidth=1.5)
        ax.plot([0, x[0]], [0, y[0]], [0, z[0]], marker="_", c='r', linewidth=5.0)
        self.axisEqual3D(ax)
        self.canvas.draw()

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
        self.figure.clear()
        self.figure.add_subplot(111)
        plt.semilogx(filterFrequency, 20 * numpy.log10(abs(filterAmplitudeResponse)))
        plt.title('Butterworth filter frequency response')
        plt.xlabel('Frequency [radians / second]')
        plt.ylabel('Amplitude [dB]')
        plt.margins(0, 0.1)
        plt.grid(which='both', axis='both')
        plt.axvline(100, color='green')  # cutoff frequency

        self.canvas.draw()

    def sph2cart(self, azimuth, elevation, r):
        x = r * numpy.cos(elevation) * numpy.cos(azimuth)
        y = r * numpy.cos(elevation) * numpy.sin(azimuth)
        z = r * numpy.sin(elevation)
        return x, y, z

