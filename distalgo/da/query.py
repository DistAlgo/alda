import os
from minizinc import Instance, Model, Solver
MZ_MODEL_HOME = os.path.join(os.path.dirname(__file__),'compiler','constraint','minizinc_model')

from pprint import pprint

SOVLER_DEFAULT = 'gecode'

def flat_list(inputlist, dimension=1, current_len=[]):
	if isinstance(inputlist,list) and len(inputlist) > 0 and isinstance(inputlist[0],list):
		output = []
		current_len.append(len(inputlist[0]))
		for l in inputlist:
			output += l
		return flat_list(output, dimension+1, current_len)
	elif isinstance(inputlist,list):
		tmplist = ['_' if (l is None or l == 0) else str(l) for l in inputlist]
		tmplen = ','.join(['1..%s'%l for l in current_len])
		return 'array%sd(%s,[%s])' % (dimension,tmplen,','.join(tmplist))
	else:
		print("TODO: should't get here")
		

def query(self, constraint, **args):

	model = Model(os.path.join(MZ_MODEL_HOME, constraint+'.mzn'))
	
	datafile = os.path.join(MZ_MODEL_HOME, constraint+'.dzn')
	file = open(datafile,'w')
	for key, val in args.items():
		if isinstance(val, list):
			flatten_val = flat_list(val,current_len=[len(val)])
		else:
			flatten_val = str(val)
		file.write('%s = %s;\n' % (key,flatten_val))

	file.close()

	model.add_file(datafile)
	solver = Solver.lookup(SOVLER_DEFAULT)
	instance = Instance(solver, model)
	result = instance.solve()
	return result._solutions
	