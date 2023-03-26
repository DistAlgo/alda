#!/bin/bash

# run this script in examples/RBAC

# small workload for testing
#pgms="RBACunion"
#datasets="$(seq 50 50 500)"
#startIter=0
#endIter=2

# run everything.
pgms="RBACunion RBACallloc RBACnonloc RBACpy RBACda"
datasets="$(seq 50 50 500)"
startIter=0
endIter=4

if [ ! -d "out" ]; then
    mkdir out
fi

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
        timeout 1800 python3 -m da -r -I thread --rule RBACtimer.da --bench $pgm --workload $data --workmode random 1>>$outfile 2>>$errfile
        # in case of timeout, append timeout message to outfile, to confirm that execution didn't abort for other reasons.
        if [ "$?" == "124" ]; then
            echo "timeout!" >>$outfile
            timedout="true"
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

# I usually run extract_times.py separately later, using run_extract.sh
#iters=$(expr $endIter + 1)
#python3 ../extract_times.py "RBAC" "${pgms}" "${datasets}" ${iters}

echo " =============== FINISHED ==================="
tput bel