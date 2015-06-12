:- module(suturo_learning, [
	get_designator_by_type/2
]).

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

