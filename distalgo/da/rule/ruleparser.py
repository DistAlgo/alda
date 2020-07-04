from da.compiler.utils import CompilerMessagePrinter, MalformedStatementError
from da.compiler import dast
from ast import *
from . import ruleast
import sys, os
from .rule_io import write_file,clear_cache
from pprint import pprint
# from .resolver import RuleResolver

KW_RULES = "rules_"
KW_COND = "if_"
KW_INFER = "_infer"

FUNC_NAME_EMPTYSET = "__try_var_defined__"

UniqueUpperCasePrefix = 'V'
UniqueLowerCasePrefix = 'p'


def ruleast_from_daast(daast, filename='<str>', options=None):#, _package=None, _parent=None):
	try:
		rp = Parser(filename, None)
		ruleast = rp.visit(daast)
		rp2 = ParserSecondPass(filename, rp)#, _package, options)
		ruleast = rp2.visit(ruleast)
		sys.stderr.write("%s Rules compiled with %d errors and %d warnings.\n" %
					 (filename, rp2.errcnt, rp2.warncnt))

		if rp2.errcnt == 0:
			return ruleast
	except SyntaxError as e:
		sys.stderr.write("%s:%d:%d: SyntaxError: %s" % (e.filename, e.lineno,
													e.offset, e.text))
	return None


class Parser(NodeTransformer, CompilerMessagePrinter):
	def __init__(self, _filename="", _parent=None):
		CompilerMessagePrinter.__init__(self, _filename, _parent=_parent)
		NodeTransformer.__init__(self)
		self.state_stack = []
		self.filename = _filename
		self.moduleName = os.path.splitext(os.path.basename(self.filename))[0]
		clear_cache(self.moduleName)

	def push_state(self, node):
		self.state_stack.append(node)

	def pop_state(self):
		self.state_stack.pop()

	@property
	def current_scope(self):
		for node in reversed(self.state_stack):
			if isinstance(node, dast.NameScope):
				return node
		return None

	@property
	def current_parent(self):
		return self.state_stack[-1]

	def create_expr(self, exprcls, **params):
		if params is None:
			expr = exprcls(self.current_parent, ast=None)
		else:
			expr = exprcls(self.current_parent, ast=None, **params)
		return expr

	def gen_name(self, node, rule_set=None):
		if not rule_set or node in rule_set.bounded_base:
			return self.create_expr(dast.NameExpr, value=node)
		else:
			# try to resolve the name if it is not bounded:
			# getattr(self, name) if hasattr(self, name) else name
			# even there is no name here, it is possible that the set is empty
			scope = self.current_scope
			while scope:
				if isinstance(scope, dast.ClassStmt):
					selfvar = self.current_scope.find_name('self')
					res = self.create_expr(dast.IfExpr)
					res.condition = self.create_expr(dast.CallExpr)
					res.condition.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('hasattr'))
					res.condition.args = [selfvar, 
										  self.create_expr(dast.ConstantExpr, value=str(node.name))]
					res.condition.keywords = []
					res.body = self.create_expr(dast.CallExpr)
					res.body.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('getattr'))
					res.body.args = [selfvar, 
										  self.create_expr(dast.ConstantExpr, value=str(node.name))]
					res.body.keywords = []
					res.orbody = self.create_expr(dast.NameExpr, value=node)
					return res
				scope = scope.parent
			return self.create_expr(dast.NameExpr, value=node)

	def gen_assignInfer(self, rule_set, user_binding=None):
		""" assign the return value of infer to all bounded derived variables
		the case when queries are not specified
		"""
		derived = list(rule_set.bounded_derived)
		if not derived:
			return None
		queries = self.create_expr(dast.ListExpr,
								   subexprs=[self.create_expr(dast.ConstantExpr, value=v.name) for v in derived])
		stmt = self.create_expr(dast.AssignmentStmt)
		stmt.targets = [self.gen_name(v) for v in derived]
		stmt.value = self.gen_infer_call(rule_set, user_binding, queries)
		for v in rule_set.bounded_derived:
			v.add_assignment(stmt)
		return stmt

	def gen_infer_call(self, rule_set, user_binding=None, user_query=None):
		""" generate infer call of rule_set with user_binding and user_query
		an addition arity argument is added storing the arities of all predicates used in the rule.
		"""
		callinf = self.create_expr(dast.CallExpr)
		func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name(KW_INFER))
		keywords = [('rule',self.create_expr(dast.ConstantExpr, value=self.moduleName+'.'+rule_set.unique_name))]
		arity = self.create_expr(dast.DictExpr)
		allpred = list(rule_set.base)+list(rule_set.derived)
		arity.keys = [self.create_expr(dast.ConstantExpr,value=p.name) for p in allpred]
		arity.values = [self.create_expr(dast.ConstantExpr,value=rule_set.get_arity(p)) for p in allpred]

		keywords.append(('arity', arity))
		keywords.append(('bindings', user_binding))
		keywords.append(('queries', user_query))
		# pprint(vars(callinf))
		callinf.func=func
		callinf.args=[]
		callinf.keywords=keywords
		return callinf
	
	def gen_inline_if(self, userDict, v, rule_set):
		"""generate the following code: 
		userDict[v.name] if v.name in userDict else self.gen_name(v, rule_set)
		""" 
		ifexpr = self.create_expr(dast.IfExpr)
		dm = self.create_expr(dast.ComparisonExpr)
		vstr = self.create_expr(dast.ConstantExpr, value=v.name)
		dm.left = vstr
		dm.right = userDict
		dm.comparator=dast.InOp
		ifexpr.condition = dm
		body = self.create_expr(dast.SubscriptExpr)
		body.value = userDict
		body.index = self.create_expr(dast.ConstantExpr, value=v.name)
		ifexpr.body = body
		ifexpr.orbody = self.gen_name(v, rule_set)
		return ifexpr

### add try except to decide whether a binding can be found at runtime, not used for now ###
	def gen_bind_name(self, name):
		return '__binding_'+name.name+'__'

	def get_bind_name(self, name):
		var = self.current_scope.find_name(self.gen_bind_name(name))
		return self.create_expr(dast.NameExpr, value=var)

	def gen_try_varname(self, userDict, name, rule_set):
		""" generate the following statement
		try:
			__binding_name_ = userDict[name] if name in userDict else \
					getattr(self, name) if hasattr(self, name) else name
		except NameError:
			print('Warning: predicate <name> unbounded, use empty set instead')
			__binding_name_ = set()
		"""
		trystmt = self.create_expr(dast.TryStmt)
		self.push_state(trystmt)
		var = self.current_scope.add_name(self.gen_bind_name(name))
		body = self.create_expr(dast.AssignmentStmt)
		body.targets.append(self.create_expr(dast.NameExpr, value=var))
		body.value = self.gen_inline_if(userDict, name, rule_set)
		trystmt.body.append(body)
		if name in rule_set.bounded_base:
			name.add_read(body)

		exp = self.create_expr(dast.ExceptHandler)
		exp.type = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('NameError'))
		
		warn = self.create_expr(dast.SimpleStmt)
		warn.expr = self.create_expr(dast.CallExpr)
		warn.expr.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('print'))
		warn.expr.args = [self.create_expr(dast.ConstantExpr, value='Warning: predicate %s unbounded, use empty set instead' % name.name)]
		warn.expr.keywords = []
		exp.body.append(warn)

		assign = self.create_expr(dast.AssignmentStmt)
		assign.targets.append(self.create_expr(dast.NameExpr, value=var))
		emptyset = self.create_expr(dast.CallExpr)
		emptyset.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('set'))
		emptyset.args = []
		emptyset.keywords = []
		assign.value = emptyset
		exp.body.append(assign)

		trystmt.excepthandlers.append(exp)
		self.pop_state()
		return trystmt
############################################################################################

	def gen_set_flag(self, flag_var, val):
		""" generate the assignment statement that set the flag to val(True/False)
		"""
		assignstmt = self.create_expr(dast.AssignmentStmt)
		assignstmt.targets = [flag_var]
		boolvar = dast.TrueExpr if val else dast.FalseExpr
		assignstmt.value = self.create_expr(boolvar)
		return assignstmt

	def gen_rule_func_def(self, ruleset):
		""" generate the definition of rule function
		1. complete the parameter of the function. add 'self' as first parameter if ruleset defined in a Class
		2. complete the all base predicate with user input bindings and bounded base variable
		3. generate the call to infer, 
			3.1 set all the context of bounded base predicate to ReadCtx in the infer statement
				so that later, a recursive update of bounded base predicate will be generated
			3.2 call infer with bindings and queries
				3.2.1 if user specifies queries, then directly return the call of infer
				3.2.2 if the user do no specifies queries (or in the case the infer is automatically generated)
					  queries on all bounded derived predicates and assign to corresponding variables
		"""
		scope = self.current_scope
		fd = self.create_expr(dast.Function, name=ruleset.decls)
		self.push_state(fd)
		fd.args = self.create_expr(dast.Arguments)
		while scope:
			if isinstance(scope, dast.ClassStmt):
				fd.args.add_arg('self')
				break
			scope = scope.parent

		fd.args.add_defaultarg('bindings', self.create_expr(dast.NoneExpr))
		fd.args.add_defaultarg('queries', self.create_expr(dast.NoneExpr))

		user_binding = self.create_expr(dast.NameExpr, value=fd.find_name('bindings')) 
		user_query = self.create_expr(dast.NameExpr, value=fd.find_name('queries'))

		# the value of user_bindiing should be a tuple or None,
		# create a If statement, that test user_binding,
		bindingif = self.create_expr(dast.IfStmt)
		self.push_state(bindingif)
		bindingif.condition = user_binding

		# if user_binding is specified, 
		# we want the generated code to be
		# userDict = {key: val for (key,val) in user_binding}
		userDict = self.create_expr(dast.NameExpr, value=fd.add_name('userDict'))
		dictcomp = self.create_expr(dast.DictCompExpr)
		kv = self.create_expr(dast.KeyValue)
		kv.key = self.create_expr(dast.NameExpr, value=dictcomp.add_name('key'))
		kv.value = self.create_expr(dast.NameExpr, value=dictcomp.add_name('val'))
		dictcomp.elem = kv
		dm = self.create_expr(dast.DomainSpec)
		dm.domain = user_binding
		dm.pattern = self.create_expr(dast.TupleExpr, subexprs=[
				self.create_expr(dast.NameExpr, value=dictcomp.find_name('key')),
				self.create_expr(dast.NameExpr, value=dictcomp.find_name('val'))])
		dictcomp.conditions.append(dm)

		# assign the dict comprehension to userDict
		assignUserDict = self.create_expr(dast.AssignmentStmt)
		assignUserDict.targets = [userDict]
		assignUserDict.value = dictcomp
		bindingif.body.append(assignUserDict)

		# if user_binding not specified, assign userDict to empty dict
		emptyUserDict = self.create_expr(dast.AssignmentStmt)
		emptyUserDict.targets = [userDict]
		emptyUserDict.value = self.create_expr(dast.CallExpr)
		emptyUserDict.value.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('dict'))
		emptyUserDict.value.args = []
		emptyUserDict.value.keywords = []
		bindingif.elsebody.append(emptyUserDict)
		self.pop_state()
		fd.body.append(bindingif)

		# for v in ruleset.base:
		# 	fd.body.append(self.gen_try_varname(userDict, v, ruleset))

		# create the binding value by list
		# [UserDict[name] if name in UserDict else RuleDefult, ...]
		bindings = self.create_expr(dast.ListExpr, 
									subexprs=[self.create_expr(dast.TupleExpr, 
															   subexprs=[self.create_expr(dast.ConstantExpr,value=v.name),
																		 # self.get_bind_name(v)]) 
																		 self.gen_inline_if(userDict, v, ruleset)])
											  for v in ruleset.base])
		# assign the list to varialbe bindings
		assignBinding = self.create_expr(dast.AssignmentStmt)
		assignBinding.targets = [user_binding]
		assignBinding.value = bindings
		fd.body.append(assignBinding)

		for v in ruleset.bounded_base:
			v.add_read(assignBinding)
		
		# create an If statement that test queries
		ifstmt = self.create_expr(dast.IfStmt)
		self.push_state(ifstmt)
		ifstmt.condition = self.create_expr(dast.NameExpr, value=user_query)

		# if queries are specified, return the value of infer
		inferexpr = self.gen_infer_call(ruleset, user_binding, user_query)
		rtstmt = self.create_expr(dast.ReturnStmt)
		rtstmt.value = inferexpr
		ifstmt.body.append(rtstmt)

		# else, assign result of infer to derived variables
		inferstmt = self.gen_assignInfer(ruleset, user_binding)
		if inferstmt:
			ifstmt.elsebody.append(inferstmt)
			for d in ruleset.bounded_derived:
				if hasattr(d, 'flag_var'):
					ifstmt.elsebody.append(self.gen_set_flag(d.flag_var, False))
		else:
			# if no derived predicate are bounded and the user calls infer without specifying query, raise an error
			raiseError = self.create_expr(dast.RaiseStmt)
			raiseError.expr = self.create_expr(dast.CallExpr)
			raiseError.expr.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('Exception'))
			raiseError.expr.args = [self.create_expr(dast.ConstantExpr, value='%s: queries not specified and no derived variables are defined' % ruleset.decls)]
			raiseError.expr.keywords = []
			ifstmt.elsebody.append(raiseError)

		self.pop_state()
		fd.body.append(ifstmt)
		
		self.pop_state()
		return fd

	def visit_Function(self, node):
		""" replace the definition of function rules_xxx to a function the can be called with 2 parameters: bindings and queries
		"""
		if node.name.startswith(KW_RULES):# if node.name == KW_RULES:
			ruleset = RuleParser(self.filename, self).visit(node)
			if not hasattr(self.current_scope, 'rulesets'):
				self.current_scope.rulesets = dict()
			self.current_scope.rulesets[ruleset.decls] = ruleset
			res = self.gen_rule_func_def(ruleset)
			return res
		else:
			return self.visit_Scope(node)

	# def printNode(self, node):
	# 	print(type(node).__name__)
	# 	pprint(vars(node))
	# 	return self.generic_visit(node)

	def visit_Scope(self, node):
		self.push_state(node)
		res = self.generic_visit(node)
		self.pop_state()
		return res

	visit_ClassStmt = visit_Scope
	visit_InteractiveProgram = visit_Scope
	# visit_Program = visit_Scope
	visit_Process = visit_Scope

	def visit_Program(self, node):
		self.push_state(node)
		# add the import of infer at the front
		imptinfer = self.create_expr(dast.ImportFromStmt)
		imptinfer.module = 'da.rule.infer'
		imptinfer.items.append(self.create_expr(dast.Alias, name=KW_INFER))
		nobj = self.current_scope.add_name(KW_INFER)
		nobj.add_assignment(imptinfer)
		res = self.generic_visit(node)
		res.body.insert(0,imptinfer)
		self.pop_state()
		return res

class RuleParser(NodeVisitor, CompilerMessagePrinter):
	def __init__(self, filename="", _parent=None):
		CompilerMessagePrinter.__init__(self, filename, _parent=_parent)
		NodeVisitor.__init__(self)
		self.current_rule = None
		self.filename = filename
		self.moduleName = os.path.splitext(os.path.basename(self.filename))[0]

	def add_flag_vars(self, var):
		""" add a update flag variable correponding to var
		"""
		(ctx, (loc, _)) = var._indexes[0]
		assert ctx is dast.AssignmentCtx
		scope = var.scope
		flag_var_name = '_' + scope.unique_name + '_' + var.name + '_infer_flag__'
		flag_var = scope.add_name(flag_var_name)
		var.flag_var = flag_var

	def visit_Function(self, node):
		if node.name.startswith(KW_RULES): # if node.name == KW_RULES:
			self.current_rule = ruleast.RuleSet(node.parent, node.ast)
			self.current_rule.decls = node.name
			self.current_rule.rules = [self.visit(r.expr) for r in node.body]
			res = self.current_rule
			self.current_rule = None
			
			# write the rule to file, and add the file name to RuleSet object
			res.filename = self.moduleName + '.' + res.unique_name
			write_file(res.filename+'.rules', XSBTranslator().visit(res))

			# check if any derived variable can be automatically maintained
			# 	condition: all base predicates are bounded and some derived predicates are bounded
			# add a field 'trigger_infer' to the variable, the field is a set of RuleSet
			if len(res.base) == len(res.bounded_base) and len(res.bounded_derived) > 0:	
				for v in res.bounded_base:
					if not hasattr(v, 'trigger_infer'):
						v.trigger_infer = set()
					v.trigger_infer.add(res)
				for v in res.bounded_derived:
					if not hasattr(v, 'flag_var'):
						self.add_flag_vars(v)
						v.flag_var.set_scope(v.scope)
					if not hasattr(v, 'infer'):
						v.infer = set()
					elif res in v.infer:
						self.error('Variable %s defined as derived predicate for multiple RuleSet' % v.name, node)
					v.infer.add(res)

			for v in res.bounded_derived:
				setattr(v, 'no_updates', True)

			return res
		else:
			self.error("Invalid formalization of rule set: \
				function definition is not allowed in the scope of rule set", node.name)

	def visit_IfExpr(self, node):
		""" rules in form of: if hypos: concl
		"""
		raise NotImplementedError

	def visit_TupleExpr(self, node):
		""" rules of form: p1, if_(p2,...)
		conclusion must be of from p(a1,...)
		conditions must start with if_
		"""
		if len(node.subexprs) != 2 or \
		   not isinstance(node.subexprs[0], dast.CallExpr) or \
		   not (isinstance(node.subexprs[1],dast.CallExpr) and node.subexprs[1].func.name == KW_COND): 
			self.error('ERROR: invalid formalization of rules', node)
			return

		concl = self.visit(node.subexprs[0])
		hypos = self.visit(node.subexprs[1])
		return ruleast.Rule(concl,hypos)

	def visit_CallExpr(self,node):
		if node.func.name == KW_COND:
			return [self.visit(a) for a in node.args]
		return ruleast.Assertion(self.current_rule.add_name(node.func.name), [self.visit(a) for a in node.args])

	def visit_NameExpr(self,node):
		return ruleast.LogicVar(node.name)

	def visit_NamedVar(self,node):
		return ruleast.LogicVar(node.name)

	def visit_ConstantExpr(self,node):
		if isinstance(node.value, str):
			return ruleast.LogicVar("'%s'" % node.value)
		elif isinstance(node.value, bytes):
			self.error('ERROR: invalid predicate', node.value)
		else:
			return ruleast.LogicVar(node.value)

	def visit_TrueExpr(self, node):
		return ruleast.LogicVar("'True'")

	def visit_FalseExpr(self, node):
		return ruleast.LogicVar("'False'")

	def visit_NoneExpr(self, node):
		return ruleast.LogicVar("'None'")

class XSBTranslator(NodeVisitor):

	def visit_RuleSet(self, node):
		return ':- auto_table.\n'+'\n'.join(self.visit(rule) for rule in node.rules)
	
	def visit_Rule(self, node):
		if node.hypos == None: 
			return self.visit(node.concl) + '.'
		return self.visit(node.concl) + ' :- ' + \
				','.join(self.visit(assrtn) for assrtn in node.hypos) + '.'
	
	def visit_Assertion(self, node):
		return self.visit(node.pred) + '(' + \
				','.join(self.visit(arg) for arg in node.args) + ')'
	
	def visit_LogicVar(self, node):
		if node.name == '_':
			return node.name
		elif not isinstance(node.name,str) or node.name.startswith("'"):
			return str(node.name)
		else:
			return UniqueUpperCasePrefix + node.name
	
	def visit_NamedVar(self, node):
		return UniqueLowerCasePrefix + node.name



from functools import cmp_to_key
def sort_rulesets(a,b):
	if not a.derived.isdisjoint(b.base):
		return -1
	else:
		return 1

KW_INFER_CALL = "infer"

class ParserSecondPass(NodeTransformer, CompilerMessagePrinter):
	def __init__(self, _filename="", _parent=None):#, _package=None, options=None):
		CompilerMessagePrinter.__init__(self, _filename, _parent=_parent)
		NodeTransformer.__init__(self)
		self.state_stack = []
		self.filename = _filename
		self.moduleName = os.path.splitext(os.path.basename(self.filename))[0]
		# self.resolver = RuleResolver(_filename, options,
		# 						 _package if _package else options.module_name,
		# 						 _parent=self)

	def push_state(self, node):
		self.state_stack.append(node)

	def pop_state(self):
		self.state_stack.pop()

	@property
	def current_scope(self):
		for node in reversed(self.state_stack):
			if isinstance(node, dast.NameScope):
				return node
		return None

	@property
	def current_parent(self):
		return self.state_stack[-1]

	def visit_Scope(self,node):
		self.push_state(node)
		res = self.generic_visit(node)
		self.add_implicit_infer(node)
		self.pop_state()
		return res

	visit_Function = visit_Scope
	visit_ClassStmt = visit_Scope
	visit_InteractiveProgram = visit_Scope
	visit_Program = visit_Scope
	visit_Process = visit_Scope

	def create_expr(self, exprcls, **params):
		if params is None:
			expr = exprcls(self.current_parent, ast=None)
		else:
			expr = exprcls(self.current_parent, ast=None, **params)
		return expr
	
	def gen_set_flag(self,flag_var, val):
		""" generate the assignment statement that set the flag to val(True/False)
		"""
		assignstmt = self.create_expr(dast.AssignmentStmt)
		assignstmt.targets = [flag_var]
		boolvar = dast.TrueExpr if val else dast.FalseExpr
		assignstmt.value = self.create_expr(boolvar)
		return assignstmt

	def gen_infer_at_use(self, d, rs):
		""" generate infer before the use of variable d with ruleset rs. 
		1. test d's update flag before generation
		2. recusively call gen_infer_at_use on bounded base predicate of ruleset rs before infering d
		3. set d's update flag to false
		"""
		ifstmt = self.create_expr(dast.IfStmt)
		self.push_state(ifstmt)
		ifstmt.condition = d.flag_var
		func = self.find_rules_func(rs.decls)
		body = self.create_expr(dast.SimpleStmt)
		body.expr = self.gen_rule_func_call(func)
		ifstmt.body.append(body)
		self.pop_state()
		return ifstmt

	def gen_rule_func_call(self, func, bindings=None, queries=None):
		rulecall = self.create_expr(dast.CallExpr)
		rulecall.func = func
		keywords = []
		if bindings:
			keywords.append(('bindings', bindings))
		if queries:
			keywords.append(('queries', queries))
		rulecall.keywords = keywords
		rulecall.args = []
		return rulecall

	def insert_at_any_body_at_stmt(self, stmt, inserts, before=False):
		""" insert before/after stmt
		"""
		for body in ['body', 'elsebody', 'finalbody']:
			if not hasattr(stmt.parent, body):
				continue
			for i, b in enumerate(getattr(stmt.parent, body)):
				if b is stmt:
					for j, ins in enumerate(inserts):
						getattr(stmt.parent, body).insert(i+j+(0 if before else 1), ins)
					return

	def add_implicit_infer(self, node):
		""" add implicit function call of infer to Scope: node
		add infer before the use of derived predicates
		"""
		if hasattr(node, 'rulesets'):
			override_dict = dict()	# key: function_name, val: tuple: (function, (dict key: stmt, val: set of ruleset))
			setup_init = set()		# set of ruleset
			for rs in sorted(node.rulesets.values(), key=cmp_to_key(sort_rulesets)):	# iterate through rulesets
				# only generate infer when all the base predicates are bounded and some derived predicates are bounded
				if rs.unbounded_base or not rs.bounded_derived:
					continue

				# add infer calls when derived predicates are used (ReadCtx)
				for d in rs.bounded_derived:
					for (ctx, (loc, _)) in d._indexes:
						if ctx is not dast.ReadCtx:
							continue
						stmt = loc.statement if isinstance(loc, dast.Expression) else loc
						self.insert_at_any_body_at_stmt(stmt, [self.gen_infer_at_use(d, rs)], True)
				
				# set the update flag of all derived predicates to True if a base predicate is assigned or updated
				for b in rs.bounded_base:
					if not hasattr(b, 'trigger_infer') or rs not in b.trigger_infer:
						continue
					for (ctx, (loc, _)) in b._indexes:
						if not (ctx is dast.AssignmentCtx or ctx is dast.UpdateCtx):
							continue
						stmt = loc.statement if isinstance(loc, dast.Expression) else loc
						flagstmts = [self.gen_set_flag(d.flag_var, True) for d in rs.bounded_derived]
						self.insert_at_any_body_at_stmt(stmt, flagstmts)

	def find_rules_func(self, name):
		scope = self.current_scope
		attr = self.create_expr(dast.AttributeExpr)
		attr.value = self.current_scope.find_name('self')
		attr.attr = name
		while scope:
			var = scope.find_name(name)
			if var:
				if isinstance(scope, dast.ClassStmt):
					return attr
				else:
					return self.create_expr(dast.NameExpr, value=var)
			else:
				scope = scope.parent
		return attr

	def visit_CallExpr(self, node):
		if isinstance(node.func, dast.NameExpr) and node.func.name == KW_INFER_CALL:
			# check that the infer function is imported from da.rule.infer, 
			# not something else overridened by the user
			whereinfer = None
			scope = self.current_scope
			while not whereinfer and scope:
				whereinfer = scope.find_name(KW_INFER).last_assignment_before(node)
				scope = scope.parent_scope
			if not (isinstance(whereinfer, dast.ImportFromStmt) and whereinfer.module == 'da.rule.infer'):
				return self.generic_visit(node)
		
			rule_name = None
			user_binding = None
			user_query = None

			if node.keywords:
				for key, val in node.keywords:
					if key == 'rule':
						rule_var = val
					elif key == 'bindings':
						user_binding = val
					elif key == 'queries':
						user_query = val
					else:
						self.warn('Invalid argument %s in call of infer, ignored' % key, node)
			if not rule_var:
				self.error('Infer function requires keyword argument: rule', node)
			
			rulecall = self.gen_rule_func_call(rule_var, user_binding, user_query)
			return rulecall
		else:
			return self.generic_visit(node)

#################### infer at update: not used any more ####################
	def add_infer_direct(self, ruleset, stmt):
		""" add call of infer directly after stmt
		"""
		parent = stmt.parent
		assert isinstance(parent, dast.NameScope)
		if (isinstance(parent.parent, dast.Process) and parent.name == "setup") or \
		   (isinstance(parent.parent, dast.ClassStmt) and parent.name == "__init__"):
			return parent.name
		
		inferstmt = self.gen_assignInfer(ruleset)
		for i, ele in enumerate(parent.body):
			if ele is stmt:	# and ruleset.all_initialized_by(ele):
				parent.body.insert(i+1, inferstmt)

	def gen_infer_simpified(self, node, func_name=None, rulesets=None):
		""" simplified processing of infer 
		for functions that already exist in scope, 
			add all infers at the end of the function
		for functions that need to overriden, 
			generate functions whose bodies are of the following form:
				super().func_name(...)
				infer(...)
		"""
		# if func_name not provided, generate infer for setup/init by default
		if not func_name:
			func_name = "setup" if isinstance(node, dast.Process) else "__init__"
		if not rulesets:
			assert hasattr(node, 'rulesets')
			rulesets = node.rulesets.values()

		# get the function need to be added infer, 
		# if not exist in current scope, generate override function
		newfunc = False
		if func_name == "setup" and isinstance(node, dast.Process):
			if node.setup:
				func = node.setup
			else:
				newfunc = "setup"
		else:
			s = node.find_name(func_name)
			func = s.parent_scope
			if func.parent_scope is not node:
				newfunc = True
		if newfunc:
			func = self.create_expr(dast.Function, name=func_name)
			if newfunc == "setup":
				node.setup = func
				arguments = node.args
			else:
				node.body.append(func)
				arguments = None
			basefunc = node.find_name(func_name)
			supercall = self.gen_super_call(basefunc, arguments)
			func.body.append(supercall)

		# add all the infers at the end of function
		# infer functions following the order that, 
		# for rulesets a and b, if a.derived are b.base, then infer a before b
		for rs in sorted(rulesets, key=cmp_to_key(sort_rulesets)):
			inferstmt = self.gen_assignInfer(rs)
			if inferstmt:
				func.body.append(inferstmt)

	def gen_super_call(self, func_name, setupargs=None):
		""" generate the statement of calling super().func(...)
		"""
		basefunc = func_name.parent
		call = self.create_expr(dast.CallExpr)
		spfunc = self.create_expr(dast.AttributeExpr)
		spfunc.attr = func_name.name
		spfunc.value = self.create_expr(dast.CallExpr)
		spfunc.value.basefunc = self.create_expr(dast.NameExpr, value=func_name)
		spfunc.value.args = []
		spfunc.value.keywords = []
		call.basefunc = spfunc
		if func_name.name == "setup": # Process
			arguments = setupargs
		else:	# __init__ in Class
			arguments = basefunc.args
		call.args = [a.clone() for a in arguments.args]
		call.keywords = [a.clone() for a in arguments.kwonlyargs]
		# deprecated since Python 3.5
		if arguments.vararg is not None:
			call.starargs = arguments.vararg.clone()
		if arguments.kwarg is not None:
			call.kwargs = arguments.kwarg.clone()
		callstmt = self.create_expr(dast.SimpleStmt)
		callstmt.expr = call
		return callstmt

	def gen_infer_override(self, node, func_dict):
		res = []
		# key: func_name, val: (container_function, stmt, rs)
		for func_name, val in func_dict.items():
			# override setup/init function:
			if isinstance(node, dast.Process) and func_name == "setup" or \
			   isinstance(node, dast.ClassStmt) and func_name == "__init__":
				rls = set.union(*[rs for _,rs in val.items()])
				self.gen_infer_simpified(node, func_name, rls)
				continue

			# if the function inherits multiple functions, then simplify to a super call and infer
			funcs = {c for c,_,_ in val}
			if len(funcs) > 1:
				rls = set.union(*[rs for _,rs in val.items()])
				self.gen_infer_simpified(node, func_name, rls)
				continue
			
			# override regular function
			position_dict = dict() # key: index of statement, val: list of infer functions
			for func, stmt, ruleset in val:
				for i, ele in enumerate(func.body):
					if ele is stmt:
						if i not in position_dict:
							position_dict[i] = []
						inferstmt = self.gen_assignInfer(ruleset)
						if inferstmt:
							position_dict[i].append(inferstmt)
						break
			count = 1
			newfunc = func.clone()
			for i, infers in sorted(position_dict.items()):
				count += i
				for j in infers:
					newfunc.body.insert(count, j)
					count += 1
			if isinstance(node, dast.Process):
				node.methods.append(newfunc)
			else:
				node.body.append(newfunc)

	def add_implicit_infer_at_update(self, node):
		""" add implicit function call of infer to Scope: node
		add infer after each update to base predicate
		not used any more
		"""
		if hasattr(node, 'rulesets'):
			override_dict = dict()	# key: function_name, val: tuple: (function, (dict key: stmt, val: set of ruleset))
			setup_init = set()		# set of ruleset
			for _, rs in node.rulesets.items():	# iterate through rulesets
				for v in rs.bounded_base:		# iterate through all bounded base predciates
					if not hasattr(v, 'trigger_infer') or rs not in v.trigger_infer:
						continue
					for (ctx, (loc, _)) in v._indexes:	# iterate through the index
						# find the assignments/updates
						if not (ctx is dast.AssignmentCtx or ctx is dast.UpdateCtx):
							continue
						# find the statement containing the assignments/updates
						stmt = loc.statement if isinstance(loc, dast.Expression) else loc 
						
						# case 1: the rule is defined in Program/Function, kind of globally
						if isinstance(node, (dast.Program, dast.Function)):
							if self.add_infer_direct(rs, stmt):
								# if the container function is setup/init, process differently
								setup_init.add(rs)
						# case 2: the rule is defined in Class/Process, need to deal with inheritence
						else:
							scope = stmt.parent
							container_function = None
							# check if the statement appears at current scope
							while scope and scope is not node:
								# get the function containing the statement
								if not container_function and isinstance(scope, dast.Function):
									container_function = scope
								scope = scope.parent

							# the function is defined in base classes
							if not scope:
								if container_function.name in {"setup", "__init__"}:
									setup_init.add(rs)
									continue
								if container_function.name not in override_dict:
									override_dict[container_function.name] = set()
								# if stmt not in override_dict[container_function.name]:
								# 	override_dict[container_function.name][stmt] = set()
								override_dict[container_function.name].add((container_function, stmt, rs))
							else:
								# the function is in current class, directly add call of infer after stmt
								if self.add_infer_direct(rs, stmt):
									# the container function is setup/init
									setup_init.add(rs)
			if override_dict:
				self.gen_infer_override(node, override_dict)
			if setup_init:
				self.gen_infer_simpified(node)
