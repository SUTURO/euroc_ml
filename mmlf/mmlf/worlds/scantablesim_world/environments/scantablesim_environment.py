from copy import deepcopy
import numpy
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.spaces import StateSpace, ActionSpace


__author__ = 'hansa'


class ScanTableSimEnvironment(SingleAgentEnvironment):

    DEFAULT_CONFIG_DICT = {
        "rows": 5,
        "columns": 50,
        "camera_fov_height": 1,
        "camera_fov_width": 2,
        "actionDelayTime": 0.0
    }

    def __init__(self, useGUI, *args, **kwargs):
        self.environmentInfo = EnvironmentInfo(
            versionNumber="0.3",
            environmentName="ScanTableSim",
            discreteActionSpace=True,
            episodic=True,
            continuousStateSpace=False,
            continuousActionSpace=False,
            stochastic=False)
        super(ScanTableSimEnvironment, self).__init__(*args, useGUI=useGUI, **kwargs)
        self.__table_cells = numpy.zeros(shape=(self.configDict["columns"], self.configDict["rows"]), dtype=bool, order="F")

        oldStyleStateSpace = {
            "camera_x": ("discrete", range(self.configDict["columns"])),
            "camera_y": ("discrete", range(self.configDict["rows"])),
            "percentScanned": ("discrete", range(100))
        }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace)

        oldStyleActionSpace = {
            "action": ("discrete", ["left", "right", "up", "down", "scan"])
        }

        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace)
        self.initialState = {
            "camera_x": 0,
            "camera_y": 0,
            "percentScanned": 0
        }
        self.currentState = deepcopy(self.initialState)
        if useGUI:
            from mmlf.gui.viewers import VIEWERS
            from mmlf.worlds.scantablesim_world.environments.scantablesim_viewer import ScanTableSimViewer
            VIEWERS.addViewer(lambda: ScanTableSimViewer(self,
                                                 self.stateSpace,
                                                 ["scan", "left", "right", "up", "down"]),
                              "ScanTableSimViewer")


    def getInitialState(self):
        return deepcopy(self.initialState)

    def _checkEpisodeFinished(self):
        return self.discovered_percentage >= 95 or self.stepCounter >= 100

    def evaluateAction(self, actionObject):
        action = actionObject["action"]
        self.environmentLog.info("Executing Action: %s" % action)
        #previousState = deepcopy(self.currentState)
        x, y = self.currentState["camera_x"], self.currentState["camera_y"]
        if action == "left":
            self.move_to(x, y - 1)
        elif action == "right":
            self.move_to(x, y + 1)
        elif action == "up":
            self.move_to(x - 1, y)
        elif action == "down":
            self.move_to(x + 1, y)
        elif action == "scan":
            self.scan_table()
            self.currentState["percentScanned"] = self.discovered_percentage

        episodeFinished = self._checkEpisodeFinished()
        terminalState = self.currentState if episodeFinished else None
        if episodeFinished:
            self.environmentLog.info("Episode lasted for %d steps" % self.stepCounter)
            self.episodeLengthObservable.addValue(self.episodeCounter,
                                                  self.stepCounter + 1)
            self.returnObservable.addValue(self.episodeCounter,
                                           -self.stepCounter)
            reward = 10 if self.currentState != (0, 0) else -10
            self.stepCounter = 0
            self.episodeCounter += 1

            self.currentState = self.getInitialState()
        else:
            reward = -1
            self.stepCounter += 1
        return {
            "reward": reward,
            "terminalState": terminalState,
            "nextState": self.currentState,
            "startNewEpisode": episodeFinished
        }

    def move_to(self, x, y):
        if x >= 0 and y >= 0 and x < self.configDict["columns"] and y < self.configDict["rows"]:
            self.currentState["camera_x"] = x
            self.currentState["camera_y"] = y


    def __update_if_valid(self, x, y, value):
        if x >= 0 and y >= 0 and x < self.configDict["columns"] and y < self.configDict["rows"]:
            self.__table_cells[x, y] = value

    def scan_table(self):
        curr_x, curr_y = self.currentState["camera_x"], self.currentState["camera_y"]
        fov_width, fov_height = self.configDict["camera_fov_width"], self.configDict["camera_fov_height"]
        for x in range(curr_x - fov_height, curr_x + 1 + fov_height):
            for y in range(curr_y - fov_width, curr_y + 1 + fov_width):
                self.__update_if_valid(x, y, True)

    def camera_at_position(self, x, y):
        return self.camera_index == (x, y)

    @property
    def discovered_percentage(self):
        return int(self.__table_cells.sum() / float(self.__table_cells.size) * 100)

    @property
    def cell_map(self):
        return self.__table_cells

    @property
    def camera_index(self):
        return (self.currentState["camera_x"], self.currentState["camera_y"])

    @property
    def rows(self):
        return self.configDict["rows"]

    @property
    def columns(self):
        return self.configDict["columns"]


EnvironmentClass = ScanTableSimEnvironment
EnvironmentName = "ScanTableSim"