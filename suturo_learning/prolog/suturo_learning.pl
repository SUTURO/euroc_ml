:- module(knowrob_robosherlock,
  [
    foo/1,
  ]).

:- register_ros_package(knowrob_common).
:- register_ros_package(knowrob_actions).
:- register_ros_package(knowrob_srdl).

# :- owl_parse('package://knowrob_robosherlock/owl/rs_components.owl').
#:- rdf_db:rdf_register_ns(rs_components, 'http://knowrob.org/kb/rs_components.owl#',     [keep(true)]).

set_current_robot(A):- A is 2.
