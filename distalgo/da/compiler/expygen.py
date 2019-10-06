def PythonGenerator(filename, args):
	if hasattr(args,'constraint'):
		# print('expygen: PythonGenerator')
		from .constraint.constraint_pygen import PythonGenerator
	elif hasattr(args,'rule'):
		from .rule.rule_pygen import PythonGenerator
	else:
		from .pygen import PythonGenerator
	return PythonGenerator(filename, args)