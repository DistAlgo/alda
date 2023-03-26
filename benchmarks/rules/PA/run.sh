#!/bin/bash

# run this script in examples/PA

# small workload for testing
#daPgms="PA"
#xsbPgms="paxsb_manualopt"
#datasets="numpy django blender matplotlib pandas pytorch scikit-learn scipy sympy"
#startIter=0
#endIter=0

# run everything
daPgms="PA PAopt"
xsbPgms="paxsb paoptxsb paxsb_manualopt"
datasets="numpy django blender matplotlib pandas pytorch scikit-learn scipy sympy"
startIter=0
endIter=4

if [ ! -d "out" ]; then
    mkdir out
fi

for pgm in ${daPgms}; do
  for data in ${datasets}; do
    for ((i=${startIter};i<=${endIter};i++)); do
        outfile=out/${pgm}_${data}_${i}_out.txt
        errfile=out/${pgm}_${data}_${i}_err.txt
        rm -f $outfile $errfile
        # remove facts files from previous runs.  
        for FILE in $(ls __pycache__/PA.*class_extends_rs*facts 2>/dev/null); do
            rm -f "$FILE"
        done
        echo "running ${pgm} ${data} ${i}"
        # -r option to force da to re-compile, for measurement of compilation time
        # if removing -I thread, add:  --message-buffer-size=409600000
        timeout 1800 time python3 -m da -r -I thread --rule PAtimer.da --data data/$data --bench $pgm 1>>${outfile} 2>>${errfile}
        # in case of timeout, append timeout message to outfile, to confirm that execution didn't abort for other reasons.
        if [ "$?" == "124" ]; then
            echo "timeout!" >>$outfile
        fi
        # rename file used as input to XSB.  I think it doesn't matter which pgm is used.
        if [ "${pgm}" = "PA" -a "${i}" = "0" ]; then
            for FILE in $(ls __pycache__/PA.*class_extends_rs*facts); do
                echo "renaming ${FILE}"
                mv "$FILE" __pycache__/$data.P
            done
        fi
        if ! grep -q "run_os_total" "$outfile"; then
            echo "incomplete iteration; skipping remaining iterations"
            break
        fi
    done
  done
done

for pgm in ${xsbPgms}; do
  for data in ${datasets}; do
    for ((i=${startIter};i<=${endIter};i++)); do
        outfile=out/${pgm}_${data}_${i}_out.txt
        errfile=out/${pgm}_${data}_${i}_err.txt
        rm -f $outfile $errfile xsb_result.txt
        echo "running ${pgm} ${data} ${i}"
        # redirect stdout to avoid clutter on the console, but it contains nothing interesting, so overwrite it with the result file.
        timeout 1800 time xsb -e "[$pgm], xsbtest('__pycache__/$data.P'), halt."  1>>${outfile} 2>>${errfile}
        if [ "$?" == "124" ]; then
            echo "timeout!" >>xsb_result.txt
        fi
        mv -f xsb_result.txt $outfile
        if ! grep -q "computing cputime" "$outfile"; then
            echo "incomplete iteration; skipping remaining iterations"
            break
        fi
    done
  done
done

# I usually run extract_times.py separately later, using run_extract.sh
#iters=$(expr $endIter + 1)
#python3 ../extract_times.py "PA" "${daPgms} ${xsbPgms}" "${datasets}" ${iters}

echo " =============== FINISHED ==================="
tput bel