from ast import *
from da.compiler import dast
from . import constraint_ast as cast
import os, sys
from pprint import pprint
from da.compiler.utils import CompilerMessagePrinter

MZ_MODEL_HOME = os.path.join(os.path.dirname(__file__),'minizinc_model')
if not os.path.exists(MZ_MODEL_HOME):
	os.mkdir(MZ_MODEL_HOME)

MZ_TYPE_DICT = {
	'int': 'int',
	'float': 'float',
	'str': 'string',
	'bool': 'bool'
}

MZ_QUAN_DICT = {
	dast.UniversalOp: 'forall',
	dast.ExistentialOp: 'exists'
}

MZ_COMP_OP = {
	dast.InOp: 'in',
	dast.NotInOp: 'not in',
	dast.EqOp: '=',
	dast.NotEqOp: '!=',
	dast.LtOp: '<',
	dast.LtEOp: '<=',
	dast.GtOp: '>',
	dast.GtEOp: '>=',
	dast.IsOp: '=',
	dast.IsNotOp: '!='
}

MZ_COMP_NEG_OP = {
	dast.InOp: dast.NotInOp,
	dast.NotInOp: dast.InOp,
	dast.EqOp: dast.NotEqOp,
	dast.NotEqOp: dast.EqOp,
	dast.LtOp: dast.GtEOp,
	dast.LtEOp: dast.GtOp,
	dast.GtOp: dast.LtEOp,
	dast.GtEOp: dast.LtOp,
	dast.IsOp: dast.IsNotOp,
	dast.IsNotOp: dast.IsOp
}

MZ_BIN_OP = {
	dast.MultOp: '*',
	dast.AddOp: '+',
	dast.SubOp: '-',
	dast.DivOp: '/',
	dast.ModOp: 'mod'
}

MZ_UNARY_OP = {
	dast.USubOp: '-',
	dast.UAddOp: '+',
	dast.InvertOp: 'not'
}

MZ_CPRH_OP = {
	dast.MaxExpr: 'max',
	dast.MinExpr: 'min',
	dast.SumExpr: 'sum',
	dast.SizeExpr: 'length',
	dast.MinCompExpr: 'min',
	dast.MaxCompExpr: 'max',
	dast.SumCompExpr: 'sum',
	dast.LenCompExpr: 'length',
}

MZ_TARGET_OP = {
	'min': 'minimize',
	'max': 'maximize'
}

MZ_LOGIC_OP = {
	'and': '/\\',
	'or': '\\/',
	'not': 'not',
	dast.OrOp: '\\/',
	dast.AndOp: '/\\',
	dast.NotOp: 'not'
}

MZ_ALLDIFF = 'all_different'

MZ_GLOBALFUNCS = {'alldiff'}

MZ_LIBRARY = {
	MZ_ALLDIFF: "globals.mzn"
}

class Translator(NodeVisitor, CompilerMessagePrinter):
	def __init__(self, filename="", _parent=None):
		CompilerMessagePrinter.__init__(self, filename, _parent=_parent)
		NodeVisitor.__init__(self)
		self.returnVariables = []
		self.augVariables = []
		self.augConstraints = []
		self.activeLibrary = set()
		# self.file = open(os.path.join(MZ_MODEL_HOME,filename+'.mzn'),'w')


	def visit(self, node):
		if isinstance(node, cast.CSP):
			txt = ""
			target = self.visit(node.objective)
			var = []
			con = []
			for n, v in node.variables.items():
				var.append(self.visit(v))
			for n, c in node.constraints.items():
				con.append(self.visit(c))
			for l in self.activeLibrary:
				txt += 'include "%s";\n' % l
				# self.file.write('include "%s";\n' % l)
			for v in var:
				txt += v
				# self.file.write(v)
			for c in con:
				txt += c
				# self.file.write(c)
			txt += target
			return txt
			# self.file.write(target)
		elif isinstance(node, str):
			return node
		else:
			return super().visit(node)

	def visit_Constraint(self, node):
		# {'constraints': [<da.compiler.dast.QuantifiedExpr object at 0x107470bd0>,
		# 		 <da.compiler.dast.QuantifiedExpr object at 0x107470d50>],
		#  'name': 'latin',
		#  'op': 'and'}
		txt = 'constraint\n    '
		constraints = [self.visit(c) for c in node.constraints]
		op = ' )\n '+MZ_LOGIC_OP[node.op]+' ( '
		txt += '( %s )' % op.join(constraints)+';\n'
		return txt


	def visit_DomainSpec(self, node):
		#  'index': 221,
		#  'subexprs': [<da.compiler.dast.PatternExpr object at 0x103027090>,
		#			   <da.compiler.dast.CallExpr object at 0x103027590>]}
		############################################################################
		# <generator> ::= <ident> "," ... "in" <expr>
		ident = self.visit(node.pattern)
		expr = self.visit(node.domain)
		return '%s in %s' % (ident, expr)

	def visit_NamedVar(self, node):
		return node.name

	def visit_TuplePattern(self,node):
		raise TypeError(
			'Unsupported syntax type: %s, line %s' % (node.__class__.__name__, node.lineno))
		# value = [self.visit(e) for e in node.value]
		# return ', '.join(value)
		# maybe not the best way of doing this. 

	def visit_FreePattern(self, node):
		return self.visit(node.value)

	def visit_PatternExpr(self, node):
		# TO CHECK: looks like the subexpr always contain only one element
		return self.visit(node.pattern)

	def visit_QuantifiedExpr(self, node):
		#  'domains': [<da.compiler.dast.DomainSpec object at 0x10b78a2d0>],
		#  'index': 220,
		#  'operator': <class 'da.compiler.dast.UniversalOp'>,
		#  'subexprs': [<da.compiler.dast.CallExpr object at 0x10b78a210>]}
		############################################################################
		# % Generator call expressions
		# <gen-call-expr> ::= <ident-or-quoted-op> "(" <comp-tail> ")" "(" <expr> ")"

		# % Identifiers and quoted operators
		# <ident-or-quoted-op> ::= ...
		#						| ’<builtin-op>’

		# <comp-tail> ::= <generator> [ "where" <expr> ] "," ...
		# <generator> ::= <ident> "," ... "in" <expr>

		txt = ''
		op = MZ_QUAN_DICT[node.operator]
		domains = [self.visit(d) for d in node.domains]		# TODO: I suspect this might also have case that have where
		exprs = [self.visit(e) for e in node.subexprs]
		txt += '%s ( %s )( %s )' % (op, ', '.join(domains), ', '.join(exprs))

		return txt


	def visit_LogicalExpr(self, node):
		op = MZ_LOGIC_OP[node.operator]
		if len(node.subexprs) == 1:
			if isinstance(node.left, dast.ComparisonExpr):
				node.left.comparator = MZ_COMP_NEG_OP[node.left.comparator]
				return self.visit(node.left)
			else:
				operant = self.visit(node.left)
				return '(%s %s)' % (op, operant)
		else:
			operant = [self.visit(e) for e in node.subexprs]
			return '(%s)' % (' '+op+' ').join(operant)

	def visit_GeneratorExpr(self, node):
		elem = self.visit(node.elem)
		conditions = [self.visit(c) for c in node.conditions]
		return {'elem': elem, 'cond': conditions}

	def visit_BinaryExpr(self, node):
		op = MZ_BIN_OP[node.operator]
		left = self.visit(node.left)
		right = self.visit(node.right)
		return '(%s %s %s)' % (left, op ,right)


	# comprehension
	# <array-comp> ::= "[" <expr> "|" <comp-tail> "]"
	# <set-comp> ::= "{" <expr> "|" <comp-tail> "}"
	# <comp-tail> ::= <generator> [ "where" <expr> ] "," ...

	# quantification
	# <gen-call-expr> ::= <ident-or-quoted-op> "(" <comp-tail> ")" "(" <expr> ")"
	# The identifier must be the name of a unary predicate or function that takes an array argument
	def visit_ComprehensionExpr(self, node):
		elem = self.visit(node.elem)
		domainspec = []
		conditions = []
		for c in node.conditions:
			if isinstance(c, dast.DomainSpec):
				domainspec.append(self.visit(c))
			else:
				conditions.append(self.visit(c))

		if conditions:
			op = ' /\\ '
			txt = ' where ( %s )' % op.join(conditions)
		else:
			txt = ''

		if node.__class__ in MZ_CPRH_OP:	# aggregation
			agg_op = MZ_CPRH_OP[node.__class__]
			if agg_op == "length" and conditions:
				return 'sum ( %s )( %s )' % (', '.join(domainspec), ' /\\ '.join(conditions))
			return '%s ( %s )( %s )' % (agg_op, ', '.join(domainspec)+txt, elem)

		txt = '%s | %s' % (elem, ', '.join(domainspec)) + txt
		
		if isinstance(node, dast.SetCompExpr):
			return '{ %s }' % txt
		else:
			return '[ %s ]' % txt

	visit_SetCompExpr = visit_ComprehensionExpr
	visit_ListCompExpr = visit_ComprehensionExpr
	visit_MinCompExpr = visit_ComprehensionExpr
	visit_MaxCompExpr = visit_ComprehensionExpr
	visit_SumCompExpr = visit_ComprehensionExpr
	visit_LenCompExpr = visit_ComprehensionExpr

	def visit_IfExpr(self, node):
		# cond, body, else
		# <if-then-else-expr> ::= 
		# "if" <expr> "then" <expr> [ "elseif" <expr> "then" <expr> ]* "else" <expr> "endif"
		txt = 'if '
		cond = self.visit(node.condition)
		txt += cond
		body = self.visit(node.body)
		txt += ' then '+body
		if len(node.subexprs) > 2:
			if isinstance(node.orbody, dast.IfExpr):	# elif
				pass
				print('TODO: translate_minizinc, visit_IfExpr, elif')
			else:
				elbody = self.visit(node.orbody)
				txt += ' else '+elbody
		txt += ' endif'
		return txt


	def visit_ComparisonExpr(self, node):
		op = MZ_COMP_OP[node.comparator]
		left = self.visit(node.left)
		right = self.visit(node.right)
		return '%s %s %s' % (left, op ,right)

	def visit_NameExpr(self, node):
		return node.name

	def visit_ConstantExpr(self, node):
		return str(node.value)

	def visit_UnaryExpr(self,node):
		op = MZ_UNARY_OP[node.operator]
		right = self.visit(node.right)
		return op+right

	def trans_alldiff(self, args):
		self.activeLibrary.add(MZ_LIBRARY[MZ_ALLDIFF])
		if len(args) == 1:	
			if isinstance(args[0], dict):	# generator expr
				return '%s( %s )( %s )' % (MZ_ALLDIFF, ', '.join(args[0]['cond']), args[0]['elem'])
			if isinstance(args[0], str):	# alldiff(q)
				return '%s( %s )' % (MZ_ALLDIFF, args[0])
		elif len(args) > 1:	# query expr
			return '%s( %s )( %s )' % (MZ_ALLDIFF, ', '.join(args[1:]), args[0])
		else:
			# should be error
			print('TODO, trans_alldiff: seems not possible, raise error')

	def visit_IntsExpr(self,node):
		return '%s..%s' % (self.visit(node.start), self.visit(node.end))

	def visit_CallExpr(self, node):
		# _fields = ['func', 'args', 'keywords', 'starargs', 'kwargs']
		func = self.visit(node.func)
		args = [self.visit(a) for a in node.args]
		txt = ''
		if func in MZ_GLOBALFUNCS:
			txt = getattr(self,'trans_'+func)(args)
		elif func == 'ints':
			txt = '..'.join(args)
		else:
			txt = '%s( %s )' % (func, ', '.join(args))
		return txt

	def visit_TupleExpr(self,node):
		return [self.visit(e) for e in node.subexprs]

	def visit_SliceExpr(self, node):
		return '%s..%s' % (self.visit(node.lower), self.visit(node.upper))

	def visit_SubscriptExpr(self, node):
		#  'subexprs': [<da.compiler.dast.NameExpr object at 0x10d1fdc90>,
		#			   <da.compiler.dast.TupleExpr object at 0x10d1fd590>]}
		var = self.visit(node.value)
		idx = self.visit(node.index)
		if var == 'int' or var == 'float':
			return idx

		if isinstance(idx, list):
			return '%s[%s]' % (var, ', '.join(idx))
		else:
			return '%s[%s]' % (var, idx)

	

	def visit_Num(self, node):
		return str(node.n)

	def visit_Name(self, node):
		return node.id

	def visit_TrueExpr(self, node):
		return 'true'

	def visit_FalseExpr(self, node):
		return 'false'

	def visit_AggregateExpr(self, node):
		# ['func', 'args', 'keywords', 'starargs', 'kwargs']
		args = [self.visit(a) for a in node.args]
		op = MZ_CPRH_OP[node.__class__]
		return '%s ( %s )' % (op, ', '.join(args))


	visit_MaxExpr = visit_AggregateExpr
	visit_MinExpr = visit_AggregateExpr
	visit_SumExpr = visit_AggregateExpr
	visit_SizeExpr = visit_AggregateExpr

	def visit_Variable(self, node):
		name = node.name
		if not node.value:
			domain = self.visit(node.domain)
			return '%s: %s;\n' % (domain, name)
		else:
			if isinstance(node.value, (dast.SetCompExpr, dast.ListCompExpr)):#dast.ComprehensionExpr
				node.domain.opt = True
			domain = self.visit(node.domain)
			value = self.visit(node.value)
			return '%s: %s = %s;\n' % (domain, name, value)


# DomainTuple:
#	 elements: a list of domains

# DomainSet:
#	 sub_domain: domain
# DomainMultiSet:
#	 sub\_domain: domain

# <ti-expr> ::= <base-ti-expr>
# <base-ti-expr> ::= <var-par> <base-ti-expr-tail>
# <var-par> ::= "var" | "par" | ε
# <base-ti-expr-tail> ::= <ident>
#					   | <base-type>
#					   | <set-ti-expr-tail>
#					   | <ti-variable-expr-tail>
#					   | <array-ti-expr-tail>
#					   | "ann"
#					   | "opt" <base-ti-expr-tail>
#					   | { <expr> "," ... }
#					   | <num-expr> ".." <num-expr>
# % Type-inst variables
# <ti-variable-expr-tail> ::= $[A-Za-z][A-Za-z0-9_]*
	def visit_DomainVar(self, node):
		txt = ''
		if node.parameter is False:
			txt += 'var '
		txt += self.visit(node.var)
		return txt

	def visit_DomainBasic(self, node):
		# DomainBasic: int, float, str, bool
		#	 type:   string
		#	 lb: simple expr
		#	 ub: simple expr
		#	 step: simple expr 				# minizinc does not support step
		######################################
		# <base-ti-expr> ::= <var-par> <base-ti-expr-tail>
		# <base-ti-expr-tail> ::= ...
		#						| <base-type> 
		# 						| <num-expr> ".." <num-expr>
		# <base-type> ::= "bool"
		#			   | "int"
		#			   | "float"
		#			   | "string"
		
		txt = ''
		typ = MZ_TYPE_DICT[node.type]
		if node.parameter is False:
			txt += 'var '
			if node.opt:
				txt += 'opt '
		if typ == 'int' and node.lb is not None and node.ub is not None:
			lb = self.visit(node.lb)
			ub = self.visit(node.ub)
			txt += '%s..%s' % (lb, ub)
		else:
			txt += typ
		return txt

	def visit_DomainMap(self, node):
		# DomainMap:
		#	 key: domain
		#	 val: domain
		######################################
		# % Array type-inst expressions
		# <array-ti-expr-tail> ::= "array" [ <ti-expr> "," ... ] "of" <ti-expr>
		#						| "list" "of" <ti-expr>
		
		txt = ''
		key = self.visit(node.key)
		val = self.visit(node.val)
		txt += 'array [%s] of ' % key
		if node.parameter is False:
			txt += 'var '
		if node.opt:
			txt += 'opt '
		txt += val
		return txt

	def visit_DomainTuple(self, node):
		elements = [self.visit(e) for e in node.elements]
		txt = ', '.join(elements)
		return txt

	def visit_DomainSet(self, node):
		# % Set type-inst expressions
		# <set-ti-expr-tail> ::= "set" "of" <base-type>
		txt = ''
		if node.parameter is False:
			txt = 'var '
		# if node.opt:
		# 	txt += 'opt '
		txt += 'set'
		if not node.domain:
			return txt
		else:
			domain = self.visit(node.domain)
			txt += ' of '+domain
			return txt


	def visit_DomainMultiSet(self, node):
		pass

	def visit_Target(self, node):
		for v in node.variables:
			if isinstance(v, str):
				self.returnVariables.append(v)
			else:
				# create a tmp variable and then visit
				print('TODO: visit_Target: need to create a tmp variable and then visit')
				

		for c in node.constraints:
			if not isinstance(c, str):
				# create a constraint for this and then visit
				print('TODO: visit_Target: need to create a constraint for this and then visit')

		if not node.objective:
			return 'solve satisfy;'
		else:
			op = MZ_TARGET_OP[node.objective.op]
			obj = self.visit(node.objective.obj)
			return 'solve %s %s;' % (op, obj)
