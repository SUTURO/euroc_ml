from collections import defaultdict
from matplotlib.figure import Figure
from mmlf.framework.observables import OBSERVABLES, TrajectoryObservable, StateActionValuesObservable
from mmlf.framework.state import State
from mmlf.gui.viewers.viewer import Viewer
from mmlf import QtGui, QtCore, FigureCanvas


__author__ = 'hansa'


class ScanTableSimViewer(Viewer):

    def __init__(self, scanTableSim, stateSpace, actions):
        super(ScanTableSimViewer, self).__init__()

        self.scanTableSim = scanTableSim
        self.stateSpace = stateSpace
        self.actions = actions
        self.samples = defaultdict(lambda : 0)
        self.valueAccessFunction = None
        self.stateActionValuesObservables = OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable)

        # Create matplotlib widgets
        plotWidgetPolicy = QtGui.QWidget(self)
        plotWidgetPolicy.setMinimumSize(300, 400)
        plotWidgetPolicy.setWindowTitle ("Table")

        self.figPolicy = Figure((3.0, 4.0), dpi=100)
        self.figPolicy.subplots_adjust(left=0.01, bottom=0.01, right=0.99,
                                       top= 0.99, wspace=0.05, hspace=0.11)
        self.canvasPolicy = FigureCanvas(self.figPolicy)
        self.canvasPolicy.setParent(plotWidgetPolicy)
        self.canvasPolicy.draw()
        self.mdiArea = QtGui.QMdiArea(self)
        self.mdiArea.addSubWindow(plotWidgetPolicy)
        self.vlayout = QtGui.QVBoxLayout()
        self.vlayout.addWidget(self.mdiArea)
        self.hlayout = QtGui.QHBoxLayout()
        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)

        self.stateActionValuesObservableCallback = \
             lambda valueAccessFunction, actions: self.updateValues(valueAccessFunction, actions)
        if len(self.stateActionValuesObservables) > 0:
            # Show per default the first observable
            self.stateActionValuesObservable = self.stateActionValuesObservables[1]

            self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)
        else:
            self.stateActionValuesObservable = None
        self.redraw()

    def updateValues(self, valueAccessFunction, actions):
        self.valueAccessFunction = valueAccessFunction
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

    def redraw(self):
        cols, rows = self.scanTableSim.cell_map.shape
        self.table_cells = self.scanTableSim.cell_map
        ax = self.figPolicy.gca()
        ax.clear()
        for x in range(rows):
            for y in range(cols):
                if self.scanTableSim.camera_at_position(x, y):
                    fill_color = "k"
                else:
                    fill_color = self.get_fill_color_for_cell(self.table_cells[y, x])
                self.plotSquare(ax, (y, x), color=fill_color)