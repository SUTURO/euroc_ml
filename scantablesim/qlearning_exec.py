from pybrain.rl.learners.directsearch.reinforce import Reinforce
from pybrain.rl.learners.valuebased.nfq import NFQ
from qlearningenvtask import ScanTableEnv, ScanTableTask, ScanTableEnvCameraScoreState, SimonTask

from pybrain.rl.learners.valuebased import ActionValueTable
from pybrain.rl.agents import LearningAgent
from pybrain.rl.learners import Q, SARSA
from pybrain.rl.experiments import Experiment
from pybrain.rl.explorers import EpsilonGreedyExplorer
import time

def qlearningStateEqualsScore(gui,sts,interactions):
    av_table = ActionValueTable(51, 7)
    av_table.initialize(1.)
    
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
   
    iteration = 0
    # ready to go, start the process
    while True:
      experiment.doInteractions(interactions)
      agent.learn()
      print "---- Final score of this iteration("+str(iteration)+"): " + str(sts.cells_discovered()) + "----"
      agent.reset()
      env.reset()
      task.step = 0
      task.last_reward_step = 0
      iteration+=1
      # time.sleep(0.5)
      
      
def qlearningStateEqualsScoreAndCamera(gui,sts,interactions):
    av_table = ActionValueTable(2550, 7)
    av_table.initialize(1.)
    
    sts.set_simulate_delay_in_action(False)
    # define Q-learning agent
    # learner = Q(0.5, 0.5)
    learner = Q()
    # learner = SARSA()
    # learner._setExplorer(EpsilonGreedyExplorer(0.0)) # the smaller the parameter, the less random the actions will be
    # learner._setExplorer(EpsilonGreedyExplorer(0.3,0.9))
    agent = LearningAgent(av_table, learner)
    
    # define the environment
    env = ScanTableEnvCameraScoreState(sts)

    # define the task
    task = ScanTableTask(env,sts)
    
    # finally, define experiment
    experiment = Experiment(task, agent)
    iteration = 0 
    # ready to go, start the process
    while True:
      experiment.doInteractions(interactions)
      agent.learn()
      print ""
      print "---- Final score of this iteration("+str(iteration)+"): " + str(sts.cells_discovered()) + "----"
      agent.reset()
      env.reset()
      task.reset()
      iteration += 1
      # time.sleep(0.5)

def qlearningSimon(gui,sts,interactions):
    av_table = ActionValueTable(8, 7)
    av_table.initialize(1.)

    sts.set_simulate_delay_in_action(False)
    # define Q-learning agent
    # learner = Q(0.5, 0.5)
    learner = Reinforce()
    # learner = SARSA()
    # learner._setExplorer(EpsilonGreedyExplorer(0.0)) # the smaller the parameter, the less random the actions will be
    # learner._setExplorer(EpsilonGreedyExplorer(0.3,0.9))
    agent = LearningAgent(av_table, learner)

    # define the environment
    env = ScanTableEnvCameraScoreState(sts)

    # define the task
    task = SimonTask(env,sts)

    # finally, define experiment
    experiment = Experiment(task, agent)
    iteration = 0
    # ready to go, start the process
    while True:
      experiment.doInteractions(interactions)
      agent.learn()
      print ""
      print "---- Final score of this iteration("+str(iteration)+"): " + str(sts.cells_discovered()) + "----"
      agent.reset()
      env.reset()
      task.reset()
      iteration += 1
      # time.sleep(0.5)
      
      
