from copy import deepcopy
import numpy
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.worlds.scantablesim_world.actions.action_base import SimSimAction


__author__ = 'hansa'


class ScanTableSimEnvironment(SingleAgentEnvironment):

    DEFAULT_CONFIG_DICT = {
        "rows": 50,
        "columns": 50,
        "camera_fov_height": 1,
        "camera_fov_width": 2,
        "actionDelayTime": 0.0,
        "maxActions": 100,
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
        self.__table_cells = numpy.zeros(shape=(self.configDict["rows"], self.configDict["columns"]), dtype=bool, order="F")

        # oldStyleStateSpace = {
        #     "camera_x": ("discrete", range(self.configDict["columns"])),
        #     "camera_y": ("discrete", range(self.configDict["rows"])),
        #     "isScanned": ("discrete", range(0, 1))
        # }
        self.pos_x = self.configDict["rows"] / 2
        self.pos_y = self.configDict["columns"] / 2
        oldStyleStateSpace = {
            # "camera_x": ("discrete", range(self.configDict["rows"])),
            # "camera_y": ("discrete", range(self.configDict["columns"])),
            "isScanned": ("discrete", [True,False]),
            "untenLinks": ("discrete", [True,False]),
            "untenRechts": ("discrete", [True,False]),
            "obenLinks": ("discrete", [True,False]),
            "obenRechts": ("discrete", [True,False])
            # "isTurbo": ("discrete", [0,1])
        }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace)


        self.__actions = SimSimAction()
        oldStyleActionSpace = {
            "action": ("discrete", self.__actions.actions)
        }

        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace)
        self.initialState = {
            # "camera_x": 0,
            # "camera_y": 0,
            "isScanned": False,
            "untenLinks": True,
            "untenRechts": True,
            "obenLinks": True,
            "obenRechts": True,
            # "isTurbo": 0
        }
        self.currentState = deepcopy(self.initialState)
        if useGUI:
            from mmlf.gui.viewers import VIEWERS
            from mmlf.worlds.scantablesim_world.environments.scantablesim_viewer import ScanTableSimViewer
            VIEWERS.addViewer(lambda: ScanTableSimViewer(self,
                                                         self.stateSpace,
                                                         ["scan", "left", "right", "up", "down"]),
                              "ScanTableSimViewer")

    # def

    def getInitialState(self):
        return deepcopy(self.initialState)

    def _checkEpisodeFinished(self):
        return self.discovered_percentage >= 95 or self.stepCounter >= self.configDict["maxActions"]

    def isScanned(self):
        curr_x, curr_y = self.camera_index
        fov_width, fov_height = self.configDict["camera_fov_width"], self.configDict["camera_fov_height"]
        scanned = 0
        max = 0
        for x in range(curr_x - fov_height, curr_x + 1 + fov_height):
            for y in range(curr_y - fov_width+abs(curr_x-x), curr_y + 1 + fov_width-abs(curr_x-x)):
                if x >= 0 and y >= 0 and x < self.configDict["rows"] and y < self.configDict["columns"] and self.__table_cells[x, y]:
                    scanned += 1.
                max += 1.
        return 1-((max - scanned)/ max) > 0.7

    def evaluateAction(self, actionObject):
        action = actionObject["action"]
        previousState = deepcopy(self.currentState)
        self.check_new_state2()
        x, y = self.pos_x, self.pos_y
        reward = self.__actions.performAction(action, self)
        self.environmentLog.debug("   ")
        self.environmentLog.debug("Executing Action %s" % (str(self.currentState)))
        self.environmentLog.debug("Executing Action %s at (%d / %d), reward=%d" % (action, x, y, reward))
        # self.currentState["isScanned"] = self.isScanned()
        self.currentState["isScanned"] = self.cell_map[x, y]

        episodeFinished = self._checkEpisodeFinished()
        terminalState = self.currentState if episodeFinished else None
        if episodeFinished:
            reward = self.discovered_percentage **3 /5000
            # reward = 100 if self.discovered_percentage > 95 else -100
            self.environmentLog.info("Episode %d lasted for %d steps; reward = %d" % (self.episodeCounter, self.stepCounter, reward))
            self.episodeLengthObservable.addValue(self.episodeCounter,
                                                  self.stepCounter + 1)
            self.returnObservable.addValue(self.episodeCounter,
                                           -self.stepCounter)
            self.stepCounter = 0
            self.episodeCounter += 1
            self.currentState = self.getInitialState()
            self.pos_x = self.configDict["rows"] / 2
            self.pos_y = self.configDict["columns"] / 2
            self.__table_cells = numpy.zeros(shape=(self.configDict["rows"], self.configDict["columns"]), dtype=bool, order="C")
            # reward = 200 if self.discovered_percentage >= 95 else 0
            self.trajectoryObservable.addTransition(previousState, action,
                                                    reward, terminalState,
                                                    episodeTerminated=episodeFinished)
        else:
            # if action == "scan":
            # if reward == 0:
            #     reward = -1
            self.stepCounter += 1
            self.trajectoryObservable.addTransition(previousState, action,
                                                    reward, self.currentState,
                                                    episodeTerminated=episodeFinished)
        return {
            "reward": reward,
            "terminalState": terminalState,
            "nextState": self.currentState,
            "startNewEpisode": episodeFinished
        }

    def check_new_state(self):
        x, y = self.pos_x, self.pos_y
        r = False
        for i in range(x+1, self.configDict["rows"]):
            r = r or not self.__table_cells[i,y]
        self.currentState["untenLinks"] = r
        r = False
        for i in range(0, x):
            r = r or not self.__table_cells[i,y]
        self.currentState["untenRechts"] = r
        r=False
        for i in range(y+1, self.configDict["columns"]):
            r = r or not self.__table_cells[x,i]
        self.currentState["obenLinks"] = r
        r=False
        for i in range(0, y):
            r = r or not self.__table_cells[x,i]
        self.currentState["obenRechts"] = r

    def check_new_state2(self):
        x, y = self.pos_x, self.pos_y
        uL = False
        oLL = False
        uRR = False
        oRR = False
        for i in range(self.configDict["rows"]):
            for j in range(self.configDict["columns"]):
                if i < x and j < y:
                    uL = uL or not self.__table_cells[i,j]
                elif i > x and j < y:
                    oLL = oLL or not self.__table_cells[i,j]
                elif i < x and j > y:
                    uRR = uRR or not self.__table_cells[i,j]
                elif i > x and j > y:
                    oRR = oRR or not self.__table_cells[i,j]

        self.currentState["untenLinks"] = uL
        self.currentState["untenRechts"] = uRR
        self.currentState["obenLinks"] = oLL
        self.currentState["obenRechts"] = oRR
        pass

    def update_if_valid(self, x, y, value):
        if x >= 0 and y >= 0 and x < self.configDict["rows"] and y < self.configDict["columns"]:
            if not self.__table_cells[x, y]:
                self.__table_cells[x, y] = value
                return True
        return False

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
        return (self.pos_x, self.pos_y)

    @property
    def rows(self):
        return self.configDict["rows"]

    @property
    def columns(self):
        return self.configDict["columns"]


EnvironmentClass = ScanTableSimEnvironment
EnvironmentName = "ScanTableSim"
