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
import rospkg
from json_prolog import json_prolog

# stuff_to_write="""
# 	experiments = [ 
# 		
# 		{ name: 'default', 
# 		nodesArray: [], 
# 		edgesArray : [], 
# 		nodeInformationArray: [],
# 		},
# 
# 		{ name: 'exp-foo', 
# 		nodesArray: [{id: 1, label: 'LOL State'},
#     {id: 2, label: 'State 2'},
#     {id: 3, label: 'State 3'},
#     {id: 4, label: 'State 4'},
#     {id: 5, label: 'State 5'},
#     {id: 6, label: 'Error',   shape: 'diamond', color: 'red'},
#     {id: 7, label: 'Success', shape: 'diamond', color: 'green'},
# 		], 
# 		edgesArray : [
#     {from: 1, to: 3, arrows:'to', label:'Action', font: {align: 'top'}},
#     {from: 1, to: 2, arrows:'to', label:'Action', font: {align: 'top'}},
#     {from: 2, to: 4, arrows:'to', label:'Action', font: {align: 'top'}},
#     {from: 2, to: 5, arrows:'to', label:'Action', font: {align: 'top'}},
#     {from: 5, to: 6, arrows:'to', label:'Outcome', font: {align: 'top'}},
#     {from: 4, to: 7, arrows:'to', label:'Outcome', font: {align: 'top'}},
# 		],
# 		nodeInformationArray: [
# 			"exp-foo-1",
# 			"exp-foo-2",
# 			"exp-foo-3",
# 			"exp-foo-4",
# 			"exp-foo-5",
# 			"exp-foo-6",
# 			"exp-foo-7",
# 		],
# 		},
# 
# 		];
# """
stuff_to_write="""
	experiments = [ 
		
		{ name: 'default', 
		nodesArray: [], 
		edgesArray : [], 
		nodeInformationArray: [],
		},

"""

stuff_to_write_end="""
		];
"""


def js_representation_for_experiment(ExperimentObject):
    """Recreate the js object from the given data, to write it to the visualization webpage sourcecode"""
        # self.name = name
        # self.states = states
        # self.actions = actions
    result = """ { name: '"""+ExperimentObject.name+"""', 
		nodesArray: [""";
    
    state_id = 1
    for s in ExperimentObject.states:
        # print s
        result += "{id: " + str(state_id) + ", label: '" + str(s) + "'},"
        state_id+=1
    # {id: 1, label: 'LOL State'},
    # {id: 2, label: 'State 2'},
    # {id: 3, label: 'State 3'},
    # {id: 4, label: 'State 4'},
    # {id: 5, label: 'State 5'},
    # {id: 6, label: 'Error',   shape: 'diamond', color: 'red'},
    # {id: 7, label: 'Success', shape: 'diamond', color: 'green'},

    result +=	"""], 
		edgesArray : [""";

    action_id = 1
    for a in ExperimentObject.actions:
        action_name = a[1]
        result += "{from: " + str(action_id) + ", to: " + str(action_id+1) + ", arrows:'to', label:'"+ str(action_name) +"', font: {align: 'horizontal'}},"
        action_id += 1
    # {from: 1, to: 3, arrows:'to', label:'Action', font: {align: 'top'}},
    # {from: 1, to: 2, arrows:'to', label:'Action', font: {align: 'top'}},
    # {from: 2, to: 4, arrows:'to', label:'Action', font: {align: 'top'}},
    # {from: 2, to: 5, arrows:'to', label:'Action', font: {align: 'top'}},
    # {from: 5, to: 6, arrows:'to', label:'Outcome', font: {align: 'top'}},
    # {from: 4, to: 7, arrows:'to', label:'Outcome', font: {align: 'top'}},
    result += """ ],
		nodeInformationArray: [""";
    result += """
                        'GOAL was: YYY-1. State: ZZZ. t=12345678',
			'GOAL was: YYY-2. State: ZZZ. t=12345678',
			'GOAL was: YYY-3. State: ZZZ. t=12345678',
			'GOAL was: YYY-4. State: ZZZ. t=12345678',
			'GOAL was: YYY-5. State: ZZZ. t=12345678',
			'GOAL was: YYY-6. State: ZZZ. t=12345678',
			'GOAL was: YYY-7. State: ZZZ. t=12345678',
                        """;
    result += """ ],
		},
                """;
    return result;

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
        print 'Found Experiments. Experiment= %s' % (solution['Experiment'])
        experimentNames.append(solution['Experiment'])
    query.finish() 

    # Fetch data for RobotExperiments
    for experiment in experimentNames:
        extracted_data = Experiment()
        query = prolog.query("suturo_learning:get_robot_experiment_name('"+experiment+"',ExperimentName), suturo_learning:get_learningaction_sequence_in_experiment('"+experiment+"', LS), suturo_learning:get_state_sequence_for_action_sequence(LS, SSeq)")
        # TODO: Only first result
        # print "Found " + len(query.solutions()) + " solutions"
        for solution in query.solutions():
            print 'Found Data for Experiment. ExperimentName= %s' % (solution['ExperimentName'])
            extracted_data.name = solution['ExperimentName']
            extracted_data.actions = solution['LS']
            extracted_data.states = solution['SSeq']
        query.finish() 

  # get_learningaction_sequence_in_experiment(Experiment, LS), 
  # get_state_sequence_for_action_sequence(LS, SSeq),
        experimentObjects.append(extracted_data)


    return experimentObjects

def write_visualization(ExperimentObjects):
    # Load the website template 
    rospack = rospkg.RosPack()
    path = rospack.get_path('suturo_learning')
    template_path = path + "/log_visualization/template.html"

    template_file = open(template_path,'r')
    template_content = template_file.read()
    template_file.close()

    global stuff_to_write
    experiment_selects = ""
    for e in ExperimentObjects:
        stuff_to_write += js_representation_for_experiment(e)
        experiment_selects += "<option value='"+e.name+"'>"+e.name+"</option>"

    stuff_to_write += stuff_to_write_end

    print stuff_to_write

    visualization_content = template_content.replace("--PLACEHOLDER_REPLACE_WITH_ACTUAL_DATA--", stuff_to_write)

    visualization_content = visualization_content.replace("--PLACEHOLDER_REPLACE_WITH_EXPERIMENT_NAMES--", experiment_selects)


    path = rospack.get_path('suturo_learning')
    visualization_path = path + "/log_visualization/index.html"
    visualization_file = open(visualization_path,'w')
    visualization_file.write(visualization_content)
    visualization_file.close()

    data_to_write = "FOOBAR"


    pass

if __name__ == '__main__':
    try:
        print "hi"
        rospy.init_node('test_json_prolog')
        data = load_data()
        for experiment in data:
            print experiment
        write_visualization(data)
        # prolog = json_prolog.Prolog()
        # query = prolog.query("suturo_learning:l_get_robot_experiment(Experiment), suturo_learning:get_robot_experiment_name(Experiment,ExperimentName)")
        # for solution in query.solutions():
        #     print 'Found solution. ExperimentName = %s' % (solution['ExperimentName'])
        # query.finish() 
    except rospy.ROSInterruptException:
        pass
