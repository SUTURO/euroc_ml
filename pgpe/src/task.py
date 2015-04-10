from pybrain.rl.environments.task import Task
import numpy


class ScanTableTask(Task):
    """ A task is associating a purpose with an environment. It decides how to evaluate the observations, potentially returning reinforcement rewards or fitness values.
    Furthermore it is a filter for what should be visible to the agent.
    Also, it can potentially act as a filter on how actions are transmitted to the environment. """

    __hasMoved = False
    __scanned = 0.0

    def performAction(self, action):
        old_pose = numpy.array(self.env.camera_index)
        old_scan = self.env.discovered_percentage
        super(ScanTableTask, self).performAction(int(action))
        new_pose = numpy.array(self.env.camera_index)
        new_scan = self.env.discovered_percentage
        self.__hasMoved = (new_pose != old_pose).any()
        self.__scanned = new_scan - old_scan

    def getReward(self):
        """ compute and return the current reward (i.e. corresponding to the last action performed) """
        reward = 0
        if not self.__hasMoved and self.__scanned == 0:
            reward = -1
        elif self.__scanned != 0:
            reward = self.__scanned / 100.
        print("Reward: %.2f" % reward)
        return reward
