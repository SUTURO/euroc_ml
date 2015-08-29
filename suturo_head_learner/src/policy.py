import random
import rospy

__author__ = 'suturo'


# Seed the Random generator
random.seed()


class Policy(object):

    def __init__(self, q, actions):
        # self.fullActions = actions
        # self.actions = ["GRAB-SIDE", "TURN", "OPEN-GRIPPER", "GRAB-TOP", "PLACE-IN-ZONE", "HAMMERTIME"]
        self.actions = actions
        # self.actions = map(lambda x: x[1], actions)
        self.q = q

    def getNextAction(self, stateMsg):
        if not type(stateMsg) is tuple:
            return self.getNextAction2(self.stateToTuple(stateMsg))
        return self.getNextAction2(stateMsg)

    def getNextAction2(self, state):
        pass

    def updateQ(self, q):
        self.q = q

    def stateToTuple(self, stateMsg):
        print stateMsg.featureList
        return stateMsg.featureList

class EpsilonGreedyPolicy(Policy):

    def __init__(self, q, actions, epsilon=.1):
        super(EpsilonGreedyPolicy,self).__init__(q, actions)
        rospy.loginfo("Epsilon Greedy = "+str(epsilon))
        self.epsilon = epsilon

    def getNextAction2(self, state):
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
