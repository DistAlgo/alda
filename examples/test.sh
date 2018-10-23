
for nr in 1000; do
	for nq in 50 100 150 200 250 300 350 400 450 500; do
		for mode in 'RHrule' 'rule' 'rev_rule' 'distalgo' 'python'; do
			for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=$nq --mode=$mode; done;
		done;
	done;
done;