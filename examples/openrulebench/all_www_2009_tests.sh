#!/bin/bash

# Table 1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query b2
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query b2
# Table 2
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_b2
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_b2
# Table 3
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_a
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_b1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_b2
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_b2
# Table 4 
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query a
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query a
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query b1
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query b1
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query b2
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query b2
# Table 5
python3.7 -m da --rule run_tests.da --testsuite join2 --data join2
# Table 6
python3.7 -m da --rule run_tests.da --testsuite lubm --data test_10_univs
python3.7 -m da --rule run_tests.da --testsuite lubm --data test_50_univs
# Table 7
python3.7 -m da --rule run_tests.da --testsuite mondial --data mondial 
# Table 8
python3.7 -m da --rule run_tests.da --testsuite dblp --data dblp
# Table 9
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc
# Table 10
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc --query bf
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc --query bf
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc --query bf
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc --query bf
# Table 11
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc --query fb
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc --query fb
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc --query fb
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc --query fb
# Table 12
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc
# Table 13
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc --query bf
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc --query bf
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc --query bf
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc --query bf
# Table 14
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc --query fb
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc --query fb
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc --query fb
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc --query fb
# Table 15
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query hypernym
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query hyponym
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query meronym
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query holonym
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query troponym
# Table 16
python3.7 -m da --rule run_tests.da --testsuite wine --data wine
# Table 17 (win-not-win not included yet)
python3.7 -m da --rule run_tests.da --testsuite nonsg --data nonsg_d500_parsize5000_sibsize1000
python3.7 -m da --rule run_tests.da --testsuite nonsg --data nonsg_d500_parsize20000_sibsize4000
# Table 18 (non-stratified not included yet)