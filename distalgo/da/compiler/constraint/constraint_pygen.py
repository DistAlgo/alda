from ..pygen import *
from .. import pygen
from pprint import pprint
from . import constraint_ast as cast
import os,io
from da.tools.unparse import Unparser


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
	'each': 'forall'
}

MZ_COMP_OP = {
	In: 'in',
	dast.EqOp: '=',
	dast.NotEqOp: '!=',
	dast.LtOp: '<',
    dast.LtEOp: '<=',
    dast.GtOp: '>',
    dast.GtEOp: '>=',
}

MZ_BIN_OP = {
	dast.MultOp: '*',
	dast.AddOp: '+',
	dast.SubOp: '-',
	dast.DivOp: '/',
	dast.ModOp: 'mod'
}

MZ_GLOBALFUNCS = {
	'alldiff': 'all_different'
}

MZ_CPRH_OP = {
	dast.MinCompExpr: 'min',
	dast.MaxCompExpr: 'max',
	dast.SumCompExpr: 'sum',
	dast.LenCompExpr: 'length'
}



def to_source(tree):
	textbuf = io.StringIO(newline='')
	Unparser(tree, textbuf)
	return textbuf.getvalue()

class PythonGenerator(pygen.PythonGenerator):
	def __init__(self, filename="", options=None):
		super().__init__(filename, options)
		print('constraint_PythonGenerator')
		self.constraint_options = dict()
		self.constraint_info = set()

	def visit_Program(self, node):

		if hasattr(node, 'constraints'):
			# print('?????')
			imptquery = ImportFrom('da.query',[alias('query', None)],0)
			self.preambles.append(imptquery)
			self.transConstraint(node.constraints)
		if hasattr(node, 'constraint_info'):
			# print('???????????????????????')
			self.constraint_info |= node.constraint_info
		return super().visit_Program(node)

	# def visit_Process(self, node):
	# 	if hasattr(node, 'constraints'):
	# 		self.preambles.append(imptquery)
	# 		self.transConstraint(node.constraints)
	# 	if hasattr(node, 'constraint_info'):
	# 		print('???????????????????????')
	# 		self.constraint_info |= node.constraint_info
	# 	return super().visit_Process(node)

	def transConstraint(self, constraints):
		self.toMiniZinc(constraints)

	def toMiniZinc(self, constraints):
		def trans_Domain(domain, var=False):
			""" MiniZinc Type-inst AST subset
			<ti-expr> ::= <base-ti-expr>
			<base-ti-expr> ::= <var-par> <base-ti-expr-tail>
			<var-par> ::= "var" | "par"
			<base-type> ::= "bool"
						  | "int"
						  | "float"
						  | "string"
			base-ti-expr-tail> ::= <ident>
								 | <base-type>
								 | <set-ti-expr-tail>
								 | <array-ti-expr-tail>
								 | <num-expr> ".." <num-expr>
			<set-ti-expr-tail> ::= "set" "of" <base-type>
			<array-ti-expr-tail> ::= "array" [ <ti-expr> "," ... ] "of" <ti-expr>
			"""
			text = ''
			if isinstance(domain, cast.DomainBasic):
				if var:
					text += 'var '
				if not domain.range:
					text += MZ_TYPE_DICT[domain.type]
				elif domain.type == 'int':
					text += '..'.join(domain.range)
				else:
					...
					# ERROR, range 1..n must have type int
				return text
			if isinstance(domain, cast.DomainSet):
				text = ''
				if var:
					text += 'var '
				return text + 'set of '+MZ_TYPE_DICT[domain.domain.type]
			if isinstance(domain, cast.DomainArray):
				text = 'array['
				if isinstance(domain.dimension, list):
					tmptext = [trans_Domain(d) for d in domain.dimension]
					text += ','.join(tmptext)
				else:
					text += trans_Domain(domain.dimension)
				text += '] of '
				if var:
					text += 'var '
				text += trans_Domain(domain.domain)
				return text

		def trans_DomainSpec(node):
			return '%s %s %s' % (node.name, MZ_COMP_OP[type(node.op)], trans_Domain(node.domain))

		def trans_Constraint(constraint):
			if isinstance(constraint, cast.ConstraintSet):
				# print(vars(constraint))
				body = [trans_Constraint(b) for b in constraint.body]
				if isinstance(constraint.relation, And):
					return '( '+' /\\ '.join(body)+' )'
				if isinstance(constraint.relation, Or):
					return '( '+' \\/ '.join(body)+' )'
				else:
					print('TODO: other constraint relation other than And/Or')
					pprint(constraint.relation)
					

			elif isinstance(constraint, cast.QuantifiedConstraint):
				text = ''
				text += MZ_QUAN_DICT[constraint.quantifier] + '( '
				tmptext = [trans_DomainSpec(d) for d in constraint.domain]
				text += ','.join(tmptext)
				text += ' )( '

				p = [trans_Constraint(p) for p in constraint.predicate]
				text += ','.join(p)
				text += ' )'

				return text

			elif isinstance(constraint, cast.FunctionalConstraint):
				text = ''
				if constraint.func_name in MZ_GLOBALFUNCS:
					text += MZ_GLOBALFUNCS[constraint.func_name]
				else:
					text += constraint.func_name
				text += '( '
				tmptext = [trans_DomainSpec(d) for d in constraint.domain_spec]
				text += ','.join(tmptext)
				text += ' )( '

				if isinstance(constraint.target, dast.SubscriptExpr):
					text += trans_SubscriptExpr(constraint.target)
				else:
					print('TODO: constraint_pygen: trans_Constraint -> not isinstance(constraint.target,SubscriptExpr)')

				text += ' )'
				return text

			elif isinstance(constraint, dast.ComparisonExpr):
				# print('dast.ComparisonExpr')
				# pprint(vars(constraint))
				left = constraint.subexprs[0]
				op = MZ_COMP_OP[constraint.comparator]
				target = constraint.subexprs[1]
				return '%s %s %s' % (trans_SubExpr(left), op, trans_SubExpr(target))
			elif isinstance(constraint, dast.ComprehensionExpr):
				return trans_SubExpr(constraint)
			else:
				print('TODO: constraint_pygen: trans_Constraint -> other kinds of constraints')
				print(constraint)
				pprint(vars(constraint))
				return to_source(self.visit(constraint))

		def trans_SubscriptExpr(node):
			if isinstance(node, dast.SubscriptExpr):
				text = ''
				target = node.subexprs[0].name
				text += target + '['
				if isinstance(node.subexprs[1], dast.TupleExpr):
					s = [i.id for i in self.visit_TupleExpr(node.subexprs[1]).elts]
					text +=','.join(s)
				elif isinstance(node.subexprs[1], dast.NameExpr):
					name = self.visit(node.subexprs[1])
					text += to_source(name)[:-1]
				else:
					print('TODO: constraint_pygen: trans_Constraint -> subscirpt non Tuple, non Name')
					print(node.subexprs[1])
					pprint(vars(node.subexprs[1]))
				text += ']'
				return text

		def trans_Iter(node):
			# pprint(vars(node))
			target = node.target.id
			iterator = ''
			if isinstance(node.iter, Call):
				if node.iter.func.id in {'ints', 'floats'}:
					args = [to_source(a)[:-1] for a in node.iter.args]
					iterator = args[0]+'..'+args[1]
				else:
					iterator = to_source(node.iter)[:-1]
			else:
				print('TODO: trans_Iter')
				# pprint(vars(node.iter))
			return '%s in %s' % (target, iterator)


		def trans_SubExpr(node):
			# print(node)
			# pprint(vars(node))
			if isinstance(node, dast.ComprehensionExpr):
				# pprint(vars(node))
				target = trans_SubExpr(node.elem)
				iterator = [trans_Iter(self.visit(s)) for s in node.subexprs]
				return '%s([ %s | %s ])' % (MZ_CPRH_OP[type(node)], target, ','.join(iterator))
			elif isinstance(node, dast.BinaryExpr):
				left = trans_SubExpr(node.subexprs[0])
				right = trans_SubExpr(node.subexprs[1])
				op = MZ_BIN_OP[node.operator]
				return left+op+right
			elif isinstance(node, dast.SubscriptExpr):
				return trans_SubscriptExpr(node)
			else:
				return to_source(self.visit(node))[:-1]

		def trans_Objective(obj):
			if obj.operation == 'satisfy':
				return 'solve satisfy;'
			else:
				return 'solve %s %s;' % (obj.operation, obj.target)

		############ separator between code and functions ############
		for c in constraints:
			filename = c['name']
			# print(filename)
			file = open(os.path.join(MZ_MODEL_HOME,filename+'.mzn'),'w')
			file.write('include "globals.mzn";\n')
			if 'variable' in c:
				for vname, var in c['variable'].items():
					if var:
						domain = trans_Domain(var.domain, True)
						file.write('%s: %s;\n' % (domain, vname))
					else:
						...
						# print('TODO: warning, variable not found')

			if 'parameter' in c:
				for vname, var in c['parameter'].items():
					if var:
						domain = trans_Domain(var.domain)
						file.write('%s: %s;\n' % (domain, vname))
						# print(domain)
					else:
						...
						# print('TODO: warning, parameter found')

			obj = c['objective']
			if obj.allFlag:
				self.constraint_options[filename] = ['all_solutionss']
			for constraint in obj.constraints:
				text = 'constraint \n\t'
				if constraint == obj.target:
					text += '%s = ' % obj.target
				text += trans_Constraint(c['constraint'][constraint].body)
				file.write(text+';\n')

			file.write(trans_Objective(obj))

	# def _get_NameExpr(self, node):

	def _generate_underscoreAssign(self):
		return pyAssign([pyName('_', ctx=Store())], pyNone())

	def visit_AssignmentStmt(self, node):
		u = []
		if node in self.constraint_info:
			u = [self._generate_underscoreAssign()]
		return u+super().visit_AssignmentStmt(node)

	def visit_OpAssignmentStmt(self, node):
		assignStmt = super().visit_OpAssignmentStmt(node)
		u = []
		if node in self.constraint_info:
			u = [self._generate_underscoreAssign()]
		return u+assignStmt

	def visit_SimpleStmt(self, node):
		assignStmt = super().visit_SimpleStmt(node)
		u = []
		if node in self.constraint_info:
			u = [self._generate_underscoreAssign()]
		return u+assignStmt


	def visit_BuiltinCallExpr(self,node):
		if node.func == 'query':
			return self._generate_query(node)
		else:
			return super().visit_BuiltinCallExpr(node)

	def visit_CallExpr(self, node):
		# pprint(vars(node))
		# func_name = node.subexprs[0].name
		if isinstance(node.subexprs[0], dast.NameExpr) and node.subexprs[0].name == 'query':
			return self._generate_query(node)
		else:
			return super().visit_CallExpr(node)


	def _generate_query(self, node):
		# for query called globally, replace the self with global()
		parent_process = node
		while not (isinstance(parent_process, dast.Process) or isinstance(parent_process, dast.Program)):
			# pprint(vars(parent_process))
			if not hasattr(parent_process, 'process'):
				parent_process = parent_process.parent
			else:
				parent_process = parent_process.process

		if isinstance(parent_process, dast.Program):
			target = 'query'
			inferarg = [pyCall(pyName('globals'))]
		else:
			target = pyAttr("self", 'query')
			inferarg = []

		return pyCall(target, args=inferarg, keywords=[(key, self.visit(value)) for key, value in node.keywords])
