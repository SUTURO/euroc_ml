from copy import deepcopy
import numpy
from multiprocessing import Process, Value
from euroc_c2_msgs.srv import StartSimulator, StopSimulator
from geometry_msgs.msg._PoseStamped import PoseStamped
import rospy
from suturo_environment_msgs.srv import GetMap, ResetMap, GetPercentCleared
from std_msgs import msg as std_msgs
from mmlf.framework.protocol import EnvironmentInfo
from mmlf.environments.single_agent_environment import SingleAgentEnvironment
from mmlf.framework.spaces import StateSpace, ActionSpace
from mmlf.worlds.gazo_scan_table.actions import GazeboActions
from suturo_planning_search.cell import Cell
from suturo_planning_manipulation.transformer import Transformer
from suturo_planning_search.map import Map
from mmlf_msgs.srv import TransformerService, TransformerServiceResponse
from mmlf.framework.observables import FloatStreamObservable
import time

__author__ = 'hansa'


class MMLFNode(Process):
    def __init__(self, yaml, stopped):
        super(MMLFNode, self).__init__()
        self.__yaml = yaml
        self.__stopped = stopped

    def run(self):
        rospy.init_node("MMLFNode")
        parser = rospy.Publisher("/suturo/startup/yaml_pars0r_input", std_msgs.String, latch=True)
        rospy.Service("/mmlf/transform_to", TransformerService, self.__handle_transform)
        self.__transformer = Transformer()
        r = rospy.Rate(1)  # 1Hz
        while not self.__stopped.value:
            parser.publish(data=self.__yaml)
            r.sleep()
    
    def __handle_transform(self, msg):
        response = TransformerServiceResponse()
        response.pose = self.__transformer.transform_to(msg.pose)
        return response


class GazeboScanTableEnvironment(SingleAgentEnvironment):

    DEFAULT_CONFIG_DICT = {
        "minPan": -0.65,
        "maxPan": 0.6,
        "minTilt": 0.50,
        "maxTilt": 1.40,
        "stepsPan": 4,
        "stepsTilt": 4,
	    "percentCleared": 95.0,
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

        self.__cell_map = None
        self.__need_update = True
        self.__rows = None
        self.__cols = None
        self.__cell_size = None
        self.__percent_cleared = 0.0
        self.__update_index = True
        self.__map = None
        self.__reward = 0
        self.__scans = 0
        self.pan = 0
        self.tilt = 0.5
        self.scanObservable = FloatStreamObservable(title='%s Scans' % self.__class__.__name__,
                                  time_dimension_name='Episode',
                                  value_name='Number of Scans')

        self.get_map = rospy.ServiceProxy(Map.NAME_SERVICE_GET_MAP, GetMap)
        self.reset_map = rospy.ServiceProxy(Map.NAME_SERVICE_RESET_MAP, ResetMap)
        self.map_percent_cleared = rospy.ServiceProxy("/suturo/environment/get_map_percent_cleared", GetPercentCleared)
        self.__transform_to = rospy.ServiceProxy("/mmlf/transform_to", TransformerService)
        # Initialize the simulation
        self.__init_simulation()

        oldStyleStateSpace = {
           # "x": ("discrete", [0, self.rows]),
           # "y": ("discrete", [0, self.columns]),
            "isScanned": ("discrete", [True, False]),
            "isLeftDown": ("discrete", [True, False]),
            "isRightDown": ("discrete", [True, False]),
            "isLeftUp": ("discrete", [True, False]),
            "isRightUp": ("discrete", [True, False])
        }
        self.stateSpace = StateSpace()
        self.stateSpace.addOldStyleSpace(oldStyleStateSpace, limitType="soft")

        self.__actions = GazeboActions(self.configDict["minPan"],
                                self.configDict["maxPan"],
                                self.configDict["minTilt"],
                                self.configDict["maxTilt"],
                                self.configDict["stepsPan"],
                                self.configDict["stepsTilt"])
        oldStyleActionSpace = {
            "action": ("discrete", self.__actions.actions)
        }

        x, y = self.camera_index
        self.actionSpace = ActionSpace()
        self.actionSpace.addOldStyleSpace(oldStyleActionSpace)
        self.initialState = {
         #   "x": x,
         #   "y": y,
            "isScanned": True,
            "isLeftDown": True,
            "isRightDown": True,
            "isLeftUp": True,
            "isRightUp": True
        }
        self.currentState = deepcopy(self.initialState)
        if useGUI:
            from mmlf.gui.viewers import VIEWERS
            from mmlf.worlds.gazo_scan_table.environments.gazebo_table_viewer import GazeboTableViewer
            VIEWERS.addViewer(lambda: GazeboTableViewer(self), "GazeboTable Viewer")

    def check_range(self,r=1):
        result = False
        posx, posy = self.camera_index
        for y in range(max(0, posy-r),min(posy+r,self.columns)):
            for x in range(max(0,posx-r),min(posx+r, self.rows)):
                result = result or  not self.__cell_map[x,y]
        return result

    def check_new_state(self):
        posx, posy = self.camera_index
        self.currentState["isLeftDown"] = False
        for y in range(posy):
            for x in range(posx):
                if not self.__cell_map[x, y]:
                    self.currentState["isLeftDown"] = True
                    break
            if self.currentState["isLeftDown"]:
                break
        self.currentState["isRightDown"] = False
        for y in range(posy):
            for x in range(posx+1, self.rows):
                if not self.__cell_map[x, y]:
                    self.currentState["isRightDown"] = True
                    break
            if self.currentState["isRightDown"]:
                break
        self.currentState["isLeftUp"] = False
        for y in range(posy+1, self.columns):
            for x in range(posx):
                if not self.__cell_map[x, y]:
                    self.currentState["isLeftUp"] = True
                    break
            if self.currentState["isLeftUp"]:
                break
        self.currentState["isRightUp"] = False
        for y in range(posy+1, self.columns):
            for x in range(posx+1, self.rows):
                if not self.__cell_map[x, y]:
                    self.currentState["isRightUp"] = True
                    break
            if self.currentState["isRightUp"]:
                break

    def getInitialState(self):
        return deepcopy(self.initialState)

    def _checkEpisodeFinished(self):
        return self.discovered_percentage >= self.configDict["percentCleared"] or self.stepCounter >= 500


    def __init_simulation(self):
        description = rospy.ServiceProxy("/euroc_c2_task_selector/start_simulator", StartSimulator)(user_id="C2T03",
                                                                                                    scene_name=self.configDict["task_name"])
        self.__stop_publisher = Value("b", False)
        self.__publisher = MMLFNode(description.description_yaml, self.__stop_publisher)
        self.__publisher.start()
        time.sleep(2)

    def update_index(self):
        self.__update_index = True

    def stop(self):
        # Stop the simulation
        try:
            try:
                self.__stop_publisher.value = True
                if not self.__publisher.join(timeout=2):
                    self.__publisher.terminate()
                    self.__publisher.join(2)
            except rospy.ROSInterruptException:
                pass
            try:
                rospy.ServiceProxy("/euroc_c2_task_selector/stop_simulator", StopSimulator)()
            except rospy.ServiceException:
                pass
        finally:
            super(GazeboScanTableEnvironment, self).stop()

    def evaluateAction(self, actionObject):
        action = actionObject["action"]
        previousState = deepcopy(self.currentState)
        x, y = self.pan, self.tilt
        posx, posy = self.camera_index
        reward = self.__actions.performAction(action, self)

        if action == "scan":
            self.__scans += 1
        self.__reward += reward
        self.stepCounter += 1
        self.check_new_state()

        self.environmentLog.debug("Executed Action %s Pos: (%.2f / %.2f) Reward: %d" % (action, x, y, reward))

        self.currentState["isScanned"] = self.cell_map[posx, posy]
        # self.currentState["isScanned"] = self.check_range()

        episodeFinished = self._checkEpisodeFinished()

        if episodeFinished:
            #reward = 100 if self.discovered_percentage >= self.configDict["percentCleared"] else -100
            reward = self.discovered_percentage ** 3 / 5000
            self.environmentLog.info("Episode %d lasted for %d steps; reward=%d; cleared=%d" % (self.episodeCounter, self.stepCounter, reward, self.__percent_cleared))
            self.episodeLengthObservable.addValue(self.episodeCounter,
                                                  self.stepCounter)
            self.returnObservable.addValue(self.episodeCounter, self.__reward)
            self.scanObservable.addValue(self.episodeCounter, self.__scans)
            self.stepCounter = 0
            self.episodeCounter += 1
            self.currentState = self.getInitialState()
            self.resetTable()

        self.trajectoryObservable.addTransition(previousState, action,
                                                reward, self.currentState,
                                                episodeTerminated=episodeFinished)
        return {
            "reward": reward,
            "terminalState": self.currentState if episodeFinished else None,
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
        self.__reward = 0
        self.__scans = 0
        self.pan = 0
        self.tilt = 0.5
        self.__actions.move_cam(pan=self.pan, tilt=self.tilt)

    @property
    def discovered_percentage(self):
        c = 0.
        for y in range(self.columns):
            for x in range(self.rows):
                if self.__cell_map[x, y]:
                    c += 1.
        self.__percent_cleared = (c / (self.columns * self.rows)) * 100
        # if self.__percent_cleared is None or self.__need_update:
        #     response = self.map_percent_cleared()
        #     self.__percent_cleared = response.percent * 100
        #     self.environmentLog.debug("Discovered Percent: %.2f" % self.__percent_cleared)
        return self.__percent_cleared

    @property
    def cell_map(self):
        if self.__cell_map is None or self.__need_update:
            self.__map = Map.from_msg(self.get_map().map)
            self.__cell_map = numpy.ndarray(shape=(Map.num_of_cells, Map.num_of_cells), dtype=bool)
            for y in range(Map.num_of_cells):
                for x in range(Map.num_of_cells):
                    if x < 24 and y < 24:
                        self.__cell_map[x, y] = True
                    else:
                        self.__cell_map[x, y] = self.__map.field[y * Map.num_of_cells + x].state != Cell.Unknown
        return self.__cell_map

    @property
    def camera_index(self):
        # Transform the pan and tilt into global coordinates
        c = PoseStamped()
        c.header.frame_id = "sdepth"
        c.pose.orientation.w = 1
        cx = deepcopy(c)
        cx.pose.position.x = 1
        c = self.__transform_to(pose=c).pose
        cx = self.__transform_to(pose=cx).pose

        r = (cx.pose.position.x - c.pose.position.x,
             cx.pose.position.y - c.pose.position.y,
             cx.pose.position.z - c.pose.position.z)
        s = float(-c.pose.position.z) / r[2]
        (x,y) = (c.pose.position.x + s * r[0], c.pose.position.y + s * r[1])

        if self.__map is None:
            cell_map = self.cell_map
        y, x = self.__map.coordinates_to_index(x,y)
        self.__update_index = False
        if x < 0:
            x = 0
        elif x >= self.rows:
            x = self.rows - 1
        if y < 0:
            y = 0
        elif y >= self.columns:
            y = self.columns -1
        return x, y

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
