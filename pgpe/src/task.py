from pybrain.rl.environments.episodic import EpisodicTask


class ScanTableTask(EpisodicTask):
    """ A task is associating a purpose with an environment. It decides how to evaluate the observations, potentially returning reinforcement rewards or fitness values.
    Furthermore it is a filter for what should be visible to the agent.
    Also, it can potentially act as a filter on how actions are transmitted to the environment. """

    def __init__(self, environment):
        super(ScanTableTask, self).__init__(environment)
        # we will store the last reward given, remember that "r" in the Q learning formula is the one from the last interaction, not the one given for the current interaction!
        self.__reward = -1

    def performAction(self, action):
        """ A filtered mapping towards performAction of the underlying environment. """
        self.__reward = self.env.performAction(action)

    def getObservation(self):
        """ A filtered mapping to getSample of the underlying environment. """
        sensors = self.env.getSensors()
        return sensors

    def getReward(self):
        """ Compute and return the current reward (i.e. corresponding to the last action performed) """
        # reward = raw_input("Enter reward: ")
        return self.__reward