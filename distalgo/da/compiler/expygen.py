from .. import common

def PythonGenerator(filename, args):
	print('expygen')
	if common.get_runtime_option('constraint', default=False):
		print('expygen: PythonGenerator')
		from .constraint.constraint_pygen import PythonGenerator
	elif common.get_runtime_option('rule', default=False):
		from .rule.rule_pygen import PythonGenerator
	else:
		from .pygen import PythonGenerator
	return PythonGenerator(filename, args)