#!/bin/bash
rm ~/alda_results.txt

# Table 1
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query a > ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query b2 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query b2 >> ~/alda_results.txt
# Table 2
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query bf_b2 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query bf_b2 >> ~/alda_results.txt
# Table 3
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize50000_xsb_cyc --query fb_b2 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1 --data d1000_relsize250000_xsb_cyc  --query fb_b2 >> ~/alda_results.txt
# Table 4 
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query a >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query b1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize50000_xsb_cyc --query b2 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite join1_duplicate --data d1000_relsize250000_xsb_cyc  --query b2 >> ~/alda_results.txt
# Table 5
python3.7 -m da --rule run_tests.da --testsuite join2 --data join2 >> ~/alda_results.txt
# Table 6
python3.7 -m da --rule run_tests.da --testsuite lubm --data test_10_univs --query 1 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite lubm --data test_50_univs --query 1 >> ~/alda_results.txt
# Table 7
python3.7 -m da --rule run_tests.da --testsuite mondial --data mondial  >> ~/alda_results.txt
# Table 8
python3.7 -m da --rule run_tests.da --testsuite dblp --data dblp >> ~/alda_results.txt
# Table 9
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc >> ~/alda_results.txt
# Table 10
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc --query bf >> ~/alda_results.txt
# Table 11
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_nocyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize50000_xsb_cyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_nocyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite tc --data tc_d1000_parsize500000_xsb_cyc --query fb >> ~/alda_results.txt
# Table 12
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc >> ~/alda_results.txt
# Table 13
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc --query bf >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc --query bf >> ~/alda_results.txt
# Table 14
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_nocyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize5000_sibsize1000_xsb_cyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_nocyc --query fb >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite sg --data sg_d500_parsize20000_sibsize4000_xsb_cyc --query fb >> ~/alda_results.txt
# Table 15
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query hypernym >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query hyponym >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query meronym >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query holonym >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite wordnet --data wordnet --query troponym >> ~/alda_results.txt
# Table 16
python3.7 -m da --rule run_tests.da --testsuite wine --data wine >> ~/alda_results.txt
# Table 17 (win-not-win not included yet)
python3.7 -m da --rule run_tests.da --testsuite nonsg --data nonsg_d500_parsize5000_sibsize1000 >> ~/alda_results.txt
python3.7 -m da --rule run_tests.da --testsuite nonsg --data nonsg_d500_parsize20000_sibsize4000 >> ~/alda_results.txt
# Table 18 (non-stratified not included yet)˜