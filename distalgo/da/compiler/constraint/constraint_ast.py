from da.compiler.dast import DistNode


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
		# print('fields:', self._fields)
		# print('args:', args)
		assert(len(self._fields) == len(args))
		for f, a in zip(self._fields, args):
			setattr(self, f, a)

# class CSP(DAConstraints):
# 	_fields = ['parameter', 'variable', 'constraint', 'objective']

# a single constraint statement, contains a constraint set
class Constraint(DAConstraints):
	_fields = ['name', 'body']

class ConstraintSet(DAConstraints):
	_fields = ['relation', 'body']


# detail of a constraint
class QuantifiedConstraint(DAConstraints):
	_fields = ['quantifier', 'domain', 'predicate']

class DomainSpec(DAConstraints):
	_fields = ['name', 'op', 'domain']

class FunctionalConstraint(DAConstraints):
	_fields = ['func_name', 'target', 'domain_spec']



# varaible declaration
class Variable(DAConstraints):
	_fields = ['name', 'domain']

class Parameter(DAConstraints):
	_fields = ['name', 'domain']


# domain when declaring variables
class DomainBasic(DAConstraints):
	_fields = ['type', 'range']

class DomainArray(DAConstraints):
	_fields = ['dimension', 'domain']

class DomainSet(DAConstraints):
	_fields = ['domain']


# objective function
class Objective(DAConstraints):
	_fields = ['operation', 'target', 'allFlag', 'constraints']


class QueryStmt(DAConstraints):
	_fields = ['cname', 'parameters']




