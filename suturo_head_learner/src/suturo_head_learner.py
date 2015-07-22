#!/usr/bin/env python
# from gazebo_msgs.msg._ContactState import ContactState
from collections import defaultdict
import rospy
from suturo_head_mover_msgs.msg._SuturoMlAction import SuturoMlAction
from suturo_head_mover_msgs.srv._SuturoMlFeedPolicy import SuturoMlFeedPolicy, SuturoMlFeedPolicyRequest, \
    SuturoMlFeedPolicyResponse
from suturo_head_mover_msgs.srv._SuturoMlNextAction import SuturoMlNextAction, SuturoMlNextActionRequest, \
    SuturoMlNextActionResponse
from learner import SarsaLambdaLearner
from policy import GreedyPolicy
from policy import EpsilonGreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self):
        self.feedSrv = rospy.Service('SuturoMlHeadLearnerPolicyFeeder', SuturoMlFeedPolicy, self.feedCallback)
        self.feedSrv = rospy.Service('SuturoMlHeadNextAction', SuturoMlNextAction, self.nextActionCallback)
        self.policy = []
        self.q = defaultdict(lambda : 10)
        self.learner = SarsaLambdaLearner()
        self.actions = filter(lambda x: x[0].startswith('Const'), [(a,s) for a,s in vars(SuturoMlAction).iteritems()])
        self.policyMaker = EpsilonGreedyPolicy(self.q, self.actions, .0)
        print("SuturoMlHeadLearnerPolicyFeeder started.")

    def feedCallback(self, feedPolicyRequest):
        print("start learning")
        self.q = self.learner.learn(feedPolicyRequest)
        self.policyMaker.updateQ(self.q)
        print("learning done.\n new q: \n")
        print(self.q)

        response = SuturoMlFeedPolicyResponse()
        response.success = True
        return response

    def nextActionCallback(self, nextActionRequest):
        r = SuturoMlNextActionResponse()
        r.action.actionId = self.policyMaker.getNextAction(nextActionRequest.state)
        return r





if __name__ == '__main__':
    rospy.init_node("SuturoMLHeadLearnerPolicyFeederNode", anonymous=True)
    # contact_sub = rospy.Subscriber("/gazebo/contacts", SuturoMlFeedPolicy, callback)
    # s = rospy.Service('SuturoMLHeadLearnerPolicyFeeder', CheckContact, muh)
    muh = SuturoMlHeadLearner()
    rospy.spin()