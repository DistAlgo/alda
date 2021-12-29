for mode in RBACpy RBACda RBACunion RBACallloc RBACnonloc
do
  for i in $(seq 50 50 500)
  do
    timeout 1800 time python3.9 -m da --message-buffer-size=40960000 --rule test_paper.da --workloadcount $i --workloadmode random --mode $mode 1>>out.txt 2>>msg.txt
    printf "end $mode-$i\n" >>out.txt 
    printf "end $mode-$i\n" >>msg.txt
  done
done
