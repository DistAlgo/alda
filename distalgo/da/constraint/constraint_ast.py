from da.compiler.dast import DistNode, NameScope


""" MiniZinc AST
Subset of MiniZinc Model
% A MiniZinc model
<model> ::= [ <item> ";" ... ]

% Items
<item>  ::= <include-item>
		  | <var-decl-item>
		  | <assign-item>
		  | <constraint-item> 
		  | <solve-item>


Type-Inst Expressions
<ti-expr> ::= <base-ti-expr>

<base-ti-expr> ::= <var-par> <base-ti-expr-tail>

<var-par> ::= "var" | "par"

<base-type> ::= "bool"
			  | "int"
			  | "float"
			  | "string"

<base-ti-expr-tail> ::= <ident>
					  | <base-type>
					  | <set-ti-expr-tail>
					  | <ti-variable-expr-tail>
					  | <array-ti-expr-tail>
					  | { <expr> "," ... }
					  | <num-expr> ".." <num-expr>

% Type-inst variables
<ti-variable-expr-tail> ::= $[A-Za-z][A-Za-z0-9_]*

% Set type-inst expressions
<set-ti-expr-tail> ::= "set" "of" <base-type>

% Array type-inst expressions
<array-ti-expr-tail> ::= "array" [ <ti-expr> "," ... ] "of" <ti-expr>
					   | "list" "of" <ti-expr>
"""

class DAConstraints(DistNode):
	_fields = []
	def __init__(self, *args):
		"""Populate fields named in "fields" with values in *args."""
		assert(len(self._fields) == len(args))
		for f, a in zip(self._fields, args):
			setattr(self, f, a)

class CSP(NameScope):
	_fields = ['variables', 'constraints', 'objective']
	def __init__(self, parent=None, ast=None):
		super().__init__(parent, ast)
		# self.parameters = []
		self.variables = dict()
		self.constraints = dict()
		self.objective = None
		self._index = str(CSP._index)

	@property
	def unique_name(self):
		return type(self).__name__ + self._index

# a single constraint statement, contains a constraint set
class Constraint(DAConstraints):
	_fields = ['name', 'constraints', 'op']
	def __init__(self, name, constraints, op='and'):
		super().__init__(name, constraints, op)

# class ConstraintSet(DAConstraints):
# 	_fields = ['relation', 'body']


# # detail of a constraint
# class QuantifiedConstraint(DAConstraints):
# 	_fields = ['quantifier', 'domain', 'predicate']

# class DomainSpec(DAConstraints):
# 	_fields = ['name', 'op', 'domain']

# class FunctionalConstraint(DAConstraints):
# 	_fields = ['func_name', 'target', 'domain_spec']



# varaible declaration
class Variable(DAConstraints):
	_fields = ['name', 'domain', 'value']


# domain when declaring variables
# the data structure to store domain:
# DADomain: abstract class
# DomainBasic: int, float, str, bool
#	 type:   string
#	 lowerbound: simple expr
#	 upperbound: simple expr
#	 step: simple expr
# DomainTuple:
#	 elements: a list of domains
# DomainMap or DomainDict:
#	 key: domain
#	 val: domain
# DomainSet:
#	 sub_domain: domain
# DomainMultiSet
#	 sub_domain: domain
class DADomain(DAConstraints):
	_attributes = ['parameter', 'opt']
	def __init__(self, *args):
		self.parameter = None
		self.opt = False
		super().__init__(*args)

class DomainBasic(DADomain):
	_fields = ['type', 'lb', 'ub', 'step']
	def __init__(self, _type, lb= None, ub= None, step= None):
		super().__init__(_type,lb,ub,step)
		if _type == 'float' and step:
			raise ValueError("float type cannot be declared with step")

class DomainTuple(DADomain):
	_fields = ['elements']
	

class DomainMap(DADomain):
	_fields = ['key', 'val']
	

class DomainSet(DADomain):
	_fields = ['domain']

class DomainMultiSet(DADomain):
	_fields = ['domain']
	
class DomainVar(DADomain):
	_fields = ['var']

# objective function
class Objective(DAConstraints):
	_fields = ['op', 'obj']


class Target(DAConstraints):
	_fields = ['variables', 'constraints', 'objective', 'allFlag']




