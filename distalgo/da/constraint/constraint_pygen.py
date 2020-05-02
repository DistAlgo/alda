from da.compiler.pygen import *
from da.compiler import pygen
from pprint import pprint
from . import constraint_ast as cast
import os,io
from da.tools.unparse import Unparser
from .translate_minizinc import Translator

KW_CONSTRAINT = 'constraint'
SOLVER = 'MiniZinc'	# default solver
CONSTRAINT_OBJECT_NAME = "_constraint_object"
KW_PARAMETER = 'pars'

def to_source(tree):
	textbuf = io.StringIO(newline='')
	Unparser(tree, textbuf)
	return textbuf.getvalue()

class PythonGenerator(pygen.PythonGenerator):
	def __init__(self, filename="", options=None):
		super().__init__(filename, options)
		self.constraint_options = dict()	# get from parser, the information of required/inferred parameter
		self.constraint_info = set()		# get from parser, containing the assignment/update statement (if exist) of arguments in query
		self.constraint_obj = dict()		# containing the information of whole constraints, to be passed into Translator
		self.parsing = False
		self.current_constraint = None

	def new_constraint(self, name):
		tmp_constraint = dict()
		tmp_constraint['name'] = name
		tmp_constraint['parameter'] = set()
		tmp_constraint['variable'] = dict()
		tmp_constraint['constraint'] = dict()
		tmp_constraint['target'] = None
		return tmp_constraint

	def _generate_constraint_obj(self):
		target = pyName(CONSTRAINT_OBJECT_NAME, Store())
		a = pyAssign([target],
					  Dict([Str(key) for key in self.constraint_options],
						   [Set([Str(v) for v in val['required_parameter']]) 
						   	for _, val in self.constraint_options.items()]))
		return a

	def visit_Program(self, node):
		# if hasattr(node, 'constraint_info'):
		# 	self.constraint_info |= node.constraint_info
		if hasattr(node, 'constraint_options'):
			self.constraint_options.update(node.constraint_options)
			imptquery = ImportFrom('da.constraint.query',[alias('query', None)],0)
			self.preambles.append(imptquery)
			self.preambles.append(self._generate_underscoreAssign())
			self.preambles.append(self._generate_constraint_obj())
		rt = super().visit_Program(node)
		if self.constraint_obj:
			for name, val in self.constraint_obj.items():
				Translator(name).visit(val)
		return rt

	def visit_Process(self, node):
		if hasattr(node, 'constraint_options'):
			self.constraint_options.update(node.constraint_options)
		# if hasattr(node, 'constraint_info'):
		# 	self.preambles.append(imptquery)
		# 	self.constraint_info |= node.constraint_info
		return super().visit_Process(node)

	def parse_parameters(self, node):
		for e in node.elts:
			self.current_constraint['parameter'].add(e.id)

	def visit_Function(self, node):
		if node.name == KW_CONSTRAINT:
			args = self.visit(node.args)
			for i in range(len(args.args)):
				if args.args[i].arg == 'name':
					cname = args.defaults[i].s
					self.current_constraint = self.new_constraint(cname)
					self.current_constraint['parameter'] = self.constraint_options[cname]['parameter']
				elif args.args[i].arg == KW_PARAMETER:
					pass
					# self.parse_parameters(args.defaults[i])
				elif args.args[i].arg == 'variable':
					pass
				else:
					self.error("line %s: invalid argument." % node.lineno)
			self.parsing = True
			body = self.body(node.body)
			self.parsing = False
			self.constraint_obj[self.current_constraint['name']] = self.current_constraint
			self.current_constraint = None
			return []
		elif self.parsing:
			# constraint set, or definition of predicates
			name = node.name
			args = self.visit(node.args)
			if len(args.args) == 0 or len(args.defaults) != 0:
				# constraint, with relation = and/or
				if len(args.args) == 0:
					op = 'and'
				else:
					op = 'or'
				constraints = [b.expr for b in node.body]
				self.current_constraint['constraint'][name] = cast.Constraint(name,constraints,op)
			else:
				# predicate
				pass
			return []
		else:
			return super().visit_Function(node)

	def parse_domain(self, node):
		if isinstance(node, Name):
			# 1. int, str, bool, float, set
			if node.id in {'int', 'str', 'bool', 'float'}:
				return cast.DomainBasic(node.id)
			elif node.id != 'set':
				return node
			else:
				return cast.DomainSet(None)
		elif isinstance(node, Call):
			t = node.func.id
			if t == 'ints' or t == 'floats':
				# 2. ints(x,y[,z]), float(x,y)
				if len(node.args) == 3:
					if t == 'floats':
						self.error("line %s: float type do not have step size." % node.lineno)
						return None
					step = node.args[2]
				elif len(node.args) > 3 or len(node.args) < 2:
					self.error("line %s: wrong number of arguments, expect 2 or 3, got %s." % (node.lineno, len(node.args)))
					return None
				else:
					step = None
				lb = node.args[0]
				ub = node.args[1]
				return cast.DomainBasic(t[:-1],lb,ub,step)
			elif t == 'dict':
				# 4. dict(key=domain, val=domain)
				if len(node.keywords) != 2:
					self.error("line %s: wrong number of argument for declaration of dict type! expect 2, got %s." % (node.lineno, len(node.keywords)))
					return None
				for k in node.keywords:
					if k.arg == 'key':
						key = self.parse_domain(k.value)
					elif k.arg == 'val':
						val = self.parse_domain(k.value)
					else:
						self.error("line %s: wrong argument for declaration of dict type! expect 'key' and 'val', got '%s'." % (node.lineno, k.arg))
						return None
				return cast.DomainMap(key, val)
			elif t == 'Counter':
				# 6. Counter(domain)
				if(len(node.args) > 1):
					self.error("line %s: wrong number of argument for declaration of Counter type! expect 1, got %s." % (node.lineno, len(node.keywords)))
					return None
				domain = self.parse_domain(node.args[0])
				return cast.DomainMultiSet(domain)
			else:
				self.error("line %s: wrong type declaration" % node.lineno)
		elif isinstance(node, Tuple):
			# 3. tuple: (domain, domain, ...)
			element = [self.parse_domain(e) for e in node.elts]
			return cast.DomainTuple(element)
		elif isinstance(node, Subscript):
			# 5. set[domain]
			if node.value.id != 'set':
				self.error("line %s: wrong type declaration" % node.lineno)
			domain = self.parse_domain(node.slice.value)
			return cast.DomainSet(domain)
		# elif isinstance(node, Index):
		else:
			print('parse_domain: unknown domain',node)
			pprint(vars(node))

	def parse_variable(self, node):
		domain =  self.parse_domain(node._ast.annotation)
		self.current_context = Store
		targets = [self.visit(tgt) for tgt in node.targets]
		self.current_context = Load
		for t in targets:
			domain.parameter = bool(t.id in self.current_constraint['parameter'])
			self.current_constraint['variable'][t.id] = cast.Variable(t.id,domain,node.value)

	def parse_constraint(self, node):
		targets = [self.visit(tgt) for tgt in node.targets]
		if len(targets) != 1:
			self.error("line %s: definition of constraints can only have one target" % node.lineno)
			return None
		if isinstance(node.value, dast.BooleanExpr):	# default python boolean expr, no need to do
			# print('todo: constraints: BooleanExpr, maybe nothing todo')
			pass
		elif isinstance(node.value, dast.CallExpr):		# global constraints, other invented operation
			# print('todo: constraints: CallExpr')
			pass
		else:
			print(node.value)
			pprint(vars(node.value))
			self.error("line %s: unsupported constraint type" % node.lineno)
		self.current_constraint['constraint'][targets[0].id] = cast.Constraint(targets[0].id, [node.value])


	# assignment statement under constraint parsing mode: 
	# with annotation: variable
	# without annotation: constraints
	def visit_AssignmentStmt(self, node):
		if self.parsing:
			if isinstance(node._ast,AnnAssign):
				self.parse_variable(node)
			else:
				self.parse_constraint(node)
			return []
		else:
			# u = []
			# if node in self.constraint_info:
			# 	u = [self._generate_underscoreAssign()]
			# return u+super().visit_AssignmentStmt(node)
			return super().visit_AssignmentStmt(node)

	def parse_target(self,node):
		# must be setof, anyof
		if not isinstance(node.value, dast.CallExpr):
			self.error("line %s: the target must be setof or anyof" % node.lineno)
		funcid = node.value.subexprs[0].subexprs[0].name
		args = node.value.subexprs[1]

		# the number of return solutions
		if funcid == 'setof':
			allFlag = True
		elif funcid == 'anyof':
			allFlag = False
		else:
			self.error("line %s: the target must be setof or anyof" % node.lineno)
			return None
		if len(args) == 0:
			self.error("line %s: the target must be setof or anyof" % node.lineno)
			return None
		
		# the first arguemnt of target are the target variables
		var = args[0]
		if isinstance(var, dast.TupleExpr):
			variables = [v.subexprs[0].name if isinstance(v, dast.NameExpr) else v for v in var.subexprs]
		else:
			if isinstance(var, dast.NameExpr):
				variables = [var.subexprs[0].name]
			else:
				variables = [var]
		
		# for variables that is the target of the problem but decalred as parameter, set parameter flag as false
		for v in variables:
			if isinstance(v, str) and v in self.current_constraint['parameter']:
				self.current_constraint['variable'][v].domain.parameter = False

		# active constraints
		constraints = []
		objective = None
		for c in args[1:]:
			if isinstance(c, dast.NameExpr):	# the name of constraint
				constraints.append(c.subexprs[0].name)
			elif isinstance(c, dast.CallExpr):
				# ['func', 'args', 'keywords', 'starargs', 'kwargs']
				funcName = c.subexprs[0].subexprs[0].name
				if funcName == 'to_min' or funcName == 'to_max':	# the optimization goal
					if funcName == 'to_min':
						op = 'min'
					else:
						op = 'max'
					if len(c.subexprs[1]) != 1:
						self.error("line %s: wrong number of argument. expect 1." % node.lineno)
						return None
					objexpr = c.subexprs[1][0]
					if isinstance(objexpr, dast.NameExpr):
						obj = objexpr.subexprs[0].name
					else:
						obj = objexpr
					objective = cast.Objective(op,obj)
				else:
					constraints.append(c)	# global constraint or other self defined constraint
			elif isinstance(c, dast.BooleanExpr):	# boolean constraint
				constraints.append(c)
			else:
				self.error("line %s: invalid constraint" % node.lineno)
				return None

		cset = {c for c in constraints if isinstance(c, str)}
		delset = []
		for c in self.current_constraint['constraint']:
			if c not in cset:
				delset.append(c)
		for c in delset:
			del self.current_constraint['constraint'][c]

		self.current_constraint['target'] = cast.Target(variables,constraints,objective,allFlag)

	def visit_ReturnStmt(self, node):
		if self.parsing and not self.current_constraint['target']:
			if node.value is not None:
				self.parse_target(node)
			else:
				self.error("line %s: the target of the problem is undefined" % node.lineno)
			return []
		else:
			return super().visit_ReturnStmt(node)

	def _generate_underscoreAssign(self):
		return pyAssign([pyName('_', ctx=Store())], pyNone())

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
		if isinstance(node.subexprs[0], dast.NameExpr) and node.subexprs[0].name == 'query':
			return self._generate_query(node)
		else:
			return super().visit_CallExpr(node)


	def _generate_query(self, node):
		# for query called globally, replace the self with global()
		parent_process = node
		while parent_process and not (isinstance(parent_process, dast.Process) or isinstance(parent_process, dast.Program)):
			if not hasattr(parent_process, 'process'):
				parent_process = parent_process.parent
			else:
				parent_process = parent_process.process

		if isinstance(parent_process, dast.Program):
			target = 'query'
			inferarg = [pyCall(pyName('globals'))]
		elif not parent_process:
			target = 'query'
			inferarg = [pyTuple([pyCall(pyName('globals')),pyCall(pyName('locals'))])]
		else:
			target = pyAttr("self", 'query')
			inferarg = []

		keywords = [(key, self.visit(value)) for key, value in node.keywords]
		for key, val in keywords:
			if key == 'constraint':
				c = val.s
				var = pyTuple([Str(v) for v in self.constraint_obj[c]['target'].variables])
				keywords.append(('return_value',var))
		return pyCall(target, args=inferarg, keywords=keywords)
