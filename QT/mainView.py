import sys
from interface import *
from PyQt4 import QtGui
import matplotlib.pyplot as plt
import numpy as np
from plotWidget import PlotWidget
from dataProcessing import DataProcessing

class MainView(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.plotWidget = PlotWidget()
        self.dataProcceser = DataProcessing()
        self.openFile()
        self.ui.btnRecalculate.clicked.connect(self.calculate)

    def openFile(self):
        self.fileName = "C:\Users\W\Documents\IR3D\IR3D-Visualizer\Audios de prueba\stpatricks_s2r2.wav"
        "self.calculate()"

    def calculate(self):
        if self.fileName[0] != []:
            self.calc = {}
            [self.calc["data"], self.calc["fs"]] = self.dataProcceser.load_wavefile(self.fileName)
            self.calc["time"] = self.dataProcceser.generate_time(self.calc["fs"], self.calc["data"])
            self.calc["audio_filtered"] = self.dataProcceser.low_filtering(self.calc["data"], self.calc["fs"])
            min_value, max_value = self.dataProcceser.get_min_max(self.calc["audio_filtered"])
            self.calc["audio_filtered_norm"] = np.matrix([self.dataProcceser.normalizer(np.array(self.calc["audio_filtered"][channel, :])[0], min_value, max_value) for channel in range(4)])
            self.calc["intensity"] = self.dataProcceser.pressure_to_intensity(self.calc["audio_filtered"])
            [self.calc["intensity_windows"], self.calc["az_el_windows"], self.calc["i_db"]] = self.dataProcceser.temporal_windowing(self.calc["intensity"], self.calc["fs"])
            self.calc["peaks"] = self.dataProcceser.window_selector(self.calc["i_db"], self.calc["fs"])
            self.calc["normalizado"]= self.dataProcceser.normalizer(self.calc["i_db"][0, self.calc["peaks"]])

            """self.widMatplot.plot(self.audio, self.fs, "Audio")"""
            self.plotWidget.ploter(self)


if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainView()
    myapp.show()
    sys.exit(app.exec_())




