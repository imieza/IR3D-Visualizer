from __future__ import division
import warnings

warnings.filterwarnings('ignore')
from matplotlib.lines import Line2D
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
import scipy


class PlotWidget():
    mainSelf = None

    def __init__(self,mainSelf):
        self.mainSelf = mainSelf

    def plot1D(self, Self, figureWidget, layoutWidget, data, time, show_peaks=False):
        fs = Self.calc["fs"]
        label = ["P", "X", "Y", "Z"]
        if show_peaks:
            peaks = None
        else:
            peaks = Self.calc["peaks"]
        theFigure = figureWidget.figure
        theFigure.clear()
        n_window_frames = self.mainSelf.parameters["timeWindow"] * fs / 1000
        for channel in range(len(data)):
            ax1f1 = theFigure.add_subplot(len(data) * 100 + 11 + channel, axisbg='black')
            plt.subplots_adjust(hspace=1)
            ax1f1.grid(color='#737373', linestyle='-', linewidth=0.5)

            if peaks is not None:
                window_of_ds = range(int(peaks[0] - n_window_frames / 2), int(peaks[0] + n_window_frames / 2))
                ax1f1.plot(time.tolist(), data.tolist()[channel], "w-")
                ax1f1.plot(time[peaks[1:]], data[:, peaks[1:]].tolist()[channel], "bo")
                ax1f1.plot(time[window_of_ds], data[:, window_of_ds].tolist()[channel], "r")
            else:
                ax1f1.plot(time, data.tolist()[channel])

            ax1f1.set_ylabel(label[channel]+ ": [dB]")

        ax1f1.set_xlabel("Time [seconds]")

        figureWidget.draw()

    def plotSpectrogram(self, Self):
        data = Self.calc["audio_filtered"]
        fs = Self.calc["fs"]
        figureWidget = Self.plotSpectrogram
        figureWidget.figure.clear()

        title = ["W Spectrogram", "X Spectrogram", "Y Spectrogram", "Z Spectrogram"]
        NFFT = 2048
        label = ["P", "X", "Y", "Z"]

        for channel in range(len(data)):
            x = data[channel]
            x = np.array(x.tolist()[0])

            for index in range(len(x)):
                if abs(x[index]) < 0.00001:
                    x[index] = 0.00001
                else:
                    x[index] = (x[index])

            ax = figureWidget.figure.add_subplot(411 + channel,  axisbg='black')
            ax.set_ylabel(label[channel] + ": [Hz]")
            plt.subplots_adjust(hspace=1)
            Pxx, freqs, bins, im = ax.specgram(x, NFFT=NFFT, Fs=fs, noverlap=10)
        ax.set_xlabel("Time [Seconds]")
        figureWidget.draw()

    def plotFilter(self, Self):
        if Self.ui.low_pass_active.isChecked() or Self.ui.hi_pass_active.isChecked():
            filterFrequency = Self.dataProcceser.filterFrequency
            filterAmplitudeResponse = Self.dataProcceser.filterAmplitudeResponse
            figureWidget = Self.plotFilter
            figureWidget.figure.clear()
            ax = figureWidget.figure.add_subplot(111,  axisbg='black')
            ax.semilogx(filterFrequency, 20 * np.log10(abs(filterAmplitudeResponse)), 'w')
            ax.grid(color='#737373', linestyle='-', linewidth=0.5)
            ax.set_xlabel("Frequency [Radians/ seconds]")
            ax.set_ylabel("Level [dB]")
            plt.margins(0, 0.1)
            plt.axvline(100, color='green')  # cutoff frequency
            figureWidget.draw()

    def plotFloorplan(self):
        figureWidget = self.mainSelf.plotFloorplan
        figureWidget.figure.clear()
        ax = figureWidget.figure.add_subplot(111)
        FloorplanImage = plt.imread(self.mainSelf.floorplanFile)
        ax.imshow(FloorplanImage)
        ax.set_xlim(ax.get_xlim())
        ax.set_ylim(ax.get_ylim())
        for num in range(self.mainSelf.ui.listMeasurements.rowCount()):
            if 'location' in self.mainSelf.measurements[num]:
                try:
                    ir3dImage = plt.imread("images/floorplan_" + self.mainSelf.measurements[num]["name"] + ".png")
                    ir3dImage_rotated = scipy.ndimage.rotate(ir3dImage, self.mainSelf.ui.rotationAngle.value())
                    heighImage, widthImage, bpp = np.shape(ir3dImage_rotated)
                    heighImage = heighImage / 2
                    widthImage = widthImage / 2

                    locationX = self.mainSelf.measurements[num]["location"][0]
                    locationY = self.mainSelf.measurements[num]["location"][1]

                    extent = locationX - widthImage, locationX + widthImage, locationY - heighImage, locationY + heighImage

                    ax.imshow(ir3dImage_rotated, extent=extent)
                except (RuntimeError, TypeError, NameError) as err:
                    print err

        figureWidget.draw()

    def fill_data_table(self, Self):
        time = Self.calc["time"][Self.calc["peaks"]]
        [azimuth, elevation] = Self.calc["az_el_windows"][:, Self.calc["peaks"]]
        magnitude = Self.calc["i_db"][Self.calc["peaks"]]
        Self.ui.tableData.clearContents()
        for index in range(len(time)):
            Self.ui.tableData.insertRow(index)
            Self.ui.tableData.setItem(index, 0, QtGui.QTableWidgetItem(str(time[index])))
            Self.ui.tableData.setItem(index, 1, QtGui.QTableWidgetItem(str(magnitude[index]-96)))
            Self.ui.tableData.setItem(index, 2, QtGui.QTableWidgetItem(str(np.math.degrees(azimuth[index]))))
            Self.ui.tableData.setItem(index, 3, QtGui.QTableWidgetItem(str(np.math.degrees(elevation[index]))))

    def export2excel(self):
        def output(filename, time, magnitude, az, el):
            import xlwt
            book = xlwt.Workbook()
            sh = book.add_sheet('Results')

            sh.write(0, 0, 'Time')
            sh.write(0, 1, 'Magnitude')
            sh.write(0, 2, 'Azimuth')
            sh.write(0, 3, 'Elevation')

            for n, (t, m, a, e) in enumerate(zip(time, magnitude, az, el),1):
                sh.write(n, 0, t)
                sh.write(n, 1, m)
                sh.write(n, 2, np.math.degrees(a))
                sh.write(n, 3, np.math.degrees(e))

            book.save(filename)
        if self.mainSelf:
            [azimuth, elevation] = self.mainSelf.calc["az_el_windows"][:,  self.mainSelf.calc["peaks"]]
            output(filename=self.mainSelf.dir_path+'/Results/'+self.mainSelf.calc["name"]+'.xls',
                   time=self.mainSelf.calc["time"][self.mainSelf.calc["peaks"]],
                   magnitude=self.mainSelf.calc["normalizado"],
                   az=azimuth.tolist(), el=elevation.tolist())


    def plotDirectSoundSelection(self):
        figureWidget = self.mainSelf.directSoundSelection
        figureWidget.figure.clear()
        ax = figureWidget.figure.add_subplot(111, axisbg='black', position=[0.16, 0.22, 0.82, .75])
        half_window_length = int(self.mainSelf.parameters["timeWindow"] * self.mainSelf.calc["fs"] / 2000)
        peaks = [range(peak - half_window_length, peak + half_window_length) for peak in
                 self.mainSelf.calc['directSoundSelection_peaks']]  # Make several intervals of DS

        global lines
        lines = []
        selected = self.mainSelf.parameters['directSoundSelection']
        audio = np.array(self.mainSelf.calc['intensity'].tolist()[0])
        time = np.array(self.mainSelf.calc['time'].tolist())
        ax.plot(time, audio, 'w')
        ax.plot(time[peaks[selected]], audio[peaks[selected]], 'r')
        for peak in self.mainSelf.calc['directSoundSelection_peaks']:
            line, = ax.plot(time[peak], audio[peak], '*b', picker=3)
            lines.append(line)
        ax.plot(time[self.mainSelf.calc['directSoundSelection_peaks'][selected]],
                audio[self.mainSelf.calc['directSoundSelection_peaks'][selected]], '*r', linewidth=3)
        ax.set_xlim(time[peaks[0][0]] - .001, time[peaks[-1][-1]] + .001)
        ax.set_ylabel('Level')
        #subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        figureWidget.draw()

    def onpick1(self, event):
        thisline = event.artist
        if isinstance(thisline, Line2D):
            selected = [str(line) for line in lines].index(str(thisline))
            self.mainSelf.parameters['directSoundSelection'] = selected
            self.plotDirectSoundSelection()


    def ploter(self, Self):
        self.plot1D(Self, Self.plotPressure, Self.ui.tabLayoutPressureLevel, Self.calc["audio_filtered"], Self.calc['time'],
                    False)
        Self.ui.progressBar.setValue(55)
        self.plot1D(Self, Self.plotWindowLevel, Self.ui.tabLayoutIntensityLevel, Self.calc["intensity_windows"],
                    Self.calc['time'], False)
        Self.ui.progressBar.setValue(60)
        self.plot1D(Self, Self.plotIntensity, Self.ui.tabLayoutLevel, Self.calc["intensity"], Self.calc['time'],
                    False)
        Self.ui.progressBar.setValue(65)
        self.plotFilter(Self)
        Self.ui.progressBar.setValue(70)
        self.plotSpectrogram(Self)
        Self.ui.progressBar.setValue(80)
        self.fill_data_table(Self)
        self.mainSelf.directSoundSelection.figure.canvas.mpl_connect('pick_event', self.onpick1)
        self.plotDirectSoundSelection()
        Self.mayavi_widget.update_plot(Self)
        Self.ui.progressBar.setValue(100)
