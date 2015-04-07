import numpy
import time
from actions import MoveToAction, ScanTableAction


class ScanTableSimulation(object):
    """Main class for the simulation"""

    def __init__(self, environment, simulate_delay_in_action=False, action_delay=1):
        super(ScanTableSimulation, self).__init__()
        self.__env = environment
        self.__env.reset_cells_and_camera()
        self.__simulate_delay_in_action = simulate_delay_in_action
        self.__action_delay_time = action_delay  # delay 1 sec by default, if enabled
        self.__last_executed_action = -1
        self.__observer = None
        self.reset_update_flag()

    def update_occured(self):
        """Returns True, if the cells has been updated lately or the camera index changed and reset_update_flag() has not been called since then. Right now, this flag will be set everytime an action will be executed"""
        return self.__state_update

    def reset_update_flag(self):
        """Reset the flag indicating cell changes to False"""
        self.__state_update = False

    def set_observer(self, observer):
        """Set an observer. Most likely the GUI in our case"""
        self.__observer = observer

    def update_observer(self):
        """Call the update method on the observer"""
        if self.__observer is not None:
            self.__observer.update()
