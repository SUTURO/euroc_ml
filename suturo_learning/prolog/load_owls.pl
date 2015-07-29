%%Dir ist absoluter Pfad

load_owls(Dir, Blacklist) :-
	%% print('Start load dir for::  '),
	%% print(Dir),
	%% print('  --  '),
	%% (exists_directory(Dir) -> print('is Dir\n'); print('is not a Dir\n'), fail),	
	exists_directory(Dir),
	directory_files(Dir,Dir2),
	%% print(Dir2),
	%% print('\n'),
	member(DirElem,Dir2),
	DirElem \= '.',
	DirElem \= '..',
	DirElem \= 'current-experiment',
	member(BlackElem, Blacklist),
	DirElem \= BlackElem,
	%% print('check: '),
	%% print(DirElem),
	%% print('\n'),
	string_concat(Dir, '/', HalfDirElem),
	string_concat(HalfDirElem, DirElem, FullDirElem),
	load_owls(FullDirElem, Blacklist).
	%% print('load_owls end\n').

load_owls(Dir, Blacklist) :-
	%% print('Start load owls for::  '),
	%% print(Dir),
	%% print('  --  '),
	%% (exists_file(Dir) -> print('is File\n'); print('is not a File\n'), fail),
	exists_file(Dir),
	%% (end_with(Dir, 'owl') -> print('is owl\n'); print('is not an owl\n'), fail),
	end_with(Dir, 'owl'),
	owl_parse(Dir),
	print(Dir),
	print(' loaded\n\n').

end_with(String, EndString) :-
	atomic_list_concat(L,'.',String), 
	length(L,I), 
	nth1(I, L, E),
	E = EndString.