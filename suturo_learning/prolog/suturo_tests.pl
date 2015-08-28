:- module(suturo_tests, [
    red_cube_grabed/0,
    red_cube_placed/0,
    blue_handle_grabed/0,
    blue_handle_turned/0,
    plan_successful/0,
    all_actions_successful/0,
    all_actions_useful/0
]).

:- use_module(library(suturo_learning)).


red_cube_grabed :-
    once(object_grabed('red_cube')).


red_cube_placed :-
    once(object_placed('1.0')).


blue_handle_grabed :-
    once(object_grabed('blue_handle')).


blue_handle_turned :-
    once(object_turned('2.0')).


plan_successful :-
    once((
        get_learning_sequence(Plan),
        member([_, _, StateAfter, _], Plan),
        nth0(1, StateAfter, Success),
        nth0(2, StateAfter, Placed),
        nth0(3, StateAfter, Turned),
        Success = '1.0',
        Placed = '1.0',
        Turned = '1.0'
    )).


all_actions_successful :-
    once((
        get_learning_sequence(Plan),
        maplist(action_successful, Plan))
    ).
    

all_actions_useful :-
    once((
        get_learning_sequence(Plan),
        maplist(action_useful, Plan))
    ).


object_grabed(ObjectName) :-
    get_learning_sequence(Plan),
    member([_, Action, StateAfter, _], Plan),
    nth0(1, StateAfter, Success),
    sub_string(Action, _, _, _, 'GRAB'),
    sub_string(Action, _, _, _, ObjectName),
    Success = '1.0'.


object_placed(ObjectId) :-
    get_learning_sequence(Plan),
    member([StateBefore, Action, StateAfter, _], Plan),
    nth0(1, StateAfter, Success),
    nth0(0, StateBefore, Object),
    sub_string(Action, _, _, _, 'PLACE-IN-ZONE'),
    Object = ObjectId,
    Success = '1.0'.


object_turned(ObjectId) :-
    get_learning_sequence(Plan),
    member([StateBefore, Action, StateAfter, _], Plan),
    nth0(1, StateAfter, Success),
    nth0(0, StateBefore, Object),
    sub_string(Action, _, _, _, 'TURN'),
    Object = ObjectId,
    Success = '1.0'.


action_successful(ASS) :-
    nth0(2, ASS, StateAfter),
    nth0(1, StateAfter, Success),
    Success = '1.0'.


action_useful(ASS) :-
    nth0(0, ASS, StateBefore),
    nth0(2, ASS, StateAfter),
    StateBefore \= StateAfter.

