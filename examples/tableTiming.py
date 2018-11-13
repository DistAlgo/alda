mode = 'query'
# case = ['python','distalgo','RHrule','rule','rule_all','rolerule','rolerule_all']
case = ['RHrule','rule','rolerule']
numr = [100,150,200,250,300,350,400,450,500]
numq = 50
queries = [50,100,150,200,250,300,350,400,450,500]
# r = 800
numavg = -10

import numpy


def roleresult(q):
	global numr
	global numq
	outfile = 'roleresult_'+str(q)+'.csv'
	fout = open(outfile,'a')
	fout.write('\n')
	for c in case:
		fout.write(','+c)
	for r in numr:
		fout.write('\n'+str(r))
		for c in case:
			filename = './timing/timing_hrbac_'+c+'_'+'r'+str(r)+'_q'+str(numq)+'_auth'+str(q)+'.txt'
			print(filename)
			tmp = open(filename).read().split('\n')
			tmp = list(filter(('').__ne__, tmp))[numavg:]
			cpuTime = []
			for t in tmp:
				cpuTime.append(t.split(',')[-1])
			print(cpuTime)
			cpuTime = list(map(float,cpuTime))
			print(cpuTime)
			fout.write(','+str(numpy.mean(cpuTime)))
	fout.close()


def queryresult(numr):
	global queries
	global numq
	outfile = 'queryresult_'+str(numr)+'.csv'
	fout = open(outfile,'a')
	fout.write('\n')
	for c in case:
		fout.write(','+c)
	for q in queries:
		fout.write('\n'+str(q))
		for c in case:
			filename = './timing/timing_hrbac_'+c+'_'+'r'+str(numr)+'_q'+str(numq)+'_auth'+str(q)+'.txt'
			print(filename)
			tmp = open(filename).read().split('\n')
			tmp = list(filter(('').__ne__, tmp))[numavg:]
			cpuTime = []
			for t in tmp:
				cpuTime.append(t.split(',')[-1])
			print(cpuTime)
			cpuTime = list(map(float,cpuTime))
			print(cpuTime)
			fout.write(','+str(numpy.mean(cpuTime)))
	fout.close()


if __name__ == "__main__":
	if mode == 'role':
		roleresult(50)
	if mode == 'query':
		queryresult(500)

