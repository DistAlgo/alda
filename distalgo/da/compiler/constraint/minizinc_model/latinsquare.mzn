include "globals.mzn";
array[1..n,1..n] of var 1..n: x;
int: n;
constraint 
	forall( i in 1..n )( all_different( j in 1..n )( x[i,j] ) );
constraint 
	forall( j in 1..n )( all_different( i in 1..n )( x[i,j] ) );
solve satisfy;