:- module(suturo_learning, [
	get_planned_goals/1,
    get_actions_for_object/2
]).

:- use_module(library(http/json)).
:- use_module(library(http/json_convert)).

:- owl_parse('package://suturo_learning/owl/suturo_learning.owl').
:- rdf_db:rdf_register_ns(suturo_learning, 'http://knowrob.org/kb/suturo_learning.owl#',     [keep(true)]).
:- rdf_db:rdf_register_ns(knowrob, 'http://knowrob.org/kb/knowrob.owl#',     [keep(true)]).
:- use_module(library('knowrob_mango')).

get_planned_goals(Goals) :-
  Goals = [['side_grab','blue_handle'],['turn',''],['open_gripper',''],['top_grab','red_cube'], ['place_in_zone','']].


% Generate multiple plans
goal_list_generator(Goals):-
  Goals = [['top_grab','red_cube'], ['place_in_zone',''],['open_gripper',''],['side_grab','blue_handle'],['turn','']].

goal_list_generator(Goals):-
  Goals = [['top_grab','red_cube'], ['place_in_zone',''],['open_gripper',''],['top_grab','blue_handle'],['turn','']].

% TODO Construct goal list
get_planned_goals_w_alt(Goals) :-
  goal_list_generator(Goals),
  \+ failed_goal_list(Goals).
%
%   Make procedures dynamically known. Dirty hack :(
:- assert(failed_goal_list([])).
:- assert(successful_goal_list([])).

% Remember which goal lists have been succesful
assert_outcome_for_goal_list(Goals,Outcome) :-
  Outcome = 'success' ->
    assert(successful_goal_list(Goals));
    % else
    assert(failed_goal_list(Goals)).

clear_asserts:-
  retractall(successful_goal_list(_)),
  retractall(failed_goal_list(_)),
  assert(failed_goal_list([])),
  assert(successful_goal_list([])).

action_for_effect(Effect,Action) :-
  owl_subclass_of(Action, 'http://knowrob.org/kb/suturo_learning.owl#Action'),
  class_properties(Action,'http://knowrob.org/kb/suturo_learning.owl#postActionEffect',Effect).

precondition_for_action(Action,Precondition) :-
  owl_subclass_of(Action, suturo_learning:'Action'),class_properties(Action,suturo_learning:'preCondition',Precondition).

% plan(Effect, ListOfActions) :-
%   action_for_effect(Effect,Action), 
%   precondition_for_action(Action,Precond) ->
%     plan(Effect,
%     append([ListOfActions, 
plan_actions_for_goal(Goal,ListOfActions) :-
  action_for_effect(Goal,Action), 
  plan_actions(Action,ListOfPreActions),
  append(ListOfPreActions, [Action], ListOfActions).


plan_actions(Action, ListOfDependendActions) :-
  precondition_for_action(Action,Precond) ->
    action_for_effect(Precond,PreAction),
    plan_actions(PreAction, S),
    append(S, [PreAction], ListOfDependendActions)
  ;
    ListOfDependendActions = [].


get_actions_for_object(Action, Description) :-
    mang_desig_matches(Action, Description).


% REASONING PART
% ANALYZE THE INCOMING LOGS FOR FACTS
%
% Rules prefixed with an l operate directly on the log data
%
% Don't forget to load a log before you use these functions!
l_get_robot_experiment(X):-
  owl_individual_of(X,knowrob:'RobotExperiment').

% Get sub actions for a given entity
l_get_sub_actions(X,Sub):-
  owl_has(X,knowrob:'subAction',Sub).

l_get_next_actions(X,Next):-
  owl_has(X,knowrob:'nextAction',Next).

l_get_type_of_entity(X,Type):-
  owl_has(X,rdf:'type',Type).

% Example types:
% knowrob:'PerformOnProcessModule' 
% knowrob:'WithFailureHandling'
% knowrob:'CRAMPerform'
% knowrob:'CRAMAchieve'
% knowrob:'CRAMAction'
% knowrob:'CRAMDesignator'
% knowrob:'TimePoint'
% knowrob:'RobotExperiment'
% knowrob:'AnnotationInformation'
l_get_entities_of_type(X,Type):-
  owl_has(X,rdf:'type', Type).

l_get_task_success(X,Success):-
  owl_has(X,knowrob:'taskSuccess',Success).

% LEARNINGACTIONS will now be defined as the achieved CRAM Goals
get_learningactions_in_experiment(Experiment, La):-
  l_get_robot_experiment(Experiment), !,
  l_get_sub_actions(Experiment,La),
  l_get_type_of_entity(La,'http://knowrob.org/kb/knowrob.owl#CRAMAchieve').

get_learningactions(La):-
  get_learningactions_in_experiment(_, La).

get_learningaction_sequence_in_experiment(Experiment,LaS):-
  bagof([La,Str], 
  (
    get_learningactions_in_experiment(Experiment,La),
    owl_has(La,'http://knowrob.org/kb/knowrob.owl#goalContext',Str)
  ), ActionSequenceDirty),
  maplist(clean_name_of_action_in_tupel, ActionSequenceDirty, LaS).

get_learningaction_sequence(LaS):-
  get_learningaction_sequence_in_experiment(_,LaS).

clean_name_of_action_in_tupel([X,Y],Output):-
Y=(literal(type(_,Name))), Output=[X,Name].

% extract_bool

get_learningaction_name([_, Y], Name) :-
    Y=(literal(type(_, Name))).

get_action_name(X, Name) :-
    owl_has(X, knowrob:'goalContext', Str),
    Str=(literal(type(_, Action))),
    % parse the action name, Action may be something like (GRAB-SIDE ?OBJECT)
    % or (TURN)
    % split at the whitespace
    atomic_list_concat(L1, ' ', Action),
    nth1(1, L1, Tmp1),
    % split the "("
    atomic_list_concat(L2, '(', Tmp1),
    nth1(2, L2, Tmp2),
    % split the ")"
    atomic_list_concat(L3, ')', Tmp2),
    nth1(1, L3, Name). 

% Extract the name of an action from a learning action sequence generated
% by get_learningaction_sequence
% Index begins at 1
get_learningaction_sequence_name(LaS, IndexOfAction, Name):-
  get_learningaction_sequence(LaS), nth1(IndexOfAction,LaS,Elem), get_learning_action_name(Elem, Name).

% Resolves to crucial information in our context:
% - The designator
% - taskSuccess
% - endTime
% - startTime
% - goalContext
% learningaction_info(La,P,Info):-
%   get_learningactions(La),
%   P = 'http://knowrob.org/kb/knowrob.owl#designator';
%   P = 'http://knowrob.org/kb/knowrob.owl#taskSuccess';
%   P = 'http://knowrob.org/kb/knowrob.owl#endTime';
%   P = 'http://knowrob.org/kb/knowrob.owl#startTime';
%   P = 'http://knowrob.org/kb/knowrob.owl#goalContext',
%   owl_has(La,P,Info).


