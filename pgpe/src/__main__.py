# -*- coding: utf-8 -*-
from Tkinter import *
from thread import start_new_thread
from pybrain.rl.agents import LearningAgent
from pybrain.rl.experiments.experiment import Experiment
from pybrain.rl.learners import Q, ActionValueTable
import actions
from environment import ScanTableEnv
from gui import GUI
from task import ScanTableTask


# Tkinter doesn't like to be run
# in thread, so we have to move our magic 
# to a worker thread ...
#
# !!! PLACE YOUR MACHINE LEARNING STUFF HERE !!!!


def worker_thread(env):
    print "Started worker"
    av_table = ActionValueTable(env.total_cells, env.number_of_actions)
    # av_table.initialize(1.)

    # define Q-learning agent
    # learner = Q(0.5, 0.5)
    learner = Q()
    # learner._setExplorer(EpsilonGreedyExplorer(0.0))
    agent = LearningAgent(av_table, learner)

    # define the task
    task = ScanTableTask(env)

    # finally, define experiment
    experiment = Experiment(task, agent)

    iteration = 0
    # ready to go, start the process
    while True:
      experiment.doInteractions(250)
      agent.learn()
      print("---- Final score of this iteration (%s): %s ----" %(iteration, env.discovered_cells))
      agent.reset()
      env.reset()
      task.step = 0
      task.last_reward_step = 0
      iteration += 1

root = Tk()

# define the environment
num_rows = 5
num_cols = 50
a = [actions.MoveToAction(x, y) for x in range(num_rows) for y in range(num_cols)]
a.append(actions.ScanTableAction())

env = ScanTableEnv(actions=a,
                   rows=num_rows,
                   cols=num_cols,
                   action_delay_time=0.0)
gui = GUI(root, env)
# Execute a new thread to do stuff beside the GUI
# This should hold your magic machine learning code
start_new_thread(worker_thread,(env,))

root.mainloop()
root.destroy() 
