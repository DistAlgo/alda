#!/bin/bash
for nume in $(seq 10 10 100); do
	for mode in 'rule' 'rev_rule' 'distalgo' 'python'; do
		for ((n=0;n<10;n++)); do python -m da -r --message-buffer-size=409600 --rules launcher.da --nume=$nume --mode=$mode; done;
	done;
done;

for nume in $(seq 200 100 1000); do
	for mode in 'rule' 'rev_rule'; do
		for ((n=0;n<10;n++)); do python -m da -r --message-buffer-size=409600 --rules launcher.da --nume=$nume --mode=$mode; done;
	done;
done;