#!/bin/bash
# extract running times from output files for OpenRuleBench, RBAC, and PA, and save them to csv files.
# run this script in this directory 

# search for errors in output files, ignoring lines containing phrases like "compiled with no errors".
grep -i --exclude=*answers* error OpenRuleBench/out/*.txt PA/out/*.txt  RBAC/out/*.txt | grep -v compiled

echo "extracting ORB"
cd OpenRuleBench
python ../extract_times.py "ORB" "TCraw TC TCrev TCxsb TCWxsb TCrevxsb TCrevWxsb" "tc_d1000_par10000_xsb_nocyc.P tc_d1000_par20000_xsb_nocyc.P tc_d1000_par30000_xsb_nocyc.P tc_d1000_par40000_xsb_nocyc.P tc_d1000_par50000_xsb_nocyc.P tc_d1000_par60000_xsb_nocyc.P tc_d1000_par70000_xsb_nocyc.P tc_d1000_par80000_xsb_nocyc.P tc_d1000_par90000_xsb_nocyc.P tc_d1000_par100000_xsb_nocyc.P" 10
python ../extract_times.py "ORB" "TCraw TC TCrev TCxsb TCWxsb TCrevxsb TCrevWxsb" "tc_d1000_par10000_xsb_cyc.P tc_d1000_par20000_xsb_cyc.P tc_d1000_par30000_xsb_cyc.P tc_d1000_par40000_xsb_cyc.P tc_d1000_par50000_xsb_cyc.P tc_d1000_par60000_xsb_cyc.P tc_d1000_par70000_xsb_cyc.P tc_d1000_par80000_xsb_cyc.P tc_d1000_par90000_xsb_cyc.P tc_d1000_par100000_xsb_cyc.P" 10
python ../extract_times.py "ORB" "Wineraw Wine_break Winexsb WineWxsb" "wine" 10
python ../extract_times.py "ORB" "DBLPraw DBLP DBLPxsb DBLPWxsb" "dblp" 10
cd ..

echo "extracting PA"
cd PA
python ../extract_times.py "PA" "PA PAopt paxsb paoptxsb paxsb_manualopt" "numpy django scikit-learn blender pandas matplotlib scipy pytorch sympy" 10
cd ..

echo "extracting RBAC"
cd RBAC
python ../extract_times.py "RBAC" "RBACunion RBACallloc RBACnonloc RBACpy RBACda" "50 100 150 200 250 300 350 400 450 500" 10
cd ..
