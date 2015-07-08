Experiment einlesen:
  cd exp-XXXXXXXXXXXXXX
  rosrun rosprolog rosprolog suturo_learning
  owl_parse('cram_log.owl').
  # Log-Inhalt testen. Das Log sollte ausgefuehrte Aktionen beinhalten.
  owl_individual_of(A,knowrob:'CRAMAction').

