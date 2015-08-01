#!/usr/bin/env python


# This script will create a visualization of the loaded data in the suturo_learning prolog node
# In order to work, you need to:
#  roslaunch suturo_learning json_prolog.launch
# The script will fetch the relevant data via
# json_prolog calls and write a HTML/JS file with
# a visualization of the abstracted state-action trees
# After you've
#  rosrun suturo_learning visualize_logs.py
# , the output will be placed in `rospack find suturo_learning`\log_visualization\index.html


import roslib; roslib.load_manifest('json_prolog')
import rospy
from json_prolog import json_prolog

class Experiment(object):
    """docstring for Experiment"""
    # def __init__(self):
    #     super(Experiment, self).__init__()
    #     self.name = ""
    #     self.states = []
    #     self.actions = []

    def __init__(self, name="", states=[], actions=[]):
        super(Experiment, self).__init__()
        self.name = name
        self.states = states
        self.actions = actions

    def __str__(self):
        return "Name: " + self.name + ", actions=" + str(self.actions) + ", states = " + str(self.states)
        

def load_data():
    """Return a list of Experiments with loaded data"""
    experimentNames = []
    experimentObjects = []

    prolog = json_prolog.Prolog()
    query = prolog.query("suturo_learning:l_get_robot_experiment(Experiment)")
            # , )

    # Load unique RobotExperiment IDs
    for solution in query.solutions():
        print 'Found solution. Experiment= %s' % (solution['Experiment'])
        experimentNames.append(solution['Experiment'])
    query.finish() 

    # Fetch data for RobotExperiments
    for experiment in experimentNames:
        extracted_data = Experiment()
        query = prolog.query("suturo_learning:get_robot_experiment_name('"+experiment+"',ExperimentName)")
        # TODO: Only first result
        # print "Found " + len(query.solutions()) + " solutions"
        for solution in query.solutions():
            print 'Found Name. ExperimentName= %s' % (solution['ExperimentName'])
        query.finish() 
        extracted_data.name = solution['ExperimentName']

  # get_learningaction_sequence_in_experiment(Experiment, LS), 
  # get_state_sequence_for_action_sequence(LS, SSeq),
        experimentObjects.append(extracted_data)


    return experimentObjects

if __name__ == '__main__':
    try:
        print "hi"
        rospy.init_node('test_json_prolog')
        data = load_data()
        for experiment in data:
            print experiment
        # prolog = json_prolog.Prolog()
        # query = prolog.query("suturo_learning:l_get_robot_experiment(Experiment), suturo_learning:get_robot_experiment_name(Experiment,ExperimentName)")
        # for solution in query.solutions():
        #     print 'Found solution. ExperimentName = %s' % (solution['ExperimentName'])
        # query.finish() 
    except rospy.ROSInterruptException:
        pass
