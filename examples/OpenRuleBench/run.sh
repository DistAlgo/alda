#!/bin/bash

# run this script in examples/OpenRuleBench

# run everything
daPgms="TCraw DBLPraw Wineraw TC TCrev DBLP Wine_break"
xsbPgms="TCxsb TCwritexsb TCrevxsb TCrevwritexsb DBLPxsb Winexsb"
tcMin=10000
tcMax=100000
# allowed values of cyc: true, false, both.  determines which TC datasets are used.
cyc="both"
startIter=0
endIter=4

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
                fi
            fi
        done
    done
done

for pgm in ${xsbPgms}; do
    # remove "xsb" suffix from pgm name to get name of .P file
    pgmfile=${pgm::-3}
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
                    echo "timeout!" >>result.txt
                fi
                mv -f result.txt $outfile
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
            fi
        done
    done
done

# I usually run extract_times.py separately later, using run_extract.sh, because it automates calling extract_times.py three times, once for each benchmark (TC, DBLP, Wine).  this is necessary because extract_times.py assumes that all programs were run on the same datasets.
#iters=$(expr $endIter + 1)
#python3 ../extract_times.py "ORB" "${daPgms} ${xsbPgms}" "${datasets}" ${iters}

echo " =============== FINISHED ==================="
tput bel