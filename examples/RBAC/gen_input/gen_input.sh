#!/bin/bash

# run this script in examples/RBAC/gen_input
# you can pass a parameter regenerate input files in examples/hrbac

# first run the code to generate input in hrbac if needed
if [ "$1" == "regen" ]; then 
  cd ../../hrbac/gen_input
  if [ ! -d "../input" ]; then
    mkdir ../input
  fi
  python3 gen_rbacDB.py
  python3 -m da -r -I thread --rule gen_queries.da 
  cd -
fi 

if [ ! -d "../input" ]; then
  mkdir ../input
fi
cp ../../hrbac/input/UR_500 ../input
cp ../../hrbac/input/RH_500 ../input
python3 use_and_randomize_hrbac_input.py