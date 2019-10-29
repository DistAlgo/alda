include "globals.mzn";
var int: a;
var int: b;
var int: obj_2;
constraint 
	obj_2 = (a + b)
;
constraint 
	( a > b /\ a+b = 10 /\ a >= 0 /\ b >= 0 );
solve satisfy;