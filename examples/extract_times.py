# extract times from output files in {bench}/{pgm}/out, and save them to a csv file.
# to run this program, run run_extract.sh in examples/, or run this program directly in examples/{bench}.

import sys
import os
import statistics

# transform pgm name to a more readable column heading
def colname(pgm):
    if pgm == 'TCwritexsb': return 'TCXSBw'
    elif pgm == 'TCrevwritexsb': return 'TCrevXSBw'
    else: return pgm.replace('xsb','XSB')

def main():
    bench = sys.argv[1] # PA, RBAC, or ORB
    pgms = [pgm for pgm in sys.argv[2].split(' ') if len(pgm)>0]
    datasets = sys.argv[3].split(' ')
    iters = int(sys.argv[4])
    xsbpgms = [pgm for pgm in pgms if 'xsb' in pgm]
    rawpgms = [pgm for pgm in pgms if 'raw' in pgm]
    dapgms = [pgm for pgm in pgms if 'xsb' not in pgm and 'raw' not in pgm]
    # extracted timings, results, etc.
    res = {}
    # we need to run extract_times 3 times for ORB, so include some info about pgms in filename.
    if bench=='ORB' and any(pgm in pgms for pgm in {'DBLP', 'DBLPraw', 'DBLPxsb'}):
        pgmname = 'DBLP'
    elif bench=='ORB' and any(pgm in pgms for pgm in {'Wine_break', 'Wineraw', 'Winexsb'}):
        pgmname = 'Wine'
    elif bench=='ORB' and any(pgm in pgms for pgm in {'TC', 'TCraw', 'TCrev', 'TCxsb','TCrevxsb'}):
        if datasets[0].endswith('_cyc.P'): pgmname='TCcyc'
        elif datasets[0].endswith('_nocyc.P'): pgmname='TCnocyc'
        else: pgmname='TC'
    else:
        pgmname=''
    if pgmname=='':
        out = open(f'timing_{bench}.csv',"w")
    else:
        out = open(f'timing_{bench}_{pgmname}.csv',"w")

    # map from initial prefix of data line to our (column) name for da pgms
    prefixes_map = {}
    # note: R_data was formerly init_tm_pf+pr.  removed ('run_tm_pf+pr', 'run_tm')
    prefixes_map['PA'] = [('init_os_total', 'R_data'), ('write_data', 'W_data'), ('xsb_load',  'xsb_R'), ('preproc_xsb', 'pre'), ('xsb_query', 'xsb_QW'), ('subprocess_xsb', 'xsb'), ('read_results', 'R_res'), ('postproc_xsb', 'post'), ('run_os_total', 'run')]
    prefixes_map['RBAC'] = prefixes_map['PA'][1:]
    # da programs that do not call XSB.  might be cleaner to remove these from dapgms.
    daNoXSBpgms = {'RBACpy', 'RBACda'}
    prefixes_map['daNoXSB'] = prefixes_map['RBAC'][-1:]
    # use 'run' instead of 'query' in column headings for consistency.  removed ('query_tm_pf+pr', 'run_tm').
    prefixes_map['ORB'] = [('init_os_total', 'R_data'), ('write_data', 'W_data'), ('xsb_load',  'xsb_R'), ('preproc_xsb', 'pre'), ('xsb_query', 'xsb_QW'), ('subprocess_xsb', 'xsb'), ('read_results', 'R_res'), ('postproc_xsb', 'post'), ('query_os_total', 'run')]
    # map from initial prefix of data line to our (column) name for ORB "raw" pgms.  removed ('init_tm_pf+pr', 'R_raw_tm'),  ('dump_tm_pf+pr', 'dump_tm').
    prefixes_map['raw'] =  [('init_os_total', 'R_raw'), ('dump_os_total', 'dump')]
    # map from initial prefix of data line to our (column) name for xsb pgms
    prefixes_map['xsb'] = [('loading cputime:', 'load'), ('computing cputime:', 'query')]

    for pgm in pgms:
        # prefixes expected in output files for this program
        prefixes = prefixes_map['xsb'] if pgm in xsbpgms else prefixes_map['raw'] if pgm in rawpgms else prefixes_map['daNoXSB'] if pgm in daNoXSBpgms else prefixes_map[bench]
        #print('prefixes ',prefixes)
        # character separating values in input files
        sepchar = ' ' if pgm in xsbpgms else '\t'
        for data in datasets:
            error=False
            incomplete=False
            for i in range(0,iters):
                fname = os.path.join('out', f'{pgm}_{data}_{i}_out.txt')
                #print('fname=',fname)
                try:
                    f=open(fname,"r")
                    lines = f.read().rstrip('\n').split('\n')
                    f.close()
                    for l in lines:
                        #print(f'{pgm} {data} {i} line ',l)
                        for (prefix,col) in prefixes:
                            if l.startswith(prefix):
                                if (col,pgm,data,i) not in res:
                                    res[col,pgm,data,i] = float(l.split(sepchar)[-1])
                                else: # sum over calls to xsb
                                    res[col,pgm,data,i] += float(l.split(sepchar)[-1])
                        if bench=='PA' and pgm in dapgms and i==0:
                            if 'result 2:' in l:
                                res['result2',pgm,data] = l.split('\t')[-4:-1]
                            if 'result 3:' in l:
                                res['result3',pgm,data] = l.split('\t')[-3:-1]
                            if 'result 4:' in l:
                                res['result4',pgm,data] = l.split('\t')[-4:-1]
                    # an iteration is incomplete if the last timing measurement is missing.  if this iteration is incomplete (probably due to time-out), don't bother to look for subsequent iterations.  the three "last timing measurements" are for dapgms, xsbpgms, and rawpgms, respectively.
                    incomplete = ('run', pgm, data, i) not in res and ('query', pgm, data, i) not in res and ('dump', pgm, data, i) not in res 
                    if incomplete:
                        #print(f'{pgm} {data} {i}: this iteration is incomplete.  not computing statistics for this program-data combination.', file=out, flush=True)
                        break
                except FileNotFoundError:
                    # don't bother to look for remaining iterations.
                    i -= 1
                    break
                except BaseException as err:
                    print(f'{pgm} {data} {i}:Unexpected {err=}, {type(err)=}.  not computing statistics for this program-data combination.', file=out, flush=True)
                    error=True
                    break
            # i==-1 if no output files exist for this pgm-data combination, presumably because the program would timeout on this data.
            if error or incomplete or i == -1:
                # don't compute stats.  proceed to next data.
                continue
            # average results from all iterations.  
            # upper bound of range is based on current value of i, in case fewer than iters iterations are present.
            iters1 = i+1
            for (_,col) in prefixes:
                times = [res[col,pgm,data,i] for i in range(0,iters1)]
                mean = statistics.fmean(times)
                res[col,pgm,data] = mean
                res['sd_'+col,pgm,data] = 0 if iters1==1 else statistics.stdev(times)
            if pgm in dapgms and pgm not in daNoXSBpgms:
                # sums
                res['xsbpp',pgm,data] = res['xsb',pgm,data] + res['pre',pgm,data] + res['post',pgm,data]
                #res['run_tm+xsb_RQW',pgm,data] = res['run_tm',pgm,data] + xsb_RQW
                #res['run_tm+xsb',pgm,data] = res['run_tm',pgm,data] + res['xsb',pgm,data]
                # note: RBAC doesn't read the workload as data, so we consider run as the total.
                if bench=='PA' or bench=='ORB':
                    res['total',pgm,data] = res['R_data',pgm,data] + res['run',pgm,data] 
                # compare xsb_RQW with xsb, as percent difference
                xsb_RQW = res['xsb_R',pgm,data] + res['xsb_QW',pgm,data]
                res['%xsbRQW-xsb',pgm,data] = 100*(xsb_RQW - res['xsb',pgm,data])/res['xsb',pgm,data]
                res['%xsbpp-run',pgm,data] = 100*(res['xsbpp',pgm,data] - res['run',pgm,data])/res['run',pgm,data]
                # compare run_tm+xsb_RQW with run_os, as percent difference
                #res['%_tm+xsbRQW_os',pgm,data] = 100*(res['run_tm+xsb_RQW',pgm,data] - res['run_os',pgm,data])/res['run_os',pgm,data]
                # compare run_tm+xsb with run_os, as percent difference
                #res['%_tm+xsb_os',pgm,data] = 100*(res['run_tm+xsb',pgm,data] - res['run_os',pgm,data])/res['run_os',pgm,data]
            if pgm in xsbpgms:
                res['total',pgm,data] = res['load',pgm,data] + res['query',pgm,data] 

    # compare results from different da versions.
    if bench=='PA':
        for data in datasets:
            for result in ['result2','result3','result4']:
                val = res[result,dapgms[0],data]
                for pgm in dapgms[1:]:
                    if val != res[result,pgm,data]:
                        print('error: ', result, 'differs for', data, file=out)
                        print(dapgms[0], ':', val, file=out)
                        print(pgm, ':', res[result,pgm,data], '\n', file=out)

    # da pgms: measured quantities to print, with std dev for each
    qtys = [col for (prefix,col) in prefixes_map[bench]]
    dacols = []
    for qty in qtys:
        dacols.append(qty)
        dacols.append('sd_'+qty)
    # sums
    dacols.append('xsbpp')
    #dacols.append('run_tm+xsb_RQW')
    #dacols.append('run_tm+xsb')
    if bench == 'PA' or bench == 'ORB':
        dacols.extend(['total'])
    # comparisons
    dacols.append('%xsbRQW-xsb')
    #dacols.append('%_tm+xsbRQW_os')
    #dacols.append('%_tm+xsb_os')
    dacols.append('%xsbpp-run')
    
    # da pgms that don't call xsb: measured quantities to print, with std dev for each
    qtys = [col for (prefix,col) in prefixes_map['daNoXSB']]
    daNoXSBcols = []
    for qty in qtys:
        daNoXSBcols.append(qty)
        daNoXSBcols.append('sd_'+qty)

    # xsb pgms: measured quantities to print, with std dev for each
    qtys = [col for (prefix,col) in prefixes_map['xsb']]
    xsbcols = []
    for qty in qtys:
        xsbcols.append(qty)
        xsbcols.append('sd_'+qty)
    xsbcols.extend(['total'])

    # raw pgms: measured quantities to print, with std dev for each
    qtys = [col for (prefix,col) in prefixes_map['raw']]
    rawcols = []
    for qty in qtys:
        rawcols.append(qty)
        rawcols.append('sd_'+qty)

    # print first row of column headings. this row contains the name of the pgm in the first column of the column range for that pgm.
      
    for pgm in rawpgms:
        print(',', colname(pgm), ','*(len(rawcols)-1), end='', file=out)
    for pgm in dapgms:
        cols = daNoXSBcols if pgm in daNoXSBpgms else dacols
        print(',', colname(pgm), ','*(len(cols)-1), end='', file=out)
    for pgm in xsbpgms:
        print(',', colname(pgm), ','*(len(xsbcols)-1), end='', file=out)
    print('', file=out)
    # print second row of column headings.
    print('dataset,', end='', file=out)
    for pgm in rawpgms:
        print(','.join(rawcols), ',', end='', file=out)
    for pgm in dapgms:
        cols = daNoXSBcols if pgm in daNoXSBpgms else dacols
        print(','.join(cols), ',', end='', file=out)
    for pgm in xsbpgms:
        print(','.join(xsbcols), ',', end='', file=out)
    print('', file=out)
    # print timings, etc.
    for data in datasets:
        print(data, end='', file=out)
        for pgm in rawpgms:
            for col in rawcols:
                # print percentages with 2 decimal places, everything else with 4
                precision = 2 if '%' in col else 4
                print(',', round(res[col,pgm,data],precision) if (col,pgm,data) in res else '', end='', file=out)
        for pgm in dapgms:
            cols = daNoXSBcols if pgm in daNoXSBpgms else dacols
            for col in cols:
                # print percentages with 2 decimal places, everything else with 4
                precision = 2 if '%' in col else 4
                print(',', round(res[col,pgm,data],precision) if (col,pgm,data) in res else '', end='', file=out)
        for pgm in xsbpgms:
            for col in xsbcols:
                # print percentages with 2 decimal places, everything else with 4
                precision = 2 if '%' in col else 4
                print(',', round(res[col,pgm,data],precision) if (col,pgm,data) in res else '', end='', file=out)
        print('', file=out)

    out.close()
        
main()
