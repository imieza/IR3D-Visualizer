import warnings

from Plotly import PrintInPlotLy

warnings.filterwarnings('ignore')
import sys
from MayaviQWidget import MayaviQWidget
import math
from scipy import signal
from interface import *
import numpy as np
from plotWidget import PlotWidget
from dataProcessing import DataProcessing
from datetime import datetime
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
import darkorange


class MainView(QtGui.QMainWindow):
    parameters = {}

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_IRV360()
        self.ui.setupUi(self)
        self.plotWidget = PlotWidget()
        self.plotly = PrintInPlotLy()
        # Adding toolbar
        self.add1DToolBars()

        # Adding Mayavi Widget
        widget = self.ui.widget3d
        layout = QtGui.QGridLayout(widget)
        self.mayavi_widget = MayaviQWidget(self)
        layout.addWidget(self.mayavi_widget, 1, 1)

        self.set_initial_values()

        self.ui.btnRecalculate.clicked.connect(self.calculate)
        self.ui.btnSelect.clicked.connect(self.selectMeasurement)
        self.ui.btnDelete.clicked.connect(self.delItem)
        self.ui.btnDeleteAll.clicked.connect(self.delAllItems)
        self.ui.btnLocate.clicked.connect(self.locate)

        self.connect(self.ui.new_project, QtCore.SIGNAL("triggered()"), self.new_project)
        self.connect(self.ui.save_Project, QtCore.SIGNAL("triggered()"), self.save_project)
        self.connect(self.ui.open_project, QtCore.SIGNAL("triggered()"), self.open_project)
        self.connect(self.ui.import_Measurement, QtCore.SIGNAL("triggered()"), self.openFile)
        self.connect(self.ui.import_Floorplan, QtCore.SIGNAL("triggered()"), self.openFileFloorplan)
        self.connect(self.ui.export_to_Plotly, QtCore.SIGNAL("triggered()"), self.export_to_plotly)

        # manually connect qdial with qbox (this is because is not possible to set 0 in horizontal-left side)
        self.connect(self.ui.dialAngle, QtCore.SIGNAL("valueChanged(int)"), self.setValue_Qdial)
        self.connect(self.ui.rotationAngle, QtCore.SIGNAL("valueChanged(int)"), self.setValue_QBox_from_Qdial)
        self.rotationAngle_in0()

    def rotationAngle_in0(self):
        self.ui.dialAngle.setValue(90)

    def setValue_Qdial(self):
        value_fromQdial = self.ui.dialAngle.value()
        value = value_fromQdial + 270 if value_fromQdial < 90 else value_fromQdial - 90
        self.ui.rotationAngle.setValue(value)
        try:
            self.plotWidget.plotFloorplan(self)
        except:
            pass

    def setValue_QBox_from_Qdial(self):
        value_fromQBox = self.ui.rotationAngle.value()
        value = value_fromQBox - 270 if value_fromQBox >= 270 else value_fromQBox + 90
        self.ui.dialAngle.setValue(value)

    def set_initial_values(self):
        # Initial values
        self.numberMeasurement = 0  # Number of measurement calculated
        self.measurements = []
        self.get_parameters()
        self.floorplanFile = None
        self.dataProcceser = DataProcessing(self)
        self.ui.progressBar.setValue(0)

    def add1DToolBars(self):

        navi_toolbarPressure = NavigationToolbar(self.ui.plotPressure, self.ui.tabPressureLevel)
        self.ui.tabLayoutPressureLevel.addWidget(navi_toolbarPressure)

        navi_toolbarIntensity = NavigationToolbar(self.ui.plotIntensity, self.ui.tabIntensityLevel)
        self.ui.tabLayoutIntensityLevel.addWidget(navi_toolbarIntensity)

        navi_toolbarWindow = NavigationToolbar(self.ui.plotWindowLevel, self.ui.tabWindowLevel)
        self.ui.tabLayoutLevel.addWidget(navi_toolbarWindow)

        navi_toolbarFilter = NavigationToolbar(self.ui.plotFilter, self.ui.tabFilter)
        self.ui.tabLayoutFilter.addWidget(navi_toolbarFilter)

        navi_toolbarSpectrogram = NavigationToolbar(self.ui.plotSpectrogram, self.ui.tabSpectrogram)
        self.ui.tabLayoutSpectrogram.addWidget(navi_toolbarSpectrogram)

        navi_toolbarFloorplan = NavigationToolbar(self.ui.plotFloorplan, self.ui.tabFloorplan)
        self.ui.tabLayoutFloorplan.addWidget(navi_toolbarFloorplan)

    def openFile(self):
        self.calc = {}
        fileName = QtGui.QFileDialog.getOpenFileNames(None, ("Open File"), "../Audios de prueba/Odeon", ("Wav Files (*.wav)"))
        self.fileName = fileName
        self.calc['filename'] = self.fileName
        self.parameters["directSoundSelection"] = 0

        [self.calc["data"], self.calc["fs"]] = self.dataProcceser.load_wavefile(self.fileName)
        self.calc["time"] = self.dataProcceser.generate_time(self.calc["fs"], self.calc["data"])
        self.ui.audioCutter.setValue(self.calc["time"][len(self.calc["time"]) - 1] * 1000)
        self.numberMeasurement = self.numberMeasurement + 1
        self.calc["name"] = "IR_" + str(self.numberMeasurement)

        self.calc["parameters"] = self.parameters

        self.calculate()
        self.calc['datetime'] = str(datetime.now())
        self.addList(self.calc)
        self.measurements.append(dict(self.calc))

    def openFileFloorplan(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(None, ("Open Image File"), "/home/", ("Image Files (*.png)"))
        self.floorplanFile = fileName[0]
        self.plotWidget.plotFloorplan(self)

    def get_parameters(self, fs=44100):
        self.parameters["value2truncate"] = self.ui.audioCutter.value()
        self.parameters["cutoff_frequency_hipass"] = self.ui.hiPassFiltering.value()  # 1000
        self.parameters["cutoff_frequency_lowpass"] = self.ui.lowPassFiltering.value()  # 5000
        self.parameters["timeWindow"] = self.ui.windowingWindowSize.value()
        self.parameters["number_of_windows"] = self.ui.windowingQuantity.value()
        self.parameters["overlapping"] = self.ui.Overlapping.currentText()
        self.parameters["conversion_type"] = self.ui.conversionType.currentText()
        self.parameters["threshold"] = self.ui.thresholdValue.value()

    def new_project(self):
        import subprocess
        np.save('utlimo_proyecto.npy', self.measurements)
        subprocess.Popen("python" + " IRV360.py", shell=True)

    def save_project(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save file", "", ".npy")
        np.save(filename, [self.measurements, self.floorplanFile])

    def export_to_plotly(self):
        self.plotly.plot(self.calc)

    def open_project(self):
        filename = QtGui.QFileDialog.getOpenFileNames(None, ("Open Project"), "/home/", ("npy Files (*.npy)"))
        [measurements, floorplanFile] = np.load(filename[0])
        self.measurements = measurements
        self.floorplanFile = floorplanFile
        self.calc = self.measurements[0]
        self.parameters = self.calc["parameters"]
        self.plotWidget.ploter(self)

        for measurement in self.measurements:
            self.addList(measurement)

        if floorplanFile:
            self.plotWidget.plotFloorplan(self)

    def addList(self, measurement):
        rowPosition = self.ui.listMeasurements.rowCount()
        self.ui.listMeasurements.insertRow(rowPosition)
        self.ui.listMeasurements.setItem(rowPosition, 0, QtGui.QTableWidgetItem(measurement["name"]))
        self.ui.listMeasurements.setItem(rowPosition, 1, QtGui.QTableWidgetItem(str(measurement["datetime"])[:19]))
        self.ui.listMeasurements.setItem(rowPosition, 2, QtGui.QTableWidgetItem(str(measurement["filename"])))

    def delItem(self):
        self.ui.listMeasurements.removeRow(self.ui.listMeasurements.currentRow())

    def delAllItems(self):
        self.ui.listMeasurements.clear();
        self.ui.listMeasurements.setRowCount(0);

    def selectMeasurement(self):
        row = self.ui.listMeasurements.currentRow()
        self.calc = self.measurements[row]
        self.parameters = self.calc["parameters"]
        self.plotWidget.ploter(self)

    def calculate(self):
        if self.fileName[0] != []:
            self.get_parameters(self.calc["fs"])
            self.ui.progressBar.setValue(8)
            self.calc["data"] = self.dataProcceser.truncate_value(self.calc["data"], self.calc["fs"])
            self.ui.progressBar.setValue(10)
            self.calc["audio_filtered"] = self.dataProcceser.filtering(self.calc["data"], self.calc["fs"])
            self.ui.progressBar.setValue(15)
            self.calc['time'] = self.dataProcceser.generate_time(self.calc['fs'], self.calc['data'])
            self.ui.progressBar.setValue(20)
            if self.parameters["conversion_type"] == "Instantaneous":
                self.calc["intensity"] = self.dataProcceser.pressure_to_intensity(self.calc["audio_filtered"])
                self.ui.progressBar.setValue(25)
                [self.calc["intensity_windows"], self.calc["az_el_windows"],
                 self.calc["i_db"]] = self.dataProcceser.temporal_windowing(self.calc["intensity"], self.calc["fs"])
            else:
                [self.calc["intensity_windows"], self.calc["intensity"], self.calc["az_el_windows"],
                 self.calc["i_db"]] = self.dataProcceser.pressure_to_intensity_fft(self.calc["fs"], self.calc["audio_filtered"])

            self.ui.progressBar.setValue(40)
            self.calc["peaks"] = self.dataProcceser.window_selector(self.calc["i_db"], self.calc["fs"])
            self.dataProcceser.refactoring_time()
            self.ui.progressBar.setValue(45)
            self.calc["normalizado"] = np.asarray(self.dataProcceser.normalizer(self.calc["i_db"]))[self.calc["peaks"]]
            # self.calc["normalizado"] = self.calc["i_db"][self.calc["peaks"]]
            self.calc['xyz'] = self.dataProcceser.sph2cart(self.calc["az_el_windows"], self.calc["peaks"],
                                                           self.calc["normalizado"])
            self.calc["center"] = self.dataProcceser.get_center(self.calc["xyz"])

            # self.widMatplot.plot(self.audio, self.fs, "Audio")
            self.ui.progressBar.setValue(50)
            #print "xyz antes de plotear: ", self.calc['xyz'][0]
            self.plotWidget.ploter(self)

            np.save('original_data.npy', self.calc['data'])

    def locate(self):
        # QApplication.OverrideCursor()
        self.eventClickLocate = self.ui.plotFloorplan.figure.canvas.mpl_connect('button_press_event', self.clickLocate)

    def clickLocate(self, event):

        if event.inaxes is not None:
            positionLocate = event.xdata, event.ydata

            row = self.ui.listMeasurements.currentRow()
            self.measurements[row]["location"] = list(positionLocate)

        self.ui.plotFloorplan.figure.canvas.mpl_disconnect(self.eventClickLocate)
        self.plotWidget.plotFloorplan(self)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainView()
    myapp.setStyleSheet(darkorange.getStyleSheet())
    myapp.show()
    sys.exit(app.exec_())
