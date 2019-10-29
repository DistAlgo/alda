from ..parser import *
from .. import parser
from . import constraint_ast as cast

from pprint import pprint
import json


KW_CONSTRAINT = 'constraint'
DirectOperatorMap = {
	'anyof': 'satisfy',
	'setof': 'satisfy',
	'maxof': 'maximize',
	'minof': 'minimize'
}
InDirectOperator = {'countof', 'sumof', 'lenof'}


def gensym(prefix):
    i = 0
    while True:
        i += 1
        yield prefix+str(i)

generator = gensym('obj_')


class Parser(parser.Parser):

	def __init__(self, filename="", options=None, execution_context=None,
				 _package=None, _parent=None):
		super().__init__(filename, options, execution_context,
				 _package, _parent)
		self.current_constraint = None

	def visit_Domain(self, node):
		# int
		# ints(1,n)
		# dict(key=(ints(1,n),ints(1,n)),val=ints(1,n))		array[1..n,1..n] of var 1..n: x;
		# setof(ints(1..n))									set of int: HEIGHT = 0..h;
		if isinstance(node, Tuple):
			return [self.visit_Domain(i) for i in node.elts]
		if isinstance(node, Name):
			return cast.DomainBasic(node.id, None)
		if isinstance(node, Call):
			if node.func.id == 'dict':
				for k in node.keywords:
					if k.arg == 'key':
						key = self.visit_Domain(k.value)
					elif k.arg == 'val':
						val = self.visit_Domain(k.value)
				return cast.DomainArray(key, val)
			elif node.func.id == 'setof':
				return cast.DomainSet(self.visit_Domain(node.args[0]))
			elif node.func.id == 'ints' or node.func.id == 'floats':
				ranges = [str(i.n) if isinstance(i, Num) else str(i.id) for i in node.args]
				return cast.DomainBasic(node.func.id[:-1], ranges)
			else:
				print('!!!!!!!!!! TODO !!!!!!!!!!')
				pprint(node.func.id)
				return cast.DomainBasic(node.func.id, None)


	def visit_AnnDelcare(self,node):
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
		# pprint(vars(node))
		
		name = node.target.id
		domain = self.visit_Domain(node.annotation)
		# print(domain)
		# pprint(vars(domain))
		if 'parameter' in self.current_constraint and name in self.current_constraint['parameter']:
			self.current_constraint['parameter'][name] = cast.Variable(name, domain)
		else:
			self.current_constraint['variable'][name] = cast.Variable(name, domain)


	def visit_Constraint(self,node):
		if isinstance(node, Expr):
			return self.visit_Constraint(node.value)
		return self.visit(node)

	def visit_ConstraintSet(self, node):
		if isinstance(node, list):
			body = [self.visit_ConstraintSet(i.value) for i in node]
			return cast.ConstraintSet(And(), body)
		if isinstance(node, BoolOp):
			relation = node.op
			body = [self.visit_ConstraintSet(i) for i in node.values]
			return cast.ConstraintSet(relation, body)
		if isinstance(node, Compare):
			# print('visit_ConstraintSet: Compare')
			# pprint(vars(node))
			return self.visit_Compare(node)

		return self.visit_Constraint(node)


	def visit_Objective(self, node):
		if isinstance(node, Call):
			allFlag = False
			op = node.func.id
			if op in DirectOperatorMap:
				operation = DirectOperatorMap[op]
				if op == 'setof':
					allFlag = True
			else:
				...
				# TODO: InDirectOperator = {'countof', 'sumof', 'lenof'}

			constraints = []
			# print('cparser: visit_Objective')
			for c in node.args:
				# pprint(vars(c))
				if isinstance(c, Name):
					constraints.append(c.id)
				else:
					tmpName = next(generator)
					constraints.append(tmpName)
					if isinstance(node, BoolOp) or isinstance(node, Compare):
						body = visit_ConstraintSet(node)
					else:
						# augConstraint = Compare(left=Name(id=tmpName), ops = [Eq()], comparators=[c])
						body = self.visit_ConstraintSet(c)
						self.current_constraint['variable'][tmpName] = cast.Variable(tmpName, cast.DomainBasic('int', None))
						# TODO: automatic type detection
						...

					# pprint(vars(body))
					self.current_constraint['constraint'][tmpName] = cast.Constraint(tmpName, body)
					constraints.append(tmpName)

			if constraints[0] not in self.current_constraint['variable']:
				self.current_constraint['variable'][constraints[0]] = cast.Variable(constraints[0], cast.DomainBasic('int', None))
				return cast.Objective(operation, constraints[0], allFlag, constraints)

			return cast.Objective(operation, constraints[0], allFlag, constraints[1:])

		else:
			# raise MalformedStatementError('Error specifying the opjective.', node)
			print('Malformed Objective Declaration', node)

	def visit_DomainSpec(self, node):
		# print('><><><><><><><><><><><><><><><><>< visit_DomainSpec')
		# pprint(node)
		# pprint(vars(node))
		if isinstance(node, Compare):
			op = node.ops[0]
			name = node.left.id
			domain = self.visit_Domain(node.comparators[0])
		elif isinstance(node, comprehension):
			op = In()
			name = node.target.id
			domain = self.visit_Domain(node.iter)
		else:
			print('><><><><><><><><><><><><><><><><>< visit_DomainSpec')
			print(node)
			pprint(vars(node))

		return cast.DomainSpec(name, op, domain)

	def visit_Predicate(self, node):
		# print('><><><><><><><><><><><><><><><><>< visit_Predicate')
		# pprint(vars(node))
		if isinstance(node, Call):
			func_name = node.func.id
			target = self.visit(node.args[0].elt)
			domain_spec = [self.visit_DomainSpec(i) for i in node.args[0].generators]
			return cast.FunctionalConstraint(func_name, target, domain_spec)
		elif isinstance(node, BoolOp):
			body = [self.visit_Predicate(b) for b in node.values]
			return cast.ConstraintSet(node.op, body)
		elif isinstance(node, Compare):
			return self.visit(node)
		else:
			print('TODO: ><><><><><><><><><><><><><><><><>< visit_Predicate')
			print(node)
			pprint(vars(node))


	def parse_quantified_expr(self, node):
		if self.current_constraint:
			quantifier = node.func.id
			domains = [self.visit_DomainSpec(i) for i in node.args]
			# pprint(vars(domains[0]))
			predicates = [self.visit_Predicate(i.value) for i in node.keywords]
			return cast.QuantifiedConstraint(quantifier, domains, predicates)
		else:
			super().parse_quantified_expr(node)

	def compile_constraint(self, node):
		"""
		def constraint(name=, variable={x}, parameter={n}):
		
		"""
		self.current_constraint = dict()
		numArgs = len(node.args.args)
		for i in range(numArgs):
			if node.args.args[i].arg == 'name':
				self.current_constraint['name'] = node.args.defaults[i].s
			if node.args.args[i].arg == 'variable':
				self.current_constraint['variable'] = dict()
				for e in node.args.defaults[i].elts:
					self.current_constraint['variable'][e.id] = None
			if node.args.args[i].arg == 'parameter':
				self.current_constraint['parameter'] = dict()
				for e in node.args.defaults[i].elts:
					self.current_constraint['parameter'][e.id] = None

		self.current_constraint['constraint'] = dict()

		for s in node.body:
			if isinstance(s, AnnAssign):
				r = self.visit_AnnDelcare(s)
			elif isinstance(s, Assign):
				name = s.targets[0].id
				body = self.visit_ConstraintSet(s.value)
				self.current_constraint['constraint'][name] = cast.Constraint(name, body)
			elif isinstance(s, FunctionDef):
				name = s.name
				body = self.visit_ConstraintSet(s.body)
				self.current_constraint['constraint'][name] = cast.Constraint(name, body)
			elif isinstance(s, Return):
				self.current_constraint['objective'] = self.visit_Objective(s.value)

		if hasattr(self.program,'constraints'):
				self.program.constraints.append(self.current_constraint)
		else:
			self.program.constraints = [self.current_constraint]

		self.current_constraint = None
		# pprint(self.current_constraint)


	def visit_FunctionDef(self, node):
		if node.name == KW_CONSTRAINT:
			self.compile_constraint(node)
		elif node.name == 'ints':
			return self.visit_Domain(node)
		else:
			super().visit_FunctionDef(node)

	def visit_Call(self,node): 
		if isinstance(node.func, Name) and node.func.id == 'query':
			if not hasattr(self.program, 'constraint_info'):
				self.program.constraint_info = set()
			for k in node.keywords:
				if k.arg != 'constraint':
					if isinstance(k.value, Name):
						par = self.current_scope.find_name(k.value.id)
						for i in par._indexes:
							if i[0] == dast.AssignmentCtx or i[0] == dast.UpdateCtx:
								# print(i[1][0])
								self.program.constraint_info.add(i[1][0])
		return super().visit_Call(node)










