from abc import abstractmethod
import random

__author__ = 'suturo'

class Policy(object):

    def __init__(self, q, actions):
        self.actions = actions
        self.q = q
        pass

    def getNextAction(self, state):
        pass

class GreedyPolicy(Policy):

    def getNextAction(self, state):
        muh = 0.00001
        max_a = []
        for a in self.actions:
            q_vel = self.q[(state, a)]
            if len(max_a) == 0 or q_vel > self.q[(state, max_a[0])]+ muh:
                max_a = [a]
            elif self.q[(state, max_a[0])] - muh < q_vel < self.q[(state, max_a[0])] + muh:
                max_a.append(a)
        return random.choice(max_a)

class EpsilonGreedyPolicy(Policy):

    def __init__(self, q, actions, epsilon):
        super(EpsilonGreedyPolicy,self).__init__(q, actions)
        self.epsilon = epsilon

    def getNextAction(self, state):
        # Select action using epsilon-greedy action selection
        if random.random() < self.epsilon:
            return random.choice(self.actions)

        muh = 0.00001
        max_a = []
        for a in self.actions:
            q_vel = self.q[(state, a)]
            if len(max_a) == 0 or q_vel > self.q[(state, max_a[0])]+ muh:
                max_a = [a]
            elif self.q[(state, max_a[0])] - muh < q_vel < self.q[(state, max_a[0])] + muh:
                max_a.append(a)
        return random.choice(max_a)
