for nr in 100 150 200 250 300 350 400 450 500; do
	for nq in 50; do
		for mode in 'RHrule'; do
			for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 hrbac.da --numr=$nr --numq=50 --q=$nq --mode=$mode; done;
		done;
	done;
done;