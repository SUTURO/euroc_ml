
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
def qlearningStateEqualsScore(gui,sts,interactions):
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
      experiment.doInteractions(interactions)
      agent.learn()
      print "---- Final score of this iteration: " + str(sts.cells_discovered()) + "----"
      print "Calling reset"
      agent.reset()
      env.reset()
      time.sleep(1)
