mode = 'transrule'
# case = ['python','distalgo','RHrule','rule','rule_all','rolerule','rolerule_all']
case = ['rule']
nume = [100,200,300,400,500,600,700,800,900,1000]
numr = [100,150,200,250,300,350,400,450,500]
numq = 50
queries = [50,100,150,200,250,300,350,400,450,500]
# r = 800
numavg = -5

import numpy

#			0			1			2			3		4			5			6				7
# print('queryElapse, queryCPU, readElapse, readCPU, convertElapse, convertCPU, totalElapse, totalCPU')

def transresult():
	global nume
	outfile = 'transresult.csv'
	fout = open(outfile,'a')
	fout.write('\n')
	for c in case:
		fout.write(','+c+'_query,'+c+'_read,'+c+'_convertsplit,'+c+'_converttuple,'+c+'_convertset,'+c+'_total')
	for e in nume:
		fout.write('\n'+str(e))
		for c in case:
			filename = './timing/trans_'+c+'_'+str(e)+'.csv'
			print(filename)
			tmp = open(filename).read().split('\n')
			tmp = list(filter(('').__ne__, tmp))[numavg:]
			qT = []
			rT = []
			cT1 = []
			cT2 = []
			cT3 = []
			tT = []
			# cpuTime = []
			for t in tmp:
				ts = t.split(',')
				qT.append(ts[0])
				rT.append(ts[3])
				cT1.append(ts[5])
				cT2.append(ts[7])
				cT3.append(ts[9])
				tT.append(ts[11])
			# print(cpuTime)
			qT = list(map(float,qT))
			rT = list(map(float,rT))
			cT1 = list(map(float,cT1))
			cT2 = list(map(float,cT2))
			cT3 = list(map(float,cT3))
			tT = list(map(float,tT))
			# print(cpuTime)
			fout.write(','+str(numpy.mean(qT))+','+str(numpy.mean(rT))+','+str(numpy.mean(cT1))+','+str(numpy.mean(cT2))+','+str(numpy.mean(cT3))+','+str(numpy.mean(tT)))
	fout.close()

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
		queryresult(100)
	if mode == 'transrule':
		transresult()

