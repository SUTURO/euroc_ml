% Dir ist absoluter Pfad
:- module(suturo_owls, [
    load_owls/2,
    load_owls/1
]).

load_owls(Dir) :-
	findall(_,load_owl(Dir,['']),_).

load_owls(Dir, Blacklist):-
	findall(_,load_owl(Dir,Blacklist),_).

load_owl(Dir, Blacklist) :-
	exists_directory(Dir),
	directory_files(Dir,Dir2),
	member(DirElem,Dir2),
	DirElem \= '.',
	DirElem \= '..',
	DirElem \= 'current-experiment',
	member(BlackElem, Blacklist),
	DirElem \= BlackElem,
	string_concat(Dir, '/', HalfDirElem),
	string_concat(HalfDirElem, DirElem, FullDirElem),
	load_owl(FullDirElem, Blacklist).

load_owl(Dir, _) :-
	exists_file(Dir),
	end_with(Dir, 'owl'),
	owl_parse(Dir),
	print(Dir),
	print(' loaded\n\n').

end_with(String, EndString) :-
	atomic_list_concat(L,'.',String), 
	length(L,I), 
	nth1(I, L, E),
	E = EndString.
