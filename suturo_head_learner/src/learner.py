from collections import defaultdict

__author__ = 'suturo'

class Learner(object):
    def __init__(self, q_init_value=1):
        self.q = defaultdict(lambda : q_init_value)

    def learn(self, feedPolicyRequest):
        return self.q

    def get_q(self):
        return self.q

    def tranform_policy(self, policy):
        p = []
        for s, a, ns, r in policy:
            state = []
            for elem in s:
                state.append(float(elem))
            p.append((tuple(state), str(a), r, float(ns)))
        return p

class SarsaLambdaLearner(Learner):

    def __init__(self, policy, q_init_value=1, alpha=.1, gamma=.9, l=.9):
        super(SarsaLambdaLearner, self).__init__(q_init_value)
        self.policy = policy
        self.q = defaultdict(lambda : 1)
        self.e = defaultdict(int)
        self.alpha = alpha
        self.gamma = gamma
        self.l = l

    def learn(self, feedPolicyRequest):
        policy = self.tranform_policy(feedPolicyRequest)
        print policy
        self.policy.updateQ(self.q)
        for i, (s,a,r,ns) in enumerate(policy):
            if i == len(policy) -1:
                next_action = self.policy.getNextAction(ns)
                next_state = ns
            else:
                next_state, next_action, egal = policy[i+1]
            delta = r + self.gamma * self.q[(next_state,next_action)] - self.q[(s,a)]
            self.e[(s, a)] = self.e[(s, a)] + 1
            for (s1,a1) in self.e.iterkeys():
                self.q[(s1,a1)] = self.q[(s1,a1)] + self.alpha * delta * self.e[(s1,a1)]
                self.e[(s1,a1)] = self.l * self.gamma * self.e[(s1,a1)]
            self.policy.updateQ(self.q)
        return self.q

    def get_q(self):
        return self.q
