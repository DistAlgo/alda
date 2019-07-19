#!/bin/bash
for dataset in "numpy" "scipy" "pandas" "matplotlib" "sympy" "django" "sklearn" "torch"; do
	for mode in "rule" "combine" "distalgo" "python"; do
		for ((n=0;n<20;n++)); do python3 -m da ast_analysis_rule.da $dataset $mode; done;
	done;
done;
