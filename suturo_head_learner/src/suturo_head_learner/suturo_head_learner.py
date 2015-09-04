#!/usr/bin/env python
from collections import defaultdict
from copy import deepcopy
from optparse import OptionParser

import rospy
from std_msgs.msg._String import String
from suturo_head_mover_msgs.srv._SuturoMlNextAction import SuturoMlNextAction, SuturoMlNextActionResponse

# from suturo_head_learner.policy import ImbaPolicy
# from suturo_head_learner.learner import SarsaLambdaLearner
from json_prolog.json_prolog import Prolog
from learner import SarsaLambdaLearner
from policy import Haxx0rPolicy
from policy import EpsilonGreedyPolicy

__author__ = 'ichumuh'

class SuturoMlHeadLearner(object):

    def __init__(self, epsilon, lambda_=0.5):
        self.feedSrv = rospy.Service('SuturoMlHeadNextAction', SuturoMlNextAction, self.nextActionCallback)
        self.policyPringPub = rospy.Publisher('SuturoMlPolicy', String, queue_size=10, latch=True)
        self.policy = []
        # self.q = defaultdict(lambda : 10)
        # self.actions = filter(lambda x: x[0].startswith('Const'), [(a,s) for a,s in vars(SuturoMlAction).iteritems()])
        self.actions = ["GRAB-SIDE blue_handle",
                        "GRAB-SIDE red_cube",
                        "TURN",
                        "OPEN-GRIPPER",
                        "GRAB-TOP blue_handle",
                        "GRAB-TOP red_cube",
                        "PLACE-IN-ZONE"]
        self.q = None
        self.policyMaker = EpsilonGreedyPolicy(self.q, self.actions, epsilon)
        # self.policyMaker = Haxx0rPolicy(self.actions)
        self.learner = SarsaLambdaLearner(self.policyMaker, l=lambda_)
        self.q = self.learner.get_q()
        self.policyMaker.updateQ(self.q)
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
        for solution in q.solutions():
            # print sol
            policy = solution["A"]
            self.q = self.learner.learn(policy)
            self.policyMaker.updateQ(self.q)
        print("learning done.\n")

        ppp = defaultdict(lambda : ((-999999999999,-999999999999),))
        tmp_q = deepcopy(self.q)
        for s in self.q.iterkeys():
            state = s[0]
            for a in self.actions:
                b = tmp_q[(state,a)]
                if ppp[state][0][1] == b and not ppp[state].__contains__((a,b)):
                    ppp[state] = ppp[state] + ((a,b),)
                elif ppp[state][0][1] < b:
                    ppp[state] = ((a,b),)

        # for a,b in self.q.iteritems():
        #     print a,b
        muh = []
        for a,b in ppp.iteritems():
            muh.append((a, b))

        def cmpmuh(x,y):
            for i in range(len(x[0])):
                if x[0][i] > y[0][i]:
                    return 1
                elif x[0][i] < y[0][i]:
                    return -1
            if x[1][1] > y[1][1]:
                return 1
            elif x[1][1] < y[1][1]:
                return -1
            return 0

        muh.sort(cmp=cmpmuh)
        msg = ""
        for a in muh:
            print a
            msg += str(a[0]) +"\n" +str(a[1]) + "\n\n"
        s = String(msg)
        self.policyPringPub.publish(s)

    def pub_policy(self):
        pass


if __name__ == '__main__':
    rospy.init_node("SuturoMlHeadLearner", anonymous=True)
    parser = OptionParser()
    parser.add_option("--epsilon", dest="epsilon", default=0., type="float")
    (options, args) = parser.parse_args()
    # print "asdasd ", options.alpha
    muh = SuturoMlHeadLearner(options.epsilon)
    muh.doTheShit()
    rospy.spin()
