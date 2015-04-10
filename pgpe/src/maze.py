# -*- coding: utf-8 -*-
from scipy import *
import sys, time

from pybrain.rl.environments.mazes import Maze, MDPMazeTask
from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q, SARSA
from pybrain.rl.experiments import Experiment
from pybrain.rl.environments import Task


# Tkinter doesn't like to be run
# in thread, so we have to move our magic 
# to a worker thread ...
#
# !!! PLACE YOUR MACHINE LEARNING STUFF HERE !!!!


def worker_thread():
    print "Started worker"
    import pylab
    pylab.gray()
    pylab.ion()

    structure = array([[1, 1, 1, 1, 1, 1, 1, 1, 1],
                      [1, 0, 0, 1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 0, 0, 1, 0, 1],
                    [1, 0, 0, 1, 0, 0, 1, 0, 1],
                    [1, 0, 0, 1, 0, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 1, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 0, 1],
                   [1, 0, 0, 0, 0, 0, 0, 0, 1],
                   [1, 1, 1, 1, 1, 1, 1, 1, 1]])

    environment = Maze(structure, (7, 7))
    controller = ActionValueTable(81, 4)
    controller.initialize(1.)

    learner = Q()
    agent = LearningAgent(controller, learner)

    task = MDPMazeTask(environment)

    experiment = Experiment(task, agent)

    while True:
        experiment.doInteractions(100)
        agent.learn()
        agent.reset()

        pylab.pcolor(controller.params.reshape(81,4).max(1).reshape(9,9))
        pylab.draw()

    # controller = ActionValueTable(numStates, numActions)
    # learner = Q()
    # agent = LearningAgent(controller, learner)
    # task = ScanTableTask(env)
    # exp = Experiment(task, agent)
    # iteration = 0
    # # ready to go, start the process
    # while True:
    #     exp.doInteractions(10000)
    #     print("--- Iteration: %d / Score: %.2f" % (iteration, env.discovered_percentage))
    #     agent.learn()
    #     agent.reset()
    #     env.reset()
    #     iteration += 1


# root = Tk()
# # define the environment
# num_rows = 20
# num_cols = 20
# env = ScanTableEnv(rows=num_rows,
#                    cols=num_cols,
#                    action_delay_time=0.0)
#
#
# gui = GUI(root, env)
# # Execute a new thread to do stuff beside the GUI
# # This should hold your magic machine learning code
# start_new_thread(worker_thread,(env, env.numStates, env.numActions))
#
# root.mainloop()
# root.destroy()
worker_thread()
