import sys
from MayaviQWidget import MayaviQWidget

from interface import *
from PyQt4.QtGui import *
from PyQt4.QtCore import SIGNAL
import matplotlib.pyplot as plt
import numpy as np
from plotWidget import PlotWidget
from dataProcessing import DataProcessing
from datetime import datetime
from pymouse import PyMouse
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar


class MainView(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.plotWidget = PlotWidget()

        # Adding toolbar
        self.add1DToolBars()

        # Adding Mayavi Widget
        widget = self.ui.widget3d
        layout = QtGui.QGridLayout(widget)
        self.mayavi_widget = MayaviQWidget(self)
        layout.addWidget(self.mayavi_widget, 1, 1)

        # Initial values
        self.numberMeasurement = 0 #Number of measurement calculated
        self.measurements = []
        self.get_parameters()
        self.dataProcceser = DataProcessing(self)
        self.ui.progressBar.setValue(0)

        self.ui.btnRecalculate.clicked.connect(self.calculate)
        self.ui.btnSelect.clicked.connect(self.selectMeasurement)
        self.ui.btnDelete.clicked.connect(self.delItem)
        self.ui.btnDeleteAll.clicked.connect(self.delAllItems)
        self.ui.btnLocate.clicked.connect(self.locate)

        self.connect(self.ui.actionNew_project, QtCore.SIGNAL("triggered()"), self.openFile)
        self.connect(self.ui.actionImport_Floorplan, QtCore.SIGNAL("triggered()"), self.openFileFloorplan)

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
        fileName = QtGui.QFileDialog.getOpenFileNames(None,("Open File"), "/home/", ("Wav Files (*.wav)"))
        #self.fileName = "C:\Users\W\Documents\IR3D\IR3D-Visualizer\Audios de prueba\stpatricks_s2r2.wav"
        self.fileName = fileName[0]
        [self.calc["data"], self.calc["fs"]] = self.dataProcceser.load_wavefile(self.fileName)
        self.calc["time"] = self.dataProcceser.generate_time(self.calc["fs"], self.calc["data"])
        self.ui.audioCutter.setValue(self.calc["time"][len(self.calc["time"])-1]*1000)
        self.numberMeasurement = self.numberMeasurement+1
        self.calc["name"] = "IR_" + str(self.numberMeasurement)
        self.calculate()
        self.addList()

    def openFileFloorplan(self):
        fileName = QtGui.QFileDialog.getOpenFileNames(None,("Open Image File"), "/home/", ("Image Files (*.png)"))
        self.floorplanFile = fileName[0]
        self.plotWidget.plotFloorplan(self)

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
        self.ui.listMeasurements.setItem(rowPosition, 0, QtGui.QTableWidgetItem(self.calc["name"]))
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
            self.calc["center"] = self.dataProcceser.get_center(self.calc["normalizado"])

            #self.widMatplot.plot(self.audio, self.fs, "Audio")
            self.ui.progressBar.setValue(50)
            self.plotWidget.ploter(self)

    def locate(self):
        #QApplication.OverrideCursor()
        self.eventClickLocate = self.ui.plotFloorplan.figure.canvas.mpl_connect('button_press_event', self.clickLocate)

    def clickLocate(self, event):

        if event.inaxes is not None:
            positionLocate = event.xdata, event.ydata

            row = self.ui.listMeasurements.currentRow()
            self.measurements[row]["location"]=positionLocate

        self.ui.plotFloorplan.figure.canvas.mpl_disconnect(self.eventClickLocate)
        self.plotWidget.plotFloorplan(self)

if __name__== "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainView()
    myapp.show()
    sys.exit(app.exec_())




