#!/usr/bin/env python
import rospy
from suturo_head_mover_msgs.srv._SuturoMlNextAction import SuturoMlNextAction, SuturoMlNextActionRequest, \
    SuturoMlNextActionResponse
from learner import SarsaLambdaLearner
from json_prolog.json_prolog import Prolog
from policy import EpsilonGreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self):
        self.feedSrv = rospy.Service('SuturoMlHeadNextAction', SuturoMlNextAction, self.nextActionCallback)
        self.policy = []
        # self.q = defaultdict(lambda : 10)
        # self.actions = filter(lambda x: x[0].startswith('Const'), [(a,s) for a,s in vars(SuturoMlAction).iteritems()])
        self.actions = ["GRAB-SIDE blue_handle",
                        "GRAB-SIDE red_cube",
                        "TURN",
                        "OPEN-GRIPPER",
                        "GRAB-TOP blue_handle",
                        "GRAB-TOP red_cube",
                        "PLACE-IN-ZONE",
                        "HAMMERTIME"]
        self.policyMaker = EpsilonGreedyPolicy(self.q, self.actions, .0)
        self.learner = SarsaLambdaLearner(self.policyMaker)
        self.q = self.learner.get_q()
        # self.policyMaker = ReverseGreedyPolicy(self.q, self.actions)
        rospy.wait_for_service('json_prolog/simple_query')
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
	    print sol
            for a,b in sol.iteritems():
                for policy in b:
                    self.q = self.learner.learn(policy)
                    self.policyMaker.updateQ(self.q)
        print("learning done.\n new q: \n")
        for a,b in self.q.iteritems():
            print a, "  ", b


if __name__ == '__main__':
    rospy.init_node("SuturoMlHeadLearner", anonymous=True)
    muh = SuturoMlHeadLearner()
    muh.doTheShit()
    rospy.spin()
