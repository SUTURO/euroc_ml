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
        stateActionValuesObservables = OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable)

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

        # Combo Box for selecting the observable
        observableLabel = QtGui.QLabel("Observable")
        self.comboBox = QtGui.QComboBox(self)
        self.comboBox.addItems(map(lambda x: "%s" % x.title, stateActionValuesObservables))
        self.connect(self.comboBox, QtCore.SIGNAL('currentIndexChanged (int)'),
                     self._observableChanged)

        # Automatically update combobox when new float stream observables
        #  are created during runtime
        def updateComboBox(observable, action):
            self.comboBox.clear()
            stateActionValuesObservables = OBSERVABLES.getAllObservablesOfType(StateActionValuesObservable)
            self.comboBox.addItems(map(lambda x: "%s" % x.title, stateActionValuesObservables))
        OBSERVABLES.addObserver(updateComboBox)

        mdiArea = QtGui.QMdiArea(self)
        mdiArea.addSubWindow(plotWidgetPolicy)
        vlayout = QtGui.QVBoxLayout()
        vlayout.addWidget(mdiArea)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(observableLabel)
        hlayout.addWidget(self.comboBox)
        vlayout.addLayout(hlayout)
        self.setLayout(vlayout)
        # Draw
        self.redraw()
        self.stateActionValuesObservableCallback = lambda _, a: self.redraw()
        if len(stateActionValuesObservables) > 0:
            # Show per default the first observable
            self.stateActionValuesObservable = stateActionValuesObservables[0]
            self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)
        else:
            self.stateActionValuesObservable = None

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
        if self.stateActionValuesObservable is not None:
            # Remove old observable
            self.stateActionValuesObservable.removeObserver(self.stateActionValuesObservableCallback)
        Viewer.close(self)

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
        self.canvasPolicy.draw()

    def _observableChanged(self, comboBoxIndex):
        if self.stateActionValuesObservable is not None:
            # Remove old observable
            self.stateActionValuesObservable.removeObserver(self.stateActionValuesObservableCallback)
        # Get new observable and add as listener
        self.stateActionValuesObservable = self.stateActionValuesObservables[comboBoxIndex]
        self.stateActionValuesObservable.addObserver(self.stateActionValuesObservableCallback)