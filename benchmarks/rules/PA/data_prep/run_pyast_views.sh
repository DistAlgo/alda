#!/bin/bash

# run in PA/data_prep, after downloading repos.

datasets="blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy"

for data in $datasets; do
    python ../../pyAnalysis/data_prepare/pyast_views.py $data
done
