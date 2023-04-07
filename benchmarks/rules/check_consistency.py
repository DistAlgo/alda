# check that different versions of a benchmark produce the same results.
# run this program in this folder.  
# usage: python check_consistency.py BENCHMARK, where BENCHMARK is OpenRuleBench, PA, or RBAC.

import glob
import os
import re
import sys

# f is a file object for the answer file.
def read_answer(bench, pgm, f):
    if bench == 'OpenRuleBench':
        lines = f.read().splitlines()
        # normalize answers from da and xsb programs to be in same format by:
        # (1) removing single quotes around strings in da answers
        # (2) remove square brackets around xsb answers
        # return the normalized answers in a set, to remove duplicates
        if 'xsb' in pgm or 'XSB' in pgm:
            return { a.removeprefix('[').removesuffix(']') for a in lines }
        else:
            return { a.replace("'","") for a in lines }
    elif bench == 'PA':
        if 'xsb' in pgm or 'XSB' in pgm:
            s = f.read()
            # results are on lines enclosed in square brackets
            matches = re.findall('^\[.*?\]$', s, re.MULTILINE)
            #matches = re.findall('f\(.*?\)', s)
            # matches[0] should have the form: [#defined, #extending, list of roots]
            result2 = matches[0].split(',')
            ndefined = int(result2[0][1:])
            nextending = int(result2[1])
            nroots = len(result2) - 2
            # matches[1] should have the form: [max_height, list of roots with max height]
            result3 = matches[1].split(',')
            max_height = int(result3[0][1:])
            nroots_max_height = len(result3)-1
            # matches[2] should have the form: [max_desc, list of roots with max desc]
            result4 = matches[2].split(',')
            # XSB pgms do not return desc, so put a dummy value.
            desc = 0
            max_desc = int(result4[0][1:])
            nroots_max_desc = len(result4)-1
        else:
            lines = f.read().splitlines()
            #print('lines=',lines)
            # get line containing 'result 2', and split it at tabs
            result2 = [l for l in lines if 'result 2' in l][0].split('\t')
            ndefined = int(result2[-3])
            nextending = int(result2[-2])
            nroots = int(result2[-1])
            # get line containing 'result 3', and split it at tabs
            result3 = [l for l in lines if 'result 3' in l][0].split('\t')
            max_height = int(result3[-2])
            nroots_max_height = int(result3[-1])
            # get line containing 'result 4', and split it at tabs
            result4 = [l for l in lines if 'result 4' in l][0].split('\t')
            desc = int(result4[-3])
            max_desc = int(result4[-2])
            nroots_max_desc = int(result4[-1])
        return (ndefined, nextending, nroots, max_height, nroots_max_height, desc, max_desc, nroots_max_desc)
    elif bench == 'RBAC':
        # results are sets enclosed in curly braces.  each result is printed on a line by itself.  don't bother parsing the result lines into sets.
        lines = f.read().splitlines()
        if any(l.startswith('timeout') for l in lines):
            return 'timeout'
        else:
            results = [l for l in lines if l.startswith('{')]
            return results
    else:
        print('unknown benchmark: ', bench)
        sys.exit()

def main():
    bench = sys.argv[1]
    if bench not in ['OpenRuleBench', 'PA', 'RBAC']:
        print('unknown benchmark')
        sys.exit()
    # worklist[bench] is a list of lists of programs.  for each sublist, answer files for programs in that sublist are compared.
    worklist = {}
    worklist['OpenRuleBench'] = [ ['TC', 'TCrev', 'TCWxsb', 'TCrevWxsb'], ['DBLP', 'DBLPWxsb'], ['Wine_break','WineWxsb'] ]
    worklist['PA'] = [['PA', 'PAopt', 'PAXSB', 'PAoptXSB', 'PAXSBopt']]
    worklist['RBAC'] = [['RBACunion','RBACallloc','RBACnonloc','RBACpy','RBACda']]
    # comparison results are saved in these lists, as tuples (pgm,pgm1,dataset)
    consistent = []
    inconsistent = []
    # missing and timeout are sets, to eliminate duplicates
    missing = set()
    timeout = set()
    # answers for PA, saved for later printing
    answers = set()
    out = open(f'consistency_{bench}.csv',"w")
    os.chdir(os.path.join(bench,'out'))
    for pgms in worklist[bench]:
        pgm = pgms[0]
        # get answer files for pgm. only compare iteration 0.
        answer_file_pat = f'{pgm}_*_answers.txt' if bench == 'OpenRuleBench' else f'{pgm}_*_0_out.txt'
        answer_files = glob.glob(answer_file_pat)
        # for each of those files, compare it with answer files for pgms[1:]
        for fname in answer_files:
            dataset = fname.removeprefix(f'{pgm}_').removesuffix('_answers.txt') if bench == 'OpenRuleBench' else fname.removeprefix(f'{pgm}_').removesuffix('_0_out.txt')
            try:
                f=open(fname,'r')
            except FileNotFoundError:
                print(f'trying to open {fname}: file not found', file=out, flush=True)
                continue
            except BaseException as err:
                print(f'trying to open {fname}: Unexpected {err=}, {type(err)=}', file=out, flush=True)
                continue
            answer = read_answer(bench, pgm, f)
            f.close()
            if bench == 'PA':
                answers.add((dataset,answer))
            for pgm1 in pgms[1:]:
                fname1 = pgm1 + fname.removeprefix(pgm)
                print(f'comparing {fname} and {fname1}')
                try:
                    f1=open(fname1,'r')
                except FileNotFoundError:
                    missing.add((pgm1,dataset))
                    continue
                except BaseException as err:
                    print(f'trying to open {fname1}: unexpected {err=}, {type(err)=}', file=out, flush=True)
                    continue
                answer1 = read_answer(bench, pgm1, f1)
                f1.close()
                if answer1 == 'timeout':
                    timeout.add((pgm1,dataset))
                else:
                    # for PA, do not compare answer[5] (=desc), because we put a dummy value there for XSB pgms
                    if (bench == 'PA' and answer[:5] == answer1[:5] and answer[6:] == answer1[6:]) or (bench != 'PA' and answer == answer1):
                        consistent.append((pgm,pgm1,dataset))
                    else:
                        inconsistent.append((pgm,pgm1,dataset))
    os.chdir(os.path.join('..','..'))
    print('Each entry under Consistent and Inconsistent has 3 columns: program1 program2 dataset.\n', file=out)
    if len(inconsistent) > 0:
        print('Inconsistent answers:', file=out)
        for (pgm,pgm1,dataset) in inconsistent:
            print(f'{pgm},{pgm1},{dataset}', file=out)
    if len(consistent) > 0:
        print('\nConsistent answers', file=out)
        for (pgm,pgm1,dataset) in consistent:
            print(f'{pgm},{pgm1},{dataset}', file=out)
    if len(timeout) > 0:
        print('\nAnswer files containing timeout', file=out)
        for (pgm1,dataset) in timeout:
            print(f'{pgm1},{dataset}', file=out)
    if len(missing) > 0:
        if len(timeout) > 0:
            print('\nMissing answer files (possibly due to timeout for smaller dataset)', file=out)
        else:
            print('\nMissing answer files', file=out)
        for (pgm1,dataset) in missing:
            print(f'{pgm1},{dataset}', file=out)
    out.close()
    if bench == 'PA':
        # print answer for each benchmark
        out = open(f'answers_PA.csv',"w")
        print('dataset,defined,extending,len(roots),max_height,len(roots_max_height),desc,max_desc,len(roots_max_desc)', file=out)
        for (dataset,ans) in answers:
            print(f'{dataset},{ans[0]},{ans[1]},{ans[2]},{ans[3]},{ans[4]},{ans[5]},{ans[6]},{ans[7]}',file=out)
        out.close()

main()
