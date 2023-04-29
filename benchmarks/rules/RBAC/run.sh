#!/bin/bash

# small workload for testing
pgms="RBACunion"
datasets="$(seq 50 50 500)"
startIter=0
endIter=0

# run everything for the experiments in the arXiv paper about Alda
#pgms="RBACunion RBACallloc RBACnonloc RBACpy RBACda"
#datasets="$(seq 50 50 500)"
#startIter=0
#endIter=9

if [ ! -d "out" ]; then
    mkdir out
fi

echo "system load at start of run" >>out/top.txt
date >>out/top.txt
top -n 1 -b | head -n 35 >>out/top.txt
echo >>out/top.txt

for pgm in $pgms; do
  for data in $datasets; do
    for ((i=${startIter};i<=${endIter};i++)); do
        outfile=out/${pgm}_${data}_${i}_out.txt
        errfile=out/${pgm}_${data}_${i}_err.txt
        if [ -a "$outfile" ]; then
            rm -f $outfile
        fi
        if [ -a "$errfile" ]; then
            rm -f $errfile
        fi
        echo "running $pgm $data $i"
        timedout="false"
        # if removing -I thread, add:  --message-buffer-size=409600000
        timeout 1800 python -m da -r -I thread --rules --timing RBACtimer.da --bench $pgm --workload $data --workmode random 1>>$outfile 2>>$errfile
        # in case of timeout, append timeout message to outfile, to confirm that execution didn't abort for other reasons.
        if [ "$?" == "124" ]; then
            echo "timeout!" >>$outfile
            timedout="true"
            echo "timeout; skipping remaining iterations"
            break
        fi
        if ! grep -q "run_os" "$outfile"; then
            echo "incomplete iteration; skipping remaining iterations"
            break
        fi
    done
    # RBAC datasets are sorted smallest to largest.  in case of timeout, skip remaining datasets for this program.
    if [ "$timedout" == "true" ]; then
        echo "timeout: skipping remaining datasets for this program"
        break
    fi
  done
done

echo "system load at end of run" >>out/top.txt
date >>out/top.txt
top -n 1 -b | head -n 35 >>out/top.txt
echo >>out/top.txt

echo " =============== FINISHED ==================="
tput bel