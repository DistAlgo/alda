#!/bin/bash

# run this script in PA/data

datasets="blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy"

rm -f line_counts.txt

outfile="line_counts.txt"

# total number of ast facts based on astFacts (includes duplicates)
echo "count lines in astFacts/*.py:" >>$outfile
for data in $datasets; do
    pushd $data/astFacts
    echo $data >>$outfile
    wc -l *.py | tail -n 1 >>../../line_counts.txt
    #wc -l *.py >>../../line_counts.txt
    popd
done
echo >>$outfile

# number of ast facts in select relations, based on astFacts and text-rep
for data in $datasets; do
    pushd $data/astFacts
    echo "count matches of (RELATION in astFacts/*.py:" >>$outfile
    echo -n "${data} ClassDef " >>$outfile
    grep -o "('ClassDef'" *.py | wc -l >>$outfile
    echo -n "${data} Member " >>$outfile
    grep -o "('Member'" *.py | wc -l >>$outfile
    echo -n "${data} Name " >>$outfile
    grep -o "('Name'" *.py | wc -l >>$outfile
    echo >>$outfile
    echo "count ( in text-rep/RELATION:" >>$outfile
    cd ../text-rep
    echo -n "${data} ClassDef " >>$outfile
    grep -o "(" ClassDef | wc -l >>$outfile
    echo -n "${data} Member " >>$outfile
    grep -o "(" Member | wc -l >>$outfile
    echo -n "${data} Name " >>$outfile
    grep -o "(" Name | wc -l >>$outfile
    echo -n "${data} is_Sub " >>$outfile
    grep -o "is_Sub" is_Sub | wc -l >>$outfile
    echo >>$outfile
    popd
done

# total number of ast facts, based on text-rep (no duplicates)
for data in $datasets; do
    pushd $data/text-rep
    echo "count ( in $data/text-rep: *, Context, ValuedIdDict" >>$outfile
    grep -o "(" * | wc -l >>$outfile
    echo -n ", " >>$outfile
    grep -o "(" Context | wc -l >>$outfile
    echo -n ", " >>$outfile
    grep -o "(" ValueIdDict | wc -l >>$outfile
    echo >>$outfile
    popd
done