for i in $(seq 10000 10000 100000)
do
  python3.9 -m da --rules run_tests.da --testsuite tc --data tc_d1000_parsize${i}_xsb_cyc.P 1>>tc_out.txt 2>>tc_msg.txt
  printf "end $i" >>tc_out.txt 
  printf "end $i" >>tc_msg.txt
done

for i in $(seq 10000 10000 100000)
do
  python3.9 -m da --rules run_tests.da --testsuite tc_rev --data tc_d1000_parsize${i}_xsb_cyc.P 1>>tc_rev_out.txt 2>>tc_rev_msg.txt
  printf "end $i" >>tc_rev_out.txt 
  printf "end $i" >>tc_rev_msg.txt
done