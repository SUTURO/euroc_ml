:- module(suturo_learning, [
	get_designator_by_type/2,
	get_planned_goals/1
]).

:- owl_parse('package://suturo_learning/owl/suturo_learning.owl').
:- rdf_db:rdf_register_ns(suturo_learning, 'http://knowrob.org/kb/suturo_learning.owl#',     [keep(true)]).
:- use_module(library('knowrob_mongo')).

get_designator_by_type(Type, Designator) :-
    jpl_list_to_array(['designator.TYPE'], QueryKeysArr),
    jpl_list_to_array([Type], QueryValuesArr),
    knowrob_mongo:mongo_interface(DB),
    jpl_call(DB, 'getDesignatorsByPattern', [QueryKeysArr, QueryValuesArr], DesigJavaArr),
    jpl_array_to_list(DesigJavaArr, DesigJavaList),
    member(DesigJava, DesigJavaList),
    jpl_call(DesigJava, 'get', ['_id'], DesigID),
    rdf_split_url('http://knowrob.org/kb/cram_log.owl#', DesigID, Designator).

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
  plan_actions(Action,ListOfActions).


plan_actions(Action, ListOfDependendActions) :-
  precondition_for_action(Action,Precond) ->
    action_for_effect(Precond,PreAction),
    plan_actions(PreAction, S),
    append(S, [PreAction], ListOfDependendActions)
  ;
    ListOfDependendActions = [].



