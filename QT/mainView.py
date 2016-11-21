import sys
from interface import *
from PyQt4.QtGui import *
import matplotlib.pyplot as plt
import numpy as np
from plotWidget import PlotWidget
from dataProcessing import DataProcessing
from datetime import datetime

class MainView(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.plotWidget = PlotWidget()
        self.measurements = []
        self.get_parameters()
        self.dataProcceser = DataProcessing(self)
        self.ui.progressBar.setValue(0)

        self.ui.btnRecalculate.clicked.connect(self.calculate)
        self.ui.btnSelect.clicked.connect(self.selectMeasurement)
        self.ui.btnDelete.clicked.connect(self.delItem)
        self.ui.btnDeleteAll.clicked.connect(self.delAllItems)
        self.connect(self.ui.actionNew_project, QtCore.SIGNAL("triggered()"), self.openFile)

    def openFile(self):
        self.calc = {}
        fileName = QtGui.QFileDialog.getOpenFileNames(None,("Open File"), "/home/", ("Wav Files (*.wav)"))
        #self.fileName = "C:\Users\W\Documents\IR3D\IR3D-Visualizer\Audios de prueba\stpatricks_s2r2.wav"
        self.fileName = fileName[0]
        [self.calc["data"], self.calc["fs"]] = self.dataProcceser.load_wavefile(self.fileName)
        self.calc["time"] = self.dataProcceser.generate_time(self.calc["fs"], self.calc["data"])
        self.ui.audioCutter.setValue(self.calc["time"][len(self.calc["time"])-1]*1000)
        self.calculate()

    def get_parameters(self):
        self.parameters = {}
        self.parameters["value2truncate"] = self.ui.audioCutter.value()
        self.parameters["cutoff_frequency"] = self.ui.lowPassFiltering.value()# 5000
        self.parameters["bandPassFilter"] = None
        self.parameters["timeWindow"] = self.ui.windowingWindowSize.value()
        self.parameters["number_of_windows"] = self.ui.windowingQuantity.value()
        self.parameters["boundedExtended"] = None

    def addList(self):
        rowPosition = self.ui.listMeasurements.rowCount()
        self.ui.listMeasurements.insertRow(rowPosition)
        self.ui.listMeasurements.setItem(rowPosition, 0, QtGui.QTableWidgetItem("Nameless"))
        self.ui.listMeasurements.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(datetime.now())[:19 ]))
        self.ui.listMeasurements.setItem(rowPosition, 2, QtGui.QTableWidgetItem(str(self.fileName)))
        self.measurements.append(dict(self.calc))

    def delItem(self):
        self.ui.listMeasurements.removeRow(self.ui.listMeasurements.currentRow())

    def delAllItems(self):
        self.ui.listMeasurements.clear();
        self.ui.listMeasurements.setRowCount(0);

    def selectMeasurement(self):
        row = self.ui.listMeasurements.currentRow()
        self.calc=self.measurements[row]
        self.plotWidget.ploter(self)

    def calculate(self):
        if self.fileName[0] != []:
            self.get_parameters()
            self.ui.progressBar.setValue(8)
            self.calc["data"] = self.dataProcceser.truncate_value(self.calc["data"],self.calc["fs"])
            self.ui.progressBar.setValue(10)
            self.calc["audio_filtered"] = self.dataProcceser.low_filtering(self.calc["data"], self.calc["fs"])
            min_value, max_value = self.dataProcceser.get_min_max(self.calc["audio_filtered"])
            self.ui.progressBar.setValue(15)
            self.calc["audio_filtered_norm"] = np.matrix([self.dataProcceser.normalizer(np.array(self.calc["audio_filtered"][channel, :])[0], min_value, max_value) for channel in range(4)])
            self.ui.progressBar.setValue(20)
            self.calc["intensity"] = self.dataProcceser.pressure_to_intensity(self.calc["audio_filtered"])
            self.ui.progressBar.setValue(25)
            [self.calc["intensity_windows"], self.calc["az_el_windows"], self.calc["i_db"]] = self.dataProcceser.temporal_windowing(self.calc["intensity"], self.calc["fs"])
            self.ui.progressBar.setValue(40)
            self.calc["peaks"] = self.dataProcceser.window_selector(self.calc["i_db"], self.calc["fs"])
            self.ui.progressBar.setValue(45)
            self.calc["normalizado"]= self.dataProcceser.normalizer(self.calc["i_db"][0, self.calc["peaks"]])

            """self.widMatplot.plot(self.audio, self.fs, "Audio")"""
            self.ui.progressBar.setValue(50)
            self.plotWidget.ploter(self)

            self.addList()


if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainView()
    myapp.show()
    sys.exit(app.exec_())




