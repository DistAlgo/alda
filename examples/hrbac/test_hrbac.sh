for q in $(seq 50 50 500); do
	for mode in 'rule' 'rolerule' 'transRH' 'python' 'distalgo'; do
		for ((n=0;n<1;n++)); do python3 -m da --message-buffer-size=409600 --rule hrbac.da --numr=500 --numq=50 --q=$q --mode=$mode; done;
	done;
done;