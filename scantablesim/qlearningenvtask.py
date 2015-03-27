# Thanks to http://simontechblog.blogspot.de/2010/08/pybrain-reinforcement-learning-tutorial_21.html

from pybrain.rl.environments.environment import Environment
from scipy import zeros
import sys

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

class ScanTableEnvCameraScoreState(ScanTableEnv):
<<<<<<< HEAD
  """This environment is pretty similar to ScanTableEnv, but it has more dimensions and different sensor values"""
  # the number of sensor values the environment produces
  # This will be the current score to start
  # TODO: Incorporate the camera_index into the state
  outdim = 2550 # e.g. this is sts.cell_totals * max_camera_idx

  def __init__(self, sts):
    super(ScanTableEnvCameraScoreState, self).__init__(sts)
    self.sts = sts

    
=======
    """This environment is pretty similar to ScanTableEnv, but it has more dimensions and different sensor values"""
>>>>>>> magic
    def __init__(self, sts):
        super(ScanTableEnvCameraScoreState, self).__init__(sts)
        self.sts = sts

        # the number of sensor values the environment produces
        # This will be the current score to start
        # TODO: Incorporate the camera_index into the state
        # outdim = 2550 # e.g. this is sts.cell_totals * max_camera_idx
        self.outdim = 7

    def getSensors(self):
        return [float(self.sts.see() )]
    

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
        self.step = 0
        self.last_reward_step = 0
        self.fails = 0
        print environment.outdim

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
        # reward = (current_cells_discovered - self.last_cells_discovered)/50
        reward = current_cells_discovered / 50
        # print self.last_cells_discovered
        if reward>0:
<<<<<<< HEAD
          reward = 1.0 # normalize reward
          print "Reward granted at step("+str(self.step)+"):" + str(reward)
          self.last_reward_step = self.step
        else:
          reward = 0.0
=======
            # rewards = 1 # normalize reward
            # print "Reward granted at step("+str(self.step)+"):" + str(reward)
            self.last_reward_step = self.step
            self.fails = 0
        else:
            self.fails += 0.01
        if reward < 0.9:
            reward = -(self.fails)
        else:
            print "done after ", str(self.step)," steps"
>>>>>>> magic
        # else:
        #   if current_cells_discovered <45: # Punish only if the agent hasn't discovered almost the complete map 
        #     print (self.step - self.last_reward_step)
        #     if (self.step - self.last_reward_step) > 5: # n Actions without any reward? punish the agent
        #       print "Punishment for gammeling"
        #       reward = -50
        # 
        # retrieve last reward, and save current given reward
        cur_reward = self.lastreward
        self.lastreward = reward
        self.last_cells_discovered = current_cells_discovered

        self.step += 1
        # return reward
        sys.stdout.write(str(cur_reward) + ":")
        return cur_reward

    def reset(self):
        self.lastreward = 0
        self.last_cells_discovered = 0
        self.step = 0
        self.last_reward_step = 0
        self.fails = 0

    @property
    def indim(self):
        return self.env.indim
    
    @property
    def outdim(self):
        return self.env.outdim

