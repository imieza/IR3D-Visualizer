from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from matplotlib import rcParams
rcParams['font.size'] = 9

class MatplotlibWidget(Canvas):
    def __init__(self, parent=None, title='', xlabel='', ylabel='', dpi=100, hold=False):
        super(MatplotlibWidget, self).__init__(Figure())

        self.setParent(parent)
        self.figure = Figure(dpi=dpi)
        self.canvas = Canvas(self.figure)
        self.theplot = self.figure.add_subplot(111)

        self.theplot.set_title(title)
        self.theplot.set_xlabel(xlabel)
        self.theplot.set_ylabel(ylabel)

        self.setStyleSheet("QWidget {background-color:   #0ff}")

        ax1f1 = self.figure.add_subplot(111, axisbg='black')
