%%Dir sollte zu sr_experimental fuehren.
%%laedt alle owl in ordnern, die in Dir sind
load_owls(Dir) :-
	directory_files(Dir,Dir2),
	member(DirElem,Dir2),
	exists_directory(DirElem),
	DirElem \= '.',
	DirElem \= '..',
	DirElem \= 'current-experiment',
	load_owls2(DirElem).

%% laedt alle owls in NewDir
load_owls2(NewDir) :-
	working_directory(OldDir, NewDir),
	expand_file_name("*.owl",F),
	member(OWLF, F),
	owl_parse(OWLF),
	working_directory(_, OldDir).

%% owl_individual_of(A,knowrob:'CRAMAction').