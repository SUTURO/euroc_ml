#!/usr/bin/env python
from collections import defaultdict
import rospy
from suturo_head_mover_msgs.msg._SuturoMlAction import SuturoMlAction
from suturo_head_mover_msgs.srv._SuturoMlNextAction import SuturoMlNextAction, SuturoMlNextActionRequest, \
    SuturoMlNextActionResponse
from learner import SarsaLambdaLearner
from policy import GreedyPolicy
from json_prolog import Prolog
from policy import EpsilonGreedyPolicy
from policy import ReverseGreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self):
        self.feedSrv = rospy.Service('SuturoMlHeadNextAction', SuturoMlNextAction, self.nextActionCallback)
        self.policy = []
        # self.q = defaultdict(lambda : 10)
        self.learner = SarsaLambdaLearner()
        self.q = self.learner.get_q()
        # self.actions = filter(lambda x: x[0].startswith('Const'), [(a,s) for a,s in vars(SuturoMlAction).iteritems()])
        self.actions = ["GRAB-SIDE BLUE_HANDLE",
                        "GRAB-SIDE RED_CUBE",
                        "TURN",
                        "OPEN-GRIPPER",
                        "GRAB-TOP BLUE_HANDLE",
                        "GRAB-TOP RED_CUBE",
                        "PLACE-IN-ZONE",
                        "HAMMERTIME"]
        # self.policyMaker = EpsilonGreedyPolicy(self.q, self.actions, .0)
        self.policyMaker = ReverseGreedyPolicy(self.q, self.actions)
        self.prolog = Prolog()
        print("SuturoMlHeadLearnerPolicyFeeder started.")


    def nextActionCallback(self, nextActionRequest):
        r = SuturoMlNextActionResponse()
        r.action.action = self.policyMaker.getNextAction(nextActionRequest.state)
        return r

    def doTheShit(self):
        q = self.prolog.query("suturo_learning:get_learning_sequence(A)")
        print("start learning")
        for sol in q.solutions():
            for a,b in sol.iteritems():
                for policy in b:
                    self.q = self.learner.learn(policy)
                    self.policyMaker.updateQ(self.q)
        print("learning done.\n new q: \n")
        for a,b in self.q.iteritems():
            print a, "  ", b


if __name__ == '__main__':
    rospy.init_node("SuturoMLHeadLearnerPolicyFeederNode", anonymous=True)
    # contact_sub = rospy.Subscriber("/gazebo/contacts", SuturoMlFeedPolicy, callback)
    # s = rospy.Service('SuturoMLHeadLearnerPolicyFeeder', CheckContact, muh)
    muh = SuturoMlHeadLearner()
    muh.doTheShit()
    rospy.spin()