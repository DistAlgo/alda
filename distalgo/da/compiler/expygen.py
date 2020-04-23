from .. import common

__all__ = ['PythonGenerator']

def PythonGenerator(filename, args):
	if common.get_runtime_option('constraint', default=False):
		from ..constraint.constraint_pygen import PythonGenerator
	elif common.get_runtime_option('rule', default=False):
		from ..rule.rule_pygen import PythonGenerator
	else:
		from .pygen import PythonGenerator
	return PythonGenerator(filename, args)