import math
from matplotlib.figure import Figure
from mmlf.framework.observables import OBSERVABLES, TrajectoryObservable, StateActionValuesObservable
from mmlf.gui.viewers.viewer import Viewer
from mmlf import QtGui, QtCore, FigureCanvas


__author__ = 'hansa'


class ScanTableSimViewer(Viewer):

    def __init__(self, scanTableSim, stateSpace, actions):
        super(ScanTableSimViewer, self).__init__()

        self.scanTableSim = scanTableSim
        self.stateSpace = stateSpace

        # Create matplotlib widgets
        plotWidgetPolicy = QtGui.QWidget(self)
        plotWidgetPolicy.setMinimumSize(400, 400)
        plotWidgetPolicy.setWindowTitle ("Table")

        self.figPolicy = Figure((4.0, 4.0), dpi=100)
        self.figPolicy.subplots_adjust(left=0.01, bottom=0.01, right=0.99,
                                       top= 0.99, wspace=0.05, hspace=0.11)
        self.canvasPolicy = FigureCanvas(self.figPolicy)
        self.canvasPolicy.setParent(plotWidgetPolicy)
        self.canvasPolicy.draw()

        # Combo Box for selecting the observable
        refreshLabel = QtGui.QLabel("Refresh after")
        comboBox = QtGui.QComboBox(self)
        comboBox.addItems(["Every step", "10 Steps", "100 Steps"])
        self.connect(comboBox, QtCore.SIGNAL('currentIndexChanged (int)'),
                     self._refeshChanged)

        mdiArea = QtGui.QMdiArea(self)
        mdiArea.addSubWindow(plotWidgetPolicy)
        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(mdiArea)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(refreshLabel)
        hlayout.addWidget(comboBox)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)
        # Draw
        self.redraw()
        self.sample_num = 0
        self.refresh_after = 1
        self.trajectoryObservable = OBSERVABLES.getAllObservablesOfType(TrajectoryObservable)[0]
        # Connect to observer (has to be the last thing!!)
        self.trajectoryObservableCallback = lambda *transition: self.updateSamples()
        self.trajectoryObservable.addObserver(self.trajectoryObservableCallback)


    def _refeshChanged(self, idx):
        self.refresh_after = int(math.pow(10, idx))

    def updateSamples(self):
        self.sample_num += 1
        if self.sample_num % self.refresh_after == 0:
            self.sample_num = 0
            self.redraw()

    def get_fill_color_for_cell(self, cell_value):
        if not cell_value:
            return "w"
        else:
            return "g"

    def plotSquare(self, axis, center, color='k', zorder=1):
        return axis.fill([center[0] - 0.5, center[0] + 0.5, center[0] + 0.5, center[0] - 0.5],
                         [center[1] - 0.5, center[1] - 0.5, center[1] + 0.5, center[1] + 0.5],
                         facecolor=color, edgecolor="k", zorder=zorder)

    def close(self):
        #if self.stateActionValuesObservable is not None:
            # Remove old observable
        #    self.stateActionValuesObservable.removeObserver(self.stateActionValuesObservableCallback)
        self.trajectoryObservable.removeObserver(self.trajectoryObservableCallback)
        Viewer.close(self)

    def redraw(self):
        rows, cols = self.scanTableSim.cell_map.shape
        self.table_cells = self.scanTableSim.cell_map
        ax = self.figPolicy.gca()
        ax.clear()
        for x in range(rows):
            for y in range(cols):
                if self.scanTableSim.camera_at_position(x, y):
                    fill_color = "k"
                else:
                    fill_color = self.get_fill_color_for_cell(self.table_cells[x, y])
                self.plotSquare(ax, (y, x), color=fill_color)
        self.canvasPolicy.draw()

    def _observableChanged(self, comboBoxIndex):
        if self.stateActionValuesObservable is not None:
            # Remove old observable
            self.stateActionValuesObservable.removeObserver(self.stateActionValuesObservableCallback)
        # Get new observable and add as listener
        self.stateActionValuesObservable = self.stateActionValuesObservables[comboBoxIndex]
        self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)