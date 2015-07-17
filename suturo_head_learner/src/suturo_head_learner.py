#!/usr/bin/env python
# from gazebo_msgs.msg._ContactState import ContactState
from collections import defaultdict
import rospy
from suturo_head_mover_msgs.srv._SuturoMlFeedPolicy import SuturoMlFeedPolicy, SuturoMlFeedPolicyRequest, \
    SuturoMlFeedPolicyResponse
from suturo_head_learner.src.learner import SarsaLambdaLearner
from suturo_head_learner.src.policy import GreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self):
        self.feedSrv = rospy.Service('SuturoMlHeadLearnerPolicyFeeder', SuturoMlFeedPolicy, self.callback)
        self.policy = []
        self.q = defaultdict(lambda : 10)
        self.learner = SarsaLambdaLearner()
        self.testactions=[10,20,30]
        self.policyMaker = GreedyPolicy(self.q, self.testactions)
        print("SuturoMlHeadLearnerPolicyFeeder started.")

    def callback(self, data):
        # r = SuturoMlFeedPolicyRequest()
        r = self.tranform_policy(data)
        print(r)
        print("start learning")
        self.q = self.learner.learn(r)
        print("learning done.\n new q: \n")
        print(self.q)

        response = SuturoMlFeedPolicyResponse()
        response.success = True
        return response

    def tranform_policy(self, policy):
        p = []
        for e in policy.policy.policyEntrys:
            state = []
            for f in e.state:
                state.append((f.featureName, f.value))
            # action
            p.append((tuple(state),e.action,e.reward))
        return p



if __name__ == '__main__':
    rospy.init_node("SuturoMLHeadLearnerPolicyFeederNode", anonymous=True)
    # contact_sub = rospy.Subscriber("/gazebo/contacts", SuturoMlFeedPolicy, callback)
    # s = rospy.Service('SuturoMLHeadLearnerPolicyFeeder', CheckContact, muh)
    muh = SuturoMlHeadLearner()
    rospy.spin()