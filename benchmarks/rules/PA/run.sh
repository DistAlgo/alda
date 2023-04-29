#!/bin/bash

# small workload for testing
# list of Alda programs to run
daPgms="PAopt"
# list of XSB programs to run
xsbPgms="PAXSBopt"
datasets="numpy django blender matplotlib pandas pytorch scikit-learn scipy sympy"
startIter=0
endIter=0

# run everything
#daPgms="PA PAopt"
#xsbPgms="PAXSB PAoptXSB PAXSBopt"
#datasets="numpy django blender matplotlib pandas pytorch scikit-learn scipy sympy"
#startIter=0
#endIter=9

if [ ! -d "out" ]; then
    mkdir out
fi

echo "system load at start of run" >>out/top.txt
date >>out/top.txt
top -n 1 -b | head -n 35 >>out/top.txt
echo >>out/top.txt

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
        timedout="false"
        timeout 1800 time python -m da -r -I thread --rules --timing PAtimer.da --data data/$data --bench $pgm 1>>${outfile} 2>>${errfile}
        # in case of timeout, append timeout message to outfile, to confirm that execution didn't abort for other reasons.
        if [ "$?" == "124" ]; then
            echo "timeout!" >>$outfile
            timedout="true"
        fi
        # rename file used as input to XSB.  I think it doesn't matter which pgm is used.
        if [ "${pgm}" = "PA" -a "${i}" = "0" ]; then
            for FILE in $(ls __pycache__/PA.*class_extends_rs*facts); do
                echo "renaming ${FILE}"
                mv "$FILE" __pycache__/$data.P
            done
        fi
        if [ "$timedout" == "true" ]; then
            echo "timeout; skipping remaining iterations"
            break
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
        timedout="false"
        timeout 1800 time xsb -e "[$pgm], xsbtest('__pycache__/$data.P'), halt."  1>>${outfile} 2>>${errfile}
        if [ "$?" == "124" ]; then
            echo "timeout!" >>xsb_result.txt
            timedout="true"
        fi
        mv -f xsb_result.txt $outfile
        if [ "$timedout" == "true" ]; then
            echo "timeout; skipping remaining iterations"
            break
        fi
        if ! grep -q "computing cputime" "$outfile"; then
            echo "incomplete iteration; skipping remaining iterations"
            break
        fi
    done
  done
done

echo "system load at end of run" >>out/top.txt
date >>out/top.txt
top -n 1 -b | head -n 35 >>out/top.txt
echo >>out/top.txt

echo " =============== FINISHED ==================="
tput bel