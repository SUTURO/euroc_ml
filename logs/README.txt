Experiment einlesen:
  cd exp-XXXXXXXXXXXXXX
  rosrun rosprolog rosprolog suturo_learning
  owl_parse('cram_log.owl').
  # Log-Inhalt testen. Das Log sollte ausgefuehrte Aktionen beinhalten.
  owl_individual_of(A,knowrob:'CRAMAction').

Attribute einer konkreten Aktion auslesen:
?- owl_individual_of(A,knowrob:'CRAMAction'),owl_has(A,P,O).
A = log:'CRAMAction_UNga7hSXnq8klADh',
P = knowrob:endTime,
O = log:'timepoint_79.495' ;
A = log:'CRAMAction_UNga7hSXnq8klADh',
P = knowrob:taskContext,
O = literal(type(xsd:string,'ANONYMOUS-TOP-LEVEL')) ;
A = log:'CRAMAction_UNga7hSXnq8klADh',
P = knowrob:taskSuccess,
O = literal(type(xsd:boolean,true)) ;
A = log:'CRAMAction_UNga7hSXnq8klADh',
P = knowrob:startTime,
O = log:'timepoint_1.965'
