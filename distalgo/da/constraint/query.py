from minizinc import Instance, Model, Solver
# MZ_MODEL_HOME = os.path.join(os.path.dirname(__file__),'minizinc_model')
from .csp_io import csp_path, write_file
import os
from pprint import pprint

# gecode, chuffed, cbc, google.or.tools
SOVLER_DEFAULT = 'cbc'

def get_value(val):
	if isinstance(val, (int, float, bool, str, set)):
		return str(val)
	elif isinstance(val,range):
		return str(list(val))
	else:
		print('ERROR: da.constraint.query, function get_value, unsupported type', val)

def flat_list(inputlist, dimension=1, current_len=[]):
	if isinstance(inputlist,list) and len(inputlist) > 0 and isinstance(inputlist[0],list):
		output = []
		current_len.append(len(inputlist[0]))
		for l in inputlist:
			output += l
		return flat_list(output, dimension+1, current_len)
	elif isinstance(inputlist,list):
		tmplist = ['_' if (l is None) else get_value(l) for l in inputlist]
		tmplen = ','.join(['1..%s'%l for l in current_len])
		return 'array%sd(%s,[%s])' % (dimension,tmplen,','.join(tmplist))
	else:
		# print("TODO: should't get here")
		return get_value(inputlist)

def _query(constraint, **args):
	model = Model(os.path.join(csp_path, constraint))
	datafile = constraint+'.dzn'
	# file = open(datafile,'w')
	txt = ""

	for key, val in args.items():
		if val:
			if isinstance(val, list):
				flatten_val = flat_list(val,current_len=[len(val)])
			else:
				flatten_val = get_value(val)
			txt += '%s = %s;\n' % (key,flatten_val)
	write_file(datafile,txt)

	model.add_file(os.path.join(csp_path, datafile))
	solver = Solver.lookup(SOVLER_DEFAULT)
	instance = Instance(solver, model)
	result = instance.solve()

	####### MiniZinc version 2.4.2
	if not result.status.has_solution():
		return None
	return {key:val for key,val in vars(result.solution).items()}#result.solution