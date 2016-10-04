from PySide import QtGui
import sys

from plotWidget import PlotWidget
from dataProcessing import DataProcessing

class MainView(QtGui.QWidget):
    def __init__(self, function=None):
        super(MainView, self).__init__()
        self.setWindowTitle('Impulse response 3D')
        self.setObjectName('MainWidget')
        self.setStyleSheet('QWidget#MainWidget {background-color: rgb(191, 191, 191)}')

        self.function = function
        self.widMatplot = PlotWidget(self.function)
        self.dataProcceser = DataProcessing()

        self._loadSignalsButton = QtGui.QPushButton('Open WAV B-Format File ')
        self.filterFrequencyResponsePlotButton = QtGui.QPushButton('Low-Pass Filtering Response')
        self.spectrogramPlotButton = QtGui.QPushButton('Spectogram')
        self.filterFrequencyResponseWithStarsPlotButton = QtGui.QPushButton('Window Selection')
        self.impulseResponse3DButton = QtGui.QPushButton('View IR3D Graph')

        self._setLayout()

        self.impulseResponse3DButton.clicked.connect(self._plotIR3D)
        self._loadSignalsButton.clicked.connect(self._showLoadSignalsDialog)
        self.spectrogramPlotButton.clicked.connect(self.showSpectogram)
        self.filterFrequencyResponsePlotButton.clicked.connect(self.showLowPassFilteringResponse)
        self.filterFrequencyResponseWithStarsPlotButton.clicked.connect(self.showSignalWithStarts)
        self.show()

        self.audio = None

    def _showLoadSignalsDialog(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(self, ("Open File"), "/home/", ("Wav Files (*.wav)"))

        if fileName[0] != []:
            [self.audio, self.fs] = self.dataProcceser.load_wavefile(fileName[0][0])
            self.audio_filtered = self.dataProcceser.low_filtering(self.audio, self.fs)
            intensity = self.dataProcceser.pressure_to_intensity(self.audio_filtered)
            [self.intensity_windows, self.az_el_windows, self.i_db] = self.dataProcceser.temporal_windowing(intensity,                                                                                         self.fs)
            self.index_of_peaks = self.dataProcceser.window_selector(self.i_db, self.fs)
            self.normalizado = self.dataProcceser.min_vector_be_equal_to_0(self.i_db[0, self.index_of_peaks])
            self.widMatplot.plot(self.audio, self.fs, "Audio")

    def _plotIR3D(self):
        self.widMatplot.ploter3d(self.normalizado, self.az_el_windows[:, self.index_of_peaks])

    def showSpectogram(self):
        self.widMatplot.plot_spectrogram(self.audio, self.fs)

    def showLowPassFilteringResponse(self):
        self.widMatplot.plotLowFilteredSignals(self.dataProcceser.filterFrequency, self.dataProcceser.filterAmplitudeResponse)

    def showSignalWithStarts(self):
        # audio_filtered = self.widMatplot.low_filtering(self.audio, False, self.fs)
        self.widMatplot.plot(self.audio, self.fs, "Audio with windows",self.index_of_peaks)

    def _setLayout(self):
        hLayout = QtGui.QHBoxLayout()

        hLayout.addWidget(self._loadSignalsButton)
        hLayout.addWidget(self.filterFrequencyResponsePlotButton)
        hLayout.addWidget(self.spectrogramPlotButton)
        hLayout.addWidget(self.filterFrequencyResponseWithStarsPlotButton)
        hLayout.addWidget(self.impulseResponse3DButton)

        self.setLayout(QtGui.QGridLayout())
        self.layout().addLayout(hLayout, 0, 0, 1, 1)
        self.layout().addWidget(self.widMatplot, 1, 0, 1, 1)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    main = MainView()
    main.show()
    sys.exit(app.exec_())
