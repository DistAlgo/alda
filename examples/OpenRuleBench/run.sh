#!/bin/bash

# run this script in examples/OpenRuleBench

# run everything
daPgms="DBLP"
xsbPgms="DBLPxsb"
tcMin=10000
tcMax=100000
# allowed values of cyc: true, false, both.  determines which TC datasets are used.
cyc="both"
startIter=0
endIter=4

if [ "$1" == "correctness" ]; then 
    endIter=0
    xsbwritesuffix="W"
    if [ ! -d "answers" ]; then
        mkdir answers
    else
        rm -rf answers/*
    fi
fi

tcdatasets=""
for i in $(seq $tcMin 10000 $tcMax); do
    if [ "$cyc" == "true" -o "$cyc" == "both" ]; then
        tcdatasets="${tcdatasets} tc_d1000_par${i}_xsb_cyc.P"
    else
        tcdatasets="${tcdatasets} tc_d1000_par${i}_xsb_nocyc.P"
    fi
done
# remove leading space
tcdatasets="${tcdatasets:1}"
if [ "$cyc" == "both" ]; then
    for i in $(seq $tcMin 10000 $tcMax); do
        tcdatasets="${tcdatasets} tc_d1000_par${i}_xsb_nocyc.P"
    done
fi

if [ ! -d "out" ]; then
    mkdir out
fi

for pgm in ${daPgms}; do
    if [ "${pgm::2}" = "TC" ]; then
        datasets="$tcdatasets"
    elif [ "$pgm" = "DBLPraw" -o "$pgm" = "DBLP" ]; then
        datasets="dblp"
    elif [ "$pgm" = "Wineraw" -o "$pgm" = "Wine_break" ]; then
        datasets="wine"
    else
        echo "unknown program $pgm"
        break
    fi
    for data in ${datasets}; do
        for ((i=${startIter};i<=${endIter};i++)); do
            outfile=out/${pgm}_${data}_${i}_out.txt
            errfile=out/${pgm}_${data}_${i}_err.txt
            rm -f $outfile $errfile
            echo "running ${pgm} ${data} ${i}"
            if [ "$pgm" = "TCraw" -o "$pgm" = "DBLPraw" -o "$pgm" = "Wineraw" ]; then
                if [ ! -d "data_pickle" ]; then
                    mkdir data_pickle
                fi
                # no processes, so don't bother giving -I thread
                timeout 1800 time python3 -m da -r --rule ORBtimer.da --data $data --mode raw 1>>${outfile} 2>>${errfile}
                # in case of timeout, append timeout message to outfile, to confirm that execution didn't abort for other reasons.
                if [ "$?" == "124" ]; then
                    echo "timeout!" >>$outfile
                fi
                if ! grep -q "dump_os_total" "$outfile"; then
                    echo "incomplete iteration; skipping remaining iterations"
                    break
                fi
            else
                # if removing -I thread, add:  --message-buffer-size=409600000
                timeout 1800 time python3 -m da -r -I thread --rule ORBtimer.da --bench $pgm --data $data 1>>${outfile} 2>>${errfile}
                if [ "$?" == "124" ]; then
                    echo "timeout!" >>$outfile
                fi
                if ! grep -q "total_os_total" "$outfile"; then
                    echo "incomplete iteration; skipping remaining iterations"
                    break
                elif [ "$1" == "correctness" ]; then 
                    latestanswers=`ls -t __pycache__/*.answers | head -n 1`
                    mv $latestanswers answers/${pgm/_break/""}_${data}_da.answers
                fi
            fi
        done
    done
done

for pgm in ${xsbPgms}; do
    # remove "xsb" suffix from pgm name to get name of .P file
    # and add a suffix "W" if checking for correctness
    pgmfile=${pgm::-3}${xsbwritesuffix}
    # datasets is needed by extract_timings
    if [ "${pgm::2}" = "TC" ]; then
        datasets="$tcdatasets"
    elif [ "$pgm" = "DBLPxsb" ]; then
        datasets="dblp"
    elif [ "$pgm" = "Winexsb" ]; then
        datasets="wine"
    else
        echo "unknown xsb program $pgm"
        break
    fi
    for data in ${datasets}; do
        for ((i=${startIter};i<=${endIter};i++)); do
            outfile=out/${pgm}_${data}_${i}_out.txt
            errfile=out/${pgm}_${data}_${i}_err.txt
            rm -f $outfile $errfile xsb_result.txt
            # redirect stdout to a file to avoid clutter on the console, but it contains nothing interesting, so overwrite it with the result file.
            if [ "${pgm::2}" = "TC" ]; then
                echo "running ${pgm} ${data} ${i}"
                timeout 1800 time xsb -e "['$pgmfile'], test('data_raw/$data'), halt."  1>>${outfile} 2>>${errfile}
                if [ "$?" == "124" ]; then
                    echo "timeout!" >>tc_result.txt
                fi
                mv -f tc_result.txt $outfile
            elif [ "$pgm" = "DBLPxsb" ]; then
                echo "running ${pgm} ${i}"
                timeout 1800 time xsb -e "['$pgmfile'], test, halt."  1>>${outfile} 2>>${errfile}
                if [ "$?" == "124" ]; then
                    echo "timeout!" >>dblp_result.txt
                fi
                mv -f dblp_result.txt $outfile
            elif [ "$pgm" = "Winexsb" ]; then
                echo "running ${pgm} ${i}"
                timeout 1800 time xsb -e "['$pgmfile'], test, halt."  1>>${outfile} 2>>${errfile}
                if [ "$?" == "124" ]; then
                    echo "timeout!" >>wine_result.txt
                fi
                mv -f wine_result.txt $outfile
            else
                echo "unknown program $pgm"
                break
            fi
            if ! grep -q "computing cputime" "$outfile"; then
                echo "incomplete iteration; skipping remaining iterations"
                break
            elif [ "$1" == "correctness" ]; then 
                latestanswers=`ls -t *answers.txt | head -n 1`
                mv $latestanswers answers/${pgm::-3}_${data}_xsb.answers
            fi
        done
    done
done

cd answers
if [ "$1" == "correctness" ]; then
    > correctness.txt
    # for each da answer, if there is a corresponding xsb answer file, then compare
    # if the corresponding xsb answer file is not there, note this as well
    for df in *_da.answers; do
        bench=${df::-11}
        xf=${bench}_xsb.answers
        if [ -f $xf ]; then
            d=`diff <(sed "s/^.//;s/.$//;s/'//g" ${xf} | sort) <(sed "s/'//g" ${df} | sort) | wc -l | tr -d ' '`
            if [ "$d" == "0" ]; then 
                echo "${bench}: match" >> correctness.txt
            else
                echo "${bench}: mismatch" >> correctness.txt
            fi
        else
            echo "${bench}: no xsb answer file" >> correctness.txt
        fi
    done
    # at this point, check if there are xsb files without corresponding da files
    for xf in *_xsb.answers; do
        bench=${xf::-12}
        df=${bench}_da.answers
        if [ ! -f $df ]; then
            echo "${bench}: no da answer file" >> correctness.txt
        fi
    done
fi
cd .. 

# I usually run extract_times.py separately later, using run_extract.sh, because it automates calling extract_times.py three times, once for each benchmark (TC, DBLP, Wine).  this is necessary because extract_times.py assumes that all programs were run on the same datasets.
#iters=$(expr $endIter + 1)
#python3 ../extract_times.py "ORB" "${daPgms} ${xsbPgms}" "${datasets}" ${iters}

echo " =============== FINISHED ==================="
tput bel