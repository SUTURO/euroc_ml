#!/usr/bin/env python
# from gazebo_msgs.msg._ContactState import ContactState
from collections import defaultdict
import rospy
from suturo_head_mover_msgs.srv._SuturoMlFeedPolicy import SuturoMlFeedPolicy, SuturoMlFeedPolicyRequest, \
    SuturoMlFeedPolicyResponse
from suturo_head_mover_msgs.srv._SuturoMlNextAction import SuturoMlNextAction, SuturoMlNextActionRequest, \
    SuturoMlNextActionResponse
from learner import SarsaLambdaLearner
from policy import GreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self):
        self.feedSrv = rospy.Service('SuturoMlHeadLearnerPolicyFeeder', SuturoMlFeedPolicy, self.feedCallback)
        self.feedSrv = rospy.Service('SuturoMlHeadNextAction', SuturoMlNextAction, self.nextActionCallback)
        self.policy = []
        self.q = defaultdict(lambda : 10)
        self.learner = SarsaLambdaLearner()
        self.testactions=[0,1,2,3]
        self.policyMaker = GreedyPolicy(self.q, self.testactions)
        print("SuturoMlHeadLearnerPolicyFeeder started.")

    def feedCallback(self, feedPolicyRequest):
        # r = SuturoMlFeedPolicyRequest()
        # r = self.tranform_policy(data)
        # print(r)
        print("start learning")
        self.q = self.learner.learn(feedPolicyRequest)
        print("learning done.\n new q: \n")
        print(self.q)

        response = SuturoMlFeedPolicyResponse()
        response.success = True
        return response

    def nextActionCallback(self, nextActionRequest):
        # a = SuturoMlNextActionRequest()
        # a.state
        r = SuturoMlNextActionResponse()
        r.action.actionId = self.policyMaker.getNextAction(nextActionRequest.state)
        return r





if __name__ == '__main__':
    rospy.init_node("SuturoMLHeadLearnerPolicyFeederNode", anonymous=True)
    # contact_sub = rospy.Subscriber("/gazebo/contacts", SuturoMlFeedPolicy, callback)
    # s = rospy.Service('SuturoMLHeadLearnerPolicyFeeder', CheckContact, muh)
    muh = SuturoMlHeadLearner()
    rospy.spin()