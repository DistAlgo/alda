#!/bin/bash

# list of Alda programs to run. set this to " " if you don't want to run any Alda programs.
daPgms="TCraw DBLPraw Wineraw TC TCrev DBLP Wine_break"
# run TCpy and TCda separately, because they are slower, and we run them on smaller datasets.
#daPgms="TCraw TCpy TCda"
# list of XSB programs to run. set this to " " if you don't want to run any XSB programs.
xsbPgms="TCxsb TCWxsb TCrevxsb TCrevWxsb DBLPxsb DBLPWxsb Winexsb WineWxsb"
# sizes of graphs to use for TC benchmark.  tcMin and tcMax define the range for the number of edges.
# the following values are suitable for all versions of TC except TCpy and TCda.
tcNodes=1000
tcMin=10000
tcMax=10000  # for the experiments in the arXiv paper about Alda: tcMax=100000
tcStep=10000
# the following smaller values are suitable for TCpy and TCda
#tcNodes=100
#tcMin=100
#tcMax=100   # for the experiments in the arXiv paper about Alda: tcMax=400
#tcStep=100
# cyc determines whether to use cyc or nocyc TC datasets.  allowed values: true, false, both
cyc="false"  # for the experiments in the arXiv paper about Alda: cyc=both
# starting value for the iteration number.
startIter=0
# ending value for the iteration number.
endIter=0 # for the experiments in the arXiv paper about Alda: endIter=9

datasets_cyc=""
datasets_nocyc=""
for i in $(seq $tcMin $tcStep $tcMax); do
    datasets_cyc="${datasets_cyc} tc_d${tcNodes}_par${i}_xsb_cyc.P"
    datasets_nocyc="${datasets_nocyc} tc_d${tcNodes}_par${i}_xsb_nocyc.P"
done
if [ "$cyc" = "true" ]; then
    tcdatasets="${datasets_cyc:1}"
elif [ "$cyc" = "false" ]; then
    tcdatasets="${datasets_nocyc:1}"
else
    tcdatasets="${datasets_cyc:1}${datasets_nocyc}"
fi

if [ ! -d "out" ]; then
    mkdir out
fi

echo "system load at start of run" >>out/top.txt
date >>out/top.txt
top -n 1 -b | head -n 35 >>out/top.txt
echo >>out/top.txt

function set_datasets () {
    if [ "${pgm::2}" = "TC" ]; then
        datasets="$tcdatasets"
        bench="tc"
    elif [ "${pgm::4}" = "DBLP" ]; then
        datasets="dblp"
        bench="dblp"
    elif [ "${pgm::4}" = "Wine" ]; then
        datasets="wine"
        bench="wine"
    else
        datasets=""
    fi
}

for pgm in ${daPgms}; do
    set_datasets
    if [ -z "${datasets}" ]; then
        echo "unknown program $pgm"
        continue
    fi
    for data in ${datasets}; do
        ansfile=out/${pgm}_${data}_answers.txt
        rm -f $ansfile
        for ((i=${startIter};i<=${endIter};i++)); do
            outfile=out/${pgm}_${data}_${i}_out.txt
            errfile=out/${pgm}_${data}_${i}_err.txt
            rm -f $outfile $errfile
            echo "running ${pgm} ${data} ${i}"
            timedout="false"
            if [ "${pgm: -3}" = "raw" ]; then
                if [ ! -d "data_pickle" ]; then
                    mkdir data_pickle
                fi
                last_timing="dump_os_total"
                # no processes, so don't bother giving -I thread
                timeout 1800 time python -m da -r --rules ORBtimer.da --data $data --mode raw 1>>${outfile} 2>>${errfile}
            else
                last_timing="total_os_total"
                timeout 1800 time python -m da -r -I thread --rules ORBtimer.da --bench $pgm --data $data 1>>${outfile} 2>>${errfile}
            fi
            # in case of timeout, append timeout message to outfile, to confirm execution didn't abort for other reasons.
            if [ "$?" == "124" ]; then
                echo "timeout!" >>$outfile
                timedout="true"
            fi
            if [ "${i}" = "${startIter}" -a "${pgm: -3}" != "raw" -a "${pgm}" != "TCpy" -a "${pgm}" != "TCda"  ]; then
                latestanswers=`ls -t __pycache__/*.answers | head -n 1`
                mv -f $latestanswers $ansfile
            fi
            if [ "$timedout" == "true" ]; then
                echo "timeout; skipping remaining iterations"
                break
            fi
            if ! grep -q "$last_timing" "$outfile"; then
                echo "incomplete iteration; skipping remaining iterations"
                break
            fi
        done
    done
done

for pgm in ${xsbPgms}; do
    set_datasets
    if [ -z "${datasets}" ]; then
        echo "unknown program $pgm"
        continue
    fi
    # remove "xsb" suffix from our "program name" to get name of .P file
    pgmfile=${pgm::-3}
    for data in ${datasets}; do
        ansfile=out/${pgm}_${data}_answers.txt
        rm -f $ansfile
        for ((i=${startIter};i<=${endIter};i++)); do
            outfile=out/${pgm}_${data}_${i}_out.txt
            errfile=out/${pgm}_${data}_${i}_err.txt
            rm -f $outfile $errfile
            # the xsb programs append to result and answer files.  we don't want
            # to accumulate old results, so delete existing files, if any.
            rm -f ${bench}_result.txt ${bench}_answers.txt
            echo "running ${pgm} ${data} ${i}"
            timedout="false"
            if [ "${bench}" = "tc" ]; then
                args="('data_raw/$data')"
            else
                args=""
            fi
            # stdout is uninteresting.  redirect to /dev/null to avoid clutter on console.
            timeout 1800 time xsb -e "['$pgmfile'], test${args}, halt."  1>>/dev/null 2>>${errfile}
            if [ "$?" == "124" ]; then
                echo "timeout!" >>${bench}_result.txt
                timedout="true"
            fi
            mv -f ${bench}_result.txt $outfile
            # if name of .P file ends with "W", the program writes its answers to an answer file.
            if [ "${i}" = "${startIter}" -a "${pgmfile: -1}" = "W" ]; then
                mv -f ${bench}_answers.txt $ansfile
            fi
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