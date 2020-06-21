import sys
from ast import *
from .. import common

__all__ = ['daast_from_file', 'daast_from_str', 'Parser']

def daast_from_file(filename, args):
	"""Generates DistAlgo AST from source file.

	'filename' is the filename of source file. Optional argument 'args' is a
	Namespace object containing the command line parameters for the compiler.
	Returns the generated DistAlgo AST.

	"""
	try:
		with open(filename, 'r') as infd:
			global InputSize
			src = infd.read()
			InputSize = len(src)
			return daast_from_str(src, filename, args)
	except Exception as e:
		print(type(e).__name__, ':', str(e), file=sys.stderr)
		raise e
	return None

def daast_from_str(src, filename='<str>', args=None):
	"""Generates DistAlgo AST from source string.

	'src' is the DistAlgo source string to parse. Optional argument 'filename'
	specifies the filename that appears in error messages, defaults to
	'<str>'. Optional argument 'args' is a Namespace object containing the
	command line parameters for the compiler. Returns the generated DistAlgo
	AST.

	"""
	try:
		if common.get_runtime_option('constraint', default=False):
			# print('exparser: daast_from_str')
			from ..constraint.constraint_parser import Parser
		else:
			from .parser import Parser
		# from .parser import Parser
		dt = Parser(filename, args)
		rawast = parse(src, filename)
		dt.visit(rawast)
		sys.stderr.write("%s compiled with %d errors and %d warnings.\n" %
					 (filename, dt.errcnt, dt.warncnt))
		if dt.errcnt == 0:
			return dt.program
	except SyntaxError as e:
		sys.stderr.write("%s:%d:%d: SyntaxError: %s" % (e.filename, e.lineno,
													e.offset, e.text))
	return None

def Parser(filename, args):
	if common.get_runtime_option('constraint', default=False):
		from ..constraint.constraint_parser import Parser
	else:
		from .parser import Parser
	return Parser(filename, args)
