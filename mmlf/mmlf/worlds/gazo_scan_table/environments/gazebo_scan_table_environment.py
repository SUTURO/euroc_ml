from copy import deepcopy
import numpy
import rospy
from suturo_environment_msgs.srv import GetMap, ResetMap, GetPercentCleared
from suturo_startup_msgs.msg import TaskData
from suturo_startup_msgs.srv import TaskDataService
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.worlds.gazo_scan_table.actions import GazeboActions
from suturo_planning_search.map import Map

__author__ = 'hansa'


class GazeboScanTableEnvironment(SingleAgentEnvironment):

    DEFAULT_CONFIG_DICT = {
        "maxActions": 100,
        "minX": -1.57,
        "maxX": 1.57,
        "minY": -1.57,
        "maxY": 1.57,
        "stepsX": 4,
        "stepsY": 2,
        "task_name": "task1_v1"
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
        super(GazeboScanTableEnvironment, self).__init__(*args, useGUI=useGUI, **kwargs)

        # Initialize the simulation
        self.__taskdata = TaskData(name=self.configDict["task_name"])
        self.__init_simulation()

        self.pos_x = 0
        self.pos_y = 0
        oldStyleStateSpace = {
            "isScanned": ("discrete", [0, 1]),
            "isSomethingRight": ("discrete", [0,1]),
            "isSomethingLeft": ("discrete", [0,1]),
            "isSomethingUp": ("discrete", [0,1]),
            "isSomethingDown": ("discrete", [0,1])
        }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace)

        actions = GazeboActions(self.configDict["minX"],
                                self.configDict["maxX"],
                                self.configDict["minY"],
                                self.configDict["maxY"],
                                self.configDict["stepsX"],
                                self.configDict["stepsY"])
        oldStyleActionSpace = {
            "action": ("discrete", [actions.moveLeft,
                                    actions.moveRight,
                                    actions.moveUp,
                                    actions.moveDown,
                                    actions.scan])
        }

        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace)
        self.initialState = {
            "isScanned": 0,
            "isSomethingRight": 1,
            "isSomethingLeft": 0,
            "isSomethingUp": 1,
            "isSomethingDown": 0
        }
        self.currentState = deepcopy(self.initialState)
        if useGUI:
            from mmlf.gui.viewers import VIEWERS
            from mmlf.worlds.gazo_scan_table.environments.gazebo_table_viewer import GazeboTableViewer
            VIEWERS.addViewer(lambda: GazeboTableViewer(self), str(GazeboTableViewer))

        self.get_map = rospy.ServiceProxy(Map.NAME_SERVICE_GET_MAP, GetMap)
        self.reset_map = rospy.ServiceProxy(Map.NAME_SERVICE_GET_MAP, ResetMap)
        self.map_percent_cleared = rospy.ServiceProxy("/suturo/environment/get_map_percent_cleared", GetPercentCleared)
        self.__cell_map = None
        self.__need_update = True

    def check_new_state(self):
        x, y = self.camera_index
        r = False
        for i in range(x+1, self.configDict["rows"]):
            r = r or not self.cell_map[i,y]
        self.currentState["isSomethingRight"] = r
        l = False
        for i in range(0, x):
            l = l or not self.cell_map[i,y]
        self.currentState["isSomethingLeft"] = l
        u=False
        for i in range(y+1, self.configDict["columns"]):
            u = u or not self.cell_map[x,i]
        self.currentState["isSomethingUp"] = u
        d=False
        for i in range(0, y):
            d = d or not self.cell_map[x,i]
        self.currentState["isSomethingDown"] = d

    def getInitialState(self):
        return deepcopy(self.initialState)

    def _checkEpisodeFinished(self):
        return self.discovered_percentage >= 95 or self.stepCounter >= self.configDict["maxActions"]

    def __init_simulation(self):
        rospy.ServiceProxy("/suturo/startup/start_simulation", TaskDataService)(self.__taskdata)
        rospy.ServiceProxy("/suturo/startup/start_manipulation", TaskDataService)(self.__taskdata)
        rospy.ServiceProxy("/suturo/startup/start_perception", TaskDataService)(self.__taskdata)

    def stop(self):
        # Stop the simulation
        try:
            rospy.ServiceProxy("/suturo/startup/stop_simulation", TaskDataService)(self.__taskdata)
        finally:
            super(GazeboScanTableEnvironment, self).stop()

    def evaluateAction(self, actionObject):
        action = actionObject["action"]
        previousState = deepcopy(self.currentState)
        x, y = self.currentState["camera_x"], self.currentState["camera_y"]

        self.environmentLog.debug("Executing Action %s at (%d / %d)" % (action, x, y))
        reward = action(self)
        self.update_map()
        self.check_new_state()

        self.currentState["isScanned"] = 1 if self.cell_map[x, y] else 0
        episodeFinished = self._checkEpisodeFinished()
        terminalState = self.currentState if episodeFinished else None
        if episodeFinished:
            self.environmentLog.info("Episode %d lasted for %d steps" % (self.episodeCounter, self.stepCounter))
            self.episodeLengthObservable.addValue(self.episodeCounter,
                                                  self.stepCounter + 1)
            self.returnObservable.addValue(self.episodeCounter,
                                           -self.stepCounter)
            self.stepCounter = 0
            self.episodeCounter += 1
            self.currentState = self.getInitialState()
            self.resetTable()
            reward = 100 if self.discovered_percentage >= 95 else 0

            self.trajectoryObservable.addTransition(previousState, action,
                                                    reward, terminalState,
                                                    episodeTerminated=episodeFinished)
        else:
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

    def update_map(self):
        self.__need_update = True

    def camera_at_position(self, x, y):
        return self.camera_index == (x, y)

    def resetTable(self):
        self.reset_map()

    @property
    def discovered_percentage(self):
        response = self.map_percent_cleared()
        return response.percent

    @property
    def cell_map(self):
        if self.__cell_map is None or self.__need_update:
            map = self.get_map().map
            self.__cell_map = numpy.ndarray(shape=(map.size_column, map.size_column), dtype=bool)
            for x in range(map.size_column):
                for y in range(map.size_column):
                    self.__cell_map[x, y] = map.field[x * map.size_column + y].marked
            self.__need_update = False
        return self.__cell_map

    @property
    def camera_index(self):
        #TODO: Calculate a ray from the camera to the map plane
        return (0 ,0)

    @property
    def rows(self):
        return self.cell_map.shape()[0]

    @property
    def columns(self):
        return self.cell_map.shape()[1]


EnvironmentClass = GazeboScanTableEnvironment
EnvironmentName = "GazeboScanTableEnvironment"
