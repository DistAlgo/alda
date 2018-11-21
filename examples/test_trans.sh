for nume in 100 200 300 400 500 600 700 800 900 1000; do
	for mode in 'rule'; do
		for ((n=0;n<5;n++)); do python3 -m da --message-buffer-size=409600 trans.da --nume=$nume --mode=$mode  >> trans\_$mode\_$nume.csv; done;
	done;
done;