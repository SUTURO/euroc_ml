# -*- coding: utf-8 -*-
from Tkinter import *
from thread import start_new_thread
from pybrain.rl.agents import LearningAgent
from pybrain.rl.experiments.experiment import Experiment
from pybrain.rl.learners import Q, ActionValueTable
from environment import ScanTableEnv
from gui import GUI
from task import ScanTableTask


# Tkinter doesn't like to be run
# in thread, so we have to move our magic 
# to a worker thread ...
#
# !!! PLACE YOUR MACHINE LEARNING STUFF HERE !!!!


def worker_thread(env, numStates, numActions):
    print "Started worker"

    controller = ActionValueTable(numStates, numActions)
    learner = Q()
    agent = LearningAgent(controller, learner)
    task = ScanTableTask(env)
    exp = Experiment(task, agent)
    iteration = 0
    # ready to go, start the process
    while True:
        exp.doInteractions(1000)
        print("--- Iteration: %d / Score: %.2f" % (iteration, env.discovered_percentage))
        agent.learn()
        agent.reset()
        env.reset()
        iteration += 1


root = Tk()
# define the environment
num_rows = 20
num_cols = 20
env = ScanTableEnv(rows=num_rows,
                   cols=num_cols,
                   action_delay_time=0.01)


gui = GUI(root, env)
# Execute a new thread to do stuff beside the GUI
# This should hold your magic machine learning code
start_new_thread(worker_thread,(env, env.numStates, env.numActions))

root.mainloop()
root.destroy() 
