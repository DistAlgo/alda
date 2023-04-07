# measure time to read facts from .P and write them to pickle files

import os, time, pickle, collections, re, statistics

def main():

    datasets="blender django matplotlib numpy pandas pytorch scikit-learn scipy sympy".split(' ')
    cputime0 = {}
    cputime1 = {}
    cputime2 = {}
    cputime3 = {}
    classdefsz = {}
    namesz = {}
    membersz = {}
    readtime = {}
    pickletime = {}
    for i in range(0,10):
        for data in datasets:
            cputime0[data] = time.process_time()

            # read facts from .P
            print('reading facts for ',data)
            with open(data+'.P', "r") as f:
              facts = collections.defaultdict(list)
              for l in f:
                l = re.split('[(,]',l.strip()[:-2])
                facts[l[0]].append(tuple(map(lambda x: x.strip("'"),l[1:])))

            cputime1[data] = time.process_time()
            
            # store the sizes, for consistency check
            #print(data)
            classdefsz[data] = len(facts['pClassDef'])
            namesz[data] = len(facts['pName'])
            membersz[data] = len(facts['pMember'])

            cputime2[data] = time.process_time()

            # write facts to pickle files
            print('pickling facts for ',data)
            for p in facts:
                f=open(f'{data}_{p}.pickle', "wb")
                pickle.dump(facts[p], f)
                f.close()

            cputime3[data] = time.process_time()

            if i==0:
                readtime[data] = []
                pickletime[data] = []
            readtime[data].append(cputime1[data]-cputime0[data])
            pickletime[data].append(cputime3[data]-cputime2[data])
    out = open('io_time.csv', 'w')
    # column headings
    print('dataset, .P_read, stdev, pickle_write, stdev, |classdef|, |name|, |member|',file=out)
    for data in datasets:
        print(data, ',', statistics.fmean(readtime[data]), ',', statistics.stdev(readtime[data]), ',', statistics.fmean(pickletime[data]), ',', statistics.stdev(pickletime[data]), ',', classdefsz[data], ',', namesz[data], ',', membersz[data], file=out)
    out.close()
    
main()
