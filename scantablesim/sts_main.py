# -*- coding: utf-8 -*-
from Tkinter import *
from thread import start_new_thread
import time
from sts import ScanTableSimulation, ScanTableAction
from sts_gui import GUI


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

    def performAction(self, action):
        """ A filtered mapping towards performAction of the underlying environment. """                
        self.env.performAction(action)
        
    def getObservation(self):
        """ A filtered mapping to getSample of the underlying environment. """
        sensors = self.env.getSensors()
        return sensors
    
    def getReward(self):
        """ Compute and return the current reward (i.e. corresponding to the last action performed) """
        # reward = raw_input("Enter reward: ")
        current_cells_discovered = self.sts.cells_discovered()
        # Only give rewards for increasing discovery rates
        reward = current_cells_discovered - self.lastreward

        if reward>0:
          print "Reward granted:" + str(reward)
        
        # retrieve last reward, and save current given reward
        cur_reward = self.lastreward
        self.lastreward = reward
    
        return cur_reward

    @property
    def indim(self):
        return self.env.indim
    
    @property
    def outdim(self):
        return self.env.outdim

from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q
from pybrain.rl.experiments import Experiment
from pybrain.rl.explorers import EpsilonGreedyExplorer

# Tkinter doesn't like to be run
# in thread, so we have to move our magic 
# to a worker thread ...
#
# !!! PLACE YOUR MACHINE LEARNING STUFF HERE !!!!
def worker_thread(gui,sts):
    print "Started worker"
    av_table = ActionValueTable(51, 7)
    av_table.initialize(0.)
    
    # define Q-learning agent
    # learner = Q(0.5, 0.5)
    learner = Q()
    # learner._setExplorer(EpsilonGreedyExplorer(0.0))
    agent = LearningAgent(av_table, learner)
    
    # define the environment
    env = ScanTableEnv(sts)
    
    # define the task
    task = ScanTableTask(env,sts)
    
    # finally, define experiment
    experiment = Experiment(task, agent)
    
    # ready to go, start the process
    while True:
      experiment.doInteractions(50)
      agent.learn()
      print "Calling reset"
      agent.reset()
      env.reset()
      time.sleep(1)

    # while 1:
    #   print "Sleeping Worker"
    #   sts.action(ScanTableAction.MOVE_RIGHT_BY_5)
    #   sts.action(ScanTableAction.SCAN_TABLE)


root = Tk()
sts = ScanTableSimulation()

gui = GUI(root,sts)
# sts.set_observer(gui)
# Simulate delay in the action of our robot
sts.set_simulate_delay_in_action(True)
sts.set_action_delay_time_in_s(0.1)

# Execute a new thread to do stuff beside the GUI
# This should hold your magic machine learning code
start_new_thread(worker_thread,(gui,sts,))

root.mainloop()
root.destroy() 
