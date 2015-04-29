from copy import deepcopy
import numpy
from threading import Thread
from euroc_c2_msgs.srv import StartSimulator, StopSimulator
import rospy
from suturo_environment_msgs.srv import GetMap, ResetMap, GetPercentCleared
from std_msgs import msg as std_msgs
import time
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.worlds.gazo_scan_table.actions import GazeboActions
from suturo_planning_search.cell import Cell
from suturo_planning_search.map import Map
from suturo_planning_yaml_pars0r.yaml_pars0r import YamlPars0r


__author__ = 'hansa'


__stopped = False


def publish_yaml(yaml):
    parser = rospy.Publisher("/suturo/startup/yaml_pars0r_input", std_msgs.String)
    while not __stopped:
        parser.publish(data=yaml)
        time.sleep(5)


class GazeboScanTableEnvironment(SingleAgentEnvironment):

    DEFAULT_CONFIG_DICT = {
        "maxActions": 100,
        "minPan": -1.50,
        "maxPan": 1.50,
        "minTilt": -1.50,
        "maxTilt": 1.50,
        "stepsPan": 8,
        "stepsTilt": 8,
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
        self.__init_simulation()

        self.pan = 0
        self.tilt = 0
        oldStyleStateSpace = {
            "isScanned": ("discrete", [0, 1]),
            "isSomethingRight": ("discrete", [0,1]),
            "isSomethingLeft": ("discrete", [0,1]),
            "isSomethingUp": ("discrete", [0,1]),
            "isSomethingDown": ("discrete", [0,1])
        }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace)

        actions = GazeboActions(self.configDict["minPan"],
                                self.configDict["maxPan"],
                                self.configDict["minTilt"],
                                self.configDict["maxTilt"],
                                self.configDict["stepsPan"],
                                self.configDict["stepsTilt"])
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
            VIEWERS.addViewer(lambda: GazeboTableViewer(self), "GazeboTable Viewer")

        self.get_map = rospy.ServiceProxy(Map.NAME_SERVICE_GET_MAP, GetMap)
        self.reset_map = rospy.ServiceProxy(Map.NAME_SERVICE_RESET_MAP, ResetMap)
        self.map_percent_cleared = rospy.ServiceProxy("/suturo/environment/get_map_percent_cleared", GetPercentCleared)
        self.__cell_map = None
        self.__need_update = True
        self.__rows = None
        self.__cols = None
        self.__cell_size = None
        self.__percent_cleared = 0.0

    def check_new_state(self):
        x, y = self.camera_index
        self.currentState["isSomethingRight"] = False
        for i in range(x+1, self.rows):
            if not self.cell_map[i,y]:
                self.currentState["isSomethingRight"] = True
                break
        self.currentState["isSomethingLeft"] = False
        for i in range(0, x):
            if not self.cell_map[i,y]:
                self.currentState["isSomethingLeft"] = True
                break
        self.currentState["isSomethingUp"] = False
        for i in range(y+1, self.columns):
            if not self.cell_map[x,i]:
                self.currentState["isSomethingUp"] = True
                break
        self.currentState["isSomethingDown"] = False
        for i in range(0, y):
            if not self.cell_map[x,i]:
                self.currentState["isSomethingDown"] = True
                break

    def getInitialState(self):
        return deepcopy(self.initialState)

    def _checkEpisodeFinished(self):
        return self.discovered_percentage >= 95.0 or self.stepCounter >= self.configDict["maxActions"]

    def __init_simulation(self):
        description = rospy.ServiceProxy("/euroc_c2_task_selector/start_simulator", StartSimulator)(user_id="C2T03",
                                                                                                    scene_name=self.configDict["task_name"])
        __stopped = False
        rospy.init_node(name="MMLF_Agent")
        self.__publisher = Thread(target=publish_yaml, args=(description.description_yaml,))
        self.__publisher.start()
        task = YamlPars0r.parse_yaml(description.description_yaml)
        self.__base_pose = task.mast_of_cam.base_pose
        self.__pan_tilt_base = task.mast_of_cam.pan_tilt_base

    def stop(self):
        # Stop the simulation
        try:
            __stopped = False
            self.__publisher.join()
            rospy.ServiceProxy("/euroc_c2_task_selector/stop_simulator", StopSimulator)()
        except rospy.ServiceException:
            pass
        finally:
            super(GazeboScanTableEnvironment, self).stop()

    def evaluateAction(self, actionObject):
        action = actionObject["action"]
        previousState = deepcopy(self.currentState)
        x, y = self.camera_index
        self.environmentLog.debug("Executing Action %s at (%d / %d)" % (action.name, x, y))
        reward = action(self)
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
        map = self.cell_map
        p = self.discovered_percentage
        self.__need_update = False

    def camera_at_position(self, x, y):
        return self.camera_index == (x, y)

    def resetTable(self):
        self.reset_map()
        self.__cell_size = None
        self.__cell_map = None
        self.__rows = None
        self.__cols = None
        self.__percent_cleared = 0.0

    @property
    def discovered_percentage(self):
        if self.__need_update:
            response = self.map_percent_cleared()
            self.__percent_cleared = response.percent
        return self.__percent_cleared

    @property
    def cell_map(self):
        if self.__cell_map is None or self.__need_update:
            self.__map = Map.from_msg(self.get_map().map)
            self.__cell_map = numpy.ndarray(shape=(Map.num_of_cells, Map.num_of_cells), dtype=bool)
            for x in range(Map.num_of_cells):
                for y in range(Map.num_of_cells):
                    self.__cell_map[x, y] = self.__map.field[x * Map.num_of_cells + y].state != Cell.Unknown
            self.__need_update = False
        return self.__cell_map

    @property
    def camera_index(self):
        return (0, 0)

    @property
    def cell_size(self):
        if self.__cell_size is None:
            self.__cell_size = self.get_map().map.cell_size
        return self.__cell_size

    @property
    def rows(self):
        if self.__rows is None:
            self.__rows = self.cell_map.shape[0]
        return self.__rows

    @property
    def columns(self):
        if self.__cols is None:
            self.__cols = self.cell_map.shape[1]
        return self.__cols


EnvironmentClass = GazeboScanTableEnvironment
EnvironmentName = "GazeboScanTableEnvironment"
