for ((n=0;n<10;n++)); do 
	for q in $(seq 50 50 500); do
		for mode in 'rule' 'rolerule' 'transRH' 'authUR' 'python' 'distalgo'; do #'rule' 'rolerule' 'authUR' 'python' 'distalgo' 'RHrule' 
			python3 -m da --message-buffer-size=409600 -r --rule launcher.da --numr=500 --numq=50 --q=$q --mode=$mode; 
		done;
	done;
done;
# for ((n=0;n<10;n++)); do python3 -m da --message-buffer-size=409600 -r --rule launcher.da --numr=500 --numq=50 --q=500 --mode='transRH'; done;