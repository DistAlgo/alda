'python' 'distalgo' 'RHrule' 'rule' 'rule_all' 'rolerule' 'rolerule_all'

for nq in 50 100 150 200 250 300 350 400 450 500; do
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=python; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=distalgo; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=RHrule; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=rule; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=rev_rule; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=rule; done;
	for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=rev_rule; done;
done

for nq in 50 100 150 200 250;do
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=python; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=RHrule; done;
done


for nq in 50 100 150 200 250 300 350 400 450 500; do
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=python; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=RHrule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=400 --numq=50 --q=$nq --mode=rev_rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=python; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=RHrule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=500 --numq=50 --q=$nq --mode=rev_rule; done;
done

for nr in 550 600 650 700 750 800 850 900 950 1000; do
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=python; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=RHrule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=rev_rule; done;
done

#!/bin/bash

for nq in 50 100 150 200 250 300 350 400 450 500; do
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=600 --numq=50 --q=$nq --mode=RHrule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=600 --numq=50 --q=$nq --mode=rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=600 --numq=50 --q=$nq --mode=rev_rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=600 --numq=50 --q=$nq --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=600 --numq=50 --q=$nq --mode=python; done;
done

for nr in 900; do
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=python; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=distalgo; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=RHrule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=rule; done;
	for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=50 --mode=rev_rule; done;
done



