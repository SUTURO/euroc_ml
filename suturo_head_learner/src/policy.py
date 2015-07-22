import random

__author__ = 'suturo'

class Policy(object):

    def __init__(self, q, actions):
        self.fullActions = actions
        self.actions = map(lambda x: x[1], actions)
        self.q = q

    def getNextAction(self, stateMsg):
        pass

    def updateQ(self, q):
        self.q = q

    def stateToTuple(self, stateMsg):
        stateTuple = []
        for f in stateMsg.featureList:
            stateTuple.append((f.featureName, f.value))
        return tuple(stateTuple)

class EpsilonGreedyPolicy(Policy):

    def __init__(self, q, actions, epsilon=.1):
        super(EpsilonGreedyPolicy,self).__init__(q, actions)
        self.epsilon = epsilon

    def getNextAction(self, stateMsg):
        state = self.stateToTuple(stateMsg)
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

class GreedyPolicy(EpsilonGreedyPolicy):

    def __init__(self, q, actions):
        super(GreedyPolicy,self).__init__(q, actions, 0.0)