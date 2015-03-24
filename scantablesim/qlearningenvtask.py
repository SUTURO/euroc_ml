# Thanks to http://simontechblog.blogspot.de/2010/08/pybrain-reinforcement-learning-tutorial_21.html

from pybrain.rl.environments.environment import Environment
from scipy import zeros

# An environment reflects the changes that will be done 
# by an agent that acts in it.
# In this context, the tablesimulation respresents the world and therefore 
# the environment
class ScanTableEnv(Environment):


    # the number of action values the environment accepts
    # MOVE_RIGHT_BY_*, MOVE_LEFT_BY_*, SCAN_TABLE
    indim = 7
    
    # the number of sensor values the environment produces
    # This will be the current score to start
    # TODO: Incorporate the camera_index into the state
    outdim = 51 # e.g. this is sts.cell_totals right now
    
    def __init__(self, sts):
      self.sts = sts

    def getSensors(self):
        return [float(self.sts.cells_discovered() ),]
                    
    def performAction(self, action):
        # """ perform an action on the world that changes it's internal state (maybe stochastically).
        #     :key action: an action that should be executed in the Environment. 
        #     :type action: by default, this is assumed to be a numpy array of doubles
        # """
        # print "Action performed: ", action
        self.sts.action(action)

    def reset(self):
        """Reinit the world"""
        print "Reset in environment"
        self.sts.reset_cells_and_camera()

from scipy import clip, asarray

from pybrain.rl.environments.task import Task
from numpy import *

class ScanTableTask(Task):
    """ A task is associating a purpose with an environment. It decides how to evaluate the observations, potentially returning reinforcement rewards or fitness values. 
    Furthermore it is a filter for what should be visible to the agent.
    Also, it can potentially act as a filter on how actions are transmitted to the environment. """

    def __init__(self, environment,sts):
        """ All tasks are coupled to an environment. """
        self.env = environment
        self.sts = sts
        # we will store the last reward given, remember that "r" in the Q learning formula is the one from the last interaction, not the one given for the current interaction!
        self.lastreward = 0
        self.last_cells_discovered = 0

    def performAction(self, action):
        """ A filtered mapping towards performAction of the underlying environment. """                
        self.env.performAction(action)
        
    def getObservation(self):
        """ A filtered mapping to getSample of the underlying environment. """
        sensors = self.env.getSensors()
        return sensors
    
    def getReward(self):
        """ Compute and return the current reward (i.e. corresponding to the last action performed) """
        current_cells_discovered = self.sts.cells_discovered()
        # Only give rewards for increasing discovery rates
        reward = current_cells_discovered - self.last_cells_discovered

        if reward>0:
          # rewards = 1 # normalize reward
          print "Reward granted:" + str(reward)
        
        # retrieve last reward, and save current given reward
        cur_reward = self.lastreward
        self.lastreward = reward
        self.last_cells_discovered = current_cells_discovered
    
        return cur_reward

    @property
    def indim(self):
        return self.env.indim
    
    @property
    def outdim(self):
        return self.env.outdim

