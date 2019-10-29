include "globals.mzn";
array[1..K] of var 0..K: pieces;
array[1..K,1..N] of var int: items;
var int: obj;
int: L;
int: K;
int: N;
array[1..N] of int: i_length;
array[1..N] of int: i_demand;
constraint 
	obj = sum([ pieces[k] | k in 1..K ]);
constraint 
	forall( k in 1..K,i in 1..N )( items[k,i] >= 0 );
constraint 
	forall( i in 1..N )( sum([ items[k,i]*pieces[k] | k in 1..K ]) >= i_demand[i] );
constraint 
	forall( k in 1..K )( sum([ items[k,i]*i_length[i] | i in 1..N ]) <= L );
solve minimize obj;