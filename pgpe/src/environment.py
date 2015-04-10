# Thanks to http://simontechblog.blogspot.de/2010/08/pybrain-reinforcement-learning-tutorial_21.html
import numpy

from pybrain.rl.environments.environment import Environment

# An environment reflects the changes that will be done 
# by an agent that acts in it.
# In this context, the tablesimulation respresents the world and therefore 
# the environment
from random import randint
import actions
import time


class ScanTableEnv(Environment):

    __actions = [actions.MoveRightAction,
                 actions.MoveLeftAction,
                 actions.MoveUpAction,
                 actions.MoveDownAction,
                 actions.ScanTableAction]

    def __init__(self, rows=1, cols=50, camera_fov_width=2, camera_fov_height=1, action_delay_time=0.0):
        self.__rows = rows
        self.__cols = cols
        self.__camera_fov_width = camera_fov_width  # How many pixels can the camera see to the left and right?
                                                    # A value of 2 means, that it can see the pixel
                                                    # at self.camera_index and 2 pixels left plus 2 pixel right from it
        self.__camera_fov_height = camera_fov_height
        self.__action_delay_time = action_delay_time
        self.reset_cells_and_camera()


    def reset_cells_and_camera(self):
        """docstring for reset_cells_and_camera"""
        # print "-------------Resetting STS---------------"
        # self.table_cells[0] = self.CELL_UNKNOWN
        self.__table_cells = numpy.zeros(shape=(self.__rows, self.__cols), dtype=bool, order="C")
        # for a in self.table_cells:
        # print(a)
#        self.__camera_index = (numpy.random.randint(0, self.__rows, size=1)[0],
#                               numpy.random.randint(0, self.__cols, size=1)[0]) # Where is the camera looking at?
        self.__camera_index = (randint(0, self.__rows), randint(0, self.__cols))
        self.__state_update = True

    def getSensors(self):
        """
        Give 9 different states according to where the cam is located:
        0 = top left
        1 = top middle
        2 = top right
        3 = middle left
        4 = middle middle
        5 = middle right
        6 = bottom left
        7 = bottom middle
        8 = bottom right

        :return: The state of the cam
        """
        def top():
            return self.__camera_index[0] - self.__camera_fov_height <= 0
        def bottom():
            return self.__camera_index[0] + self.__camera_fov_height >= self.cell_map.shape[0]
        def left():
            return self.__camera_index[1] - self.__camera_fov_width <= 0
        def right():
            return self.__camera_index[1] - self.__camera_fov_width >= self.cell_map.shape[1]

        state = None

        if top() and left():
            state = 0
        elif top() and not left() and not right():
            state = 1
        elif top() and right():
            state = 2
        elif not top() and not bottom() and left():
            state = 3
        elif not top() and not bottom() and not left() and not right():
            state = 4
        elif not top() and not bottom() and right():
            state = 5
        elif bottom() and left():
            state = 6
        elif bottom() and not left() and not right():
            state = 7
        elif bottom() and right():
            state = 8

        x ,y = self.__camera_index
        state = (state << 1) + int(self.__table_cells[x, y])
        return numpy.array([state])

    def performAction(self, action):
        # """ perform an action on the world that changes it's internal state (maybe stochastically).
        #     :key action: an action that should be executed in the Environment. 
        #     :type action: by default, this is assumed to be a numpy array of doubles
        # """
        # print "Action performed: ", action
        """Execute an action with the virtual camera"""
        action = self.__actions[action]()
        print("Perfoming Action: %s" % action)
        action.perform(self)
        time.sleep(self.__action_delay_time)

    def reset(self):
        """Reinit the world"""
        self.reset_cells_and_camera()

    def __update_if_idx_valid(self, x, y, value):
        """Write a value into self.tablen_cells[idx], if the idx is in bounds"""
        # Check if the idx is in the current row
        if x >= 0 and y >= 0 and x < self.__table_cells.shape[0] and y < self.__table_cells.shape[1]:
            self.__table_cells[x, y] = value

    def scan_table(self):
        """Execute the SCAN_TABLE action. Should be execute from action()"""
        curr_x, curr_y = self.__camera_index
        for x in range(curr_x - self.__camera_fov_height, curr_x + 1 + self.__camera_fov_height):
            for y in range(curr_y - self.__camera_fov_width, curr_y + 1 + self.__camera_fov_width):
                self.__update_if_idx_valid(x, y, True)

    def move_to(self, x, y):
        if x >= 0 and y >= 0 and x < self.__table_cells.shape[0] and y < self.__table_cells.shape[1]:
            self.__camera_index = (x, y)

    def camera_at_position(self, x, y):
        return self.__camera_index == (x, y)

    @property
    def discovered_percentage(self):
        """cells_discovered / cells_total"""
        return self.__table_cells.sum() / float(self.__table_cells.size) * 100


    @property
    def cell_map(self):
        return self.__table_cells

    @property
    def numStates(self):
        return 17

    @property
    def numActions(self):
        return len(self.__actions)

    @property
    def camera_index(self):
        return self.__camera_index