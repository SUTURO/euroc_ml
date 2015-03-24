# -*- coding: utf-8 -*-
from Tkinter import *
from thread import start_new_thread
import time
from sts import ScanTableSimulation, ScanTableAction
from sts_gui import GUI
from qlearningenvtask import ScanTableEnv, ScanTableTask

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
      print "---- Final score of this iteration: " + str(sts.cells_discovered()) + "----"
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
