from collections import defaultdict

__author__ = 'suturo'

class Learner(object):
    def __init__(self, q_init_value=10):
        self.q = defaultdict(lambda : q_init_value)

    def learn(self, feedPolicyRequest):
        return self.q

    def get_q(self):
        return self.q

    def tranform_policy(self, feedPolicyRequest):
        p = []
        for e in feedPolicyRequest.policy.policyEntrys:
            state = []
            for f in e.state.featureList:
                state.append((f.featureName, f.value))
            # action
            p.append((tuple(state),e.action.actionId,e.reward))
        return p

class SarsaLambdaLearner(Learner):

    def __init__(self, q_init_value=10, alpha=.1, gamma=.9, l=.9):
        super(SarsaLambdaLearner, self).__init__(q_init_value)
        self.q = defaultdict(lambda : 10)
        self.e = defaultdict(int)
        self.alpha = alpha
        self.gamma = gamma
        self.l = l

    def learn(self, feedPolicyRequest):
        policy = self.tranform_policy(feedPolicyRequest)
        for i, (s,a,r) in enumerate(policy):
            if i == len(policy) -1:
                break
            next_state, next_action, egal = policy[i+1]
            delta = r + self.gamma * self.q[(next_state,next_action)] - self.q[(s,a)]
            self.e[(s, a)] = self.e[(s, a)] + 1
            for (s1,a1) in self.e.iterkeys():
                    self.q[(s1,a1)] = self.q[(s1,a1)] + self.alpha * delta * self.e[(s1,a1)]
                    self.e[(s1,a1)] = self.l * self.gamma * self.e[(s1,a1)]
        return self.q

    def get_q(self):
        return self.q
