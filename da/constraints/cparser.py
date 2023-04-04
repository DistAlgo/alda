from da.compiler.utils import CompilerMessagePrinter, MalformedStatementError, set_debug_level, get_debug_level
from da.compiler import dast
from argparse import Namespace
from da.compiler.parser import Parser as daParser
from ast import *
from . import constraint_ast as cast
from .translate_minizinc import Translator
import sys
import os
from pprint import pprint
from .csp_io import write_file, clear_cache


KW_CONSTRAINT = "csp_"
KW_QUERY = "_query"


def cast_from_daast(daast, filename='<str>', options=None):  # , _package=None, _parent=None):
    try:
        cp = Parser(filename, None)
        cspast = cp.visit(daast)
        sys.stderr.write("%s Constraints compiled with %d errors and %d warnings.\n" %
                         (filename, cp.errcnt, cp.warncnt))

        if cp.errcnt == 0:
            return cspast
    except SyntaxError as e:
        sys.stderr.write("%s:%d:%d: SyntaxError: %s" % (e.filename, e.lineno,
                                                        e.offset, e.text))
    return None


def daast_from_str(src):
    debug_level = get_debug_level()
    set_debug_level(0)
    ag = Namespace()
    ag.module_name = ''
    dt = daParser('', ag)
    rawast = parse(src, '')
    dt.visit(rawast)
    set_debug_level(debug_level)
    return dt.program.body


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

    def visit_Function(self, node):
        """ replace the definition of function cons_xxx to a function the can be called with parameters
        """
        if node.name.startswith(KW_CONSTRAINT):
            csparser = CSPParser(self.filename, self)
            cspAST = csparser.visit(node)
            if csparser.errcnt != 0:
                return None
            txt = Translator(self.filename, self).visit(cspAST)
            tarfile = '%s.%s_%s.mzn' % (self.moduleName, cspAST.unique_name, node.name)
            write_file(tarfile, txt)

            # generate the function in the following form
            # 	result = _query(...)
            # 	rtn = dict()
            # 	for r in result:
            # 		if r in cspAST.objective.variables or r == 'objective':
            # 			rtn[r] = result[r]
            # 	return rtn
            func_template = """result = {KW_QUERY}('{RuleTarget}', {KWARGS})\n
rtn = list()\n
returnVars = [{ReturnVars}]\n
if not result:\n
	print('Unsatisfiable!')\n
	if len(returnVars) == 1:\n
		return None\n
	else:\n
		return (None,)*len(returnVars)\n
for r in returnVars:\n
	if r in result:\n
		rtn.append(result[r])\n
	elif "objective" in result and r == {OBJNAME}:\n
		rtn.append(result["objective"])\n
if len(rtn) == 1:\n
	return rtn[0]\n
else:\n
	return tuple(rtn)\n
"""
            node.body = []
            self.push_state(node)
            src = func_template.format(
                KW_QUERY=KW_QUERY, RuleTarget=tarfile, KWARGS=', '.join(['%s=%s' % (a.name, a.name) for a in node.args.args]),
                ReturnVars=', '.join(["'%s'" % v for v in cspAST.objective.variables]),
                OBJNAME=None
                if not cspAST.objective.objective or not isinstance(cspAST.objective.objective.obj, str) else "'%s'" % cspAST.objective.objective.obj)

            template_body = daast_from_str(src)
            node.body = template_body
            # result = _query(...)
            # asstmt = self.create_expr(dast.AssignmentStmt)
            # result = self.current_scope.add_name('result')
            # asstmt.targets = [self.create_expr(dast.NameExpr, value=result)]
            # expr = self.create_expr(dast.CallExpr)
            # expr.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name(KW_QUERY))
            # expr.args = [self.create_expr(dast.ConstantExpr, value=tarfile)]
            # expr.keywords = [(a.name, a) for a in node.args.args]
            # asstmt.value = expr
            # node.body.append(asstmt)

            # #rtn = dict()
            # asstmt = self.create_expr(dast.AssignmentStmt)
            # rtn = self.current_scope.add_name('rtn')
            # asstmt.targets = [self.create_expr(dast.NameExpr, value=rtn)]
            # asstmt.value = self.create_expr(dast.CallExpr)
            # asstmt.value.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('dict'))
            # asstmt.value.args = []
            # asstmt.value.keywords = []
            # node.body.append(asstmt)

            # # for r in result:
            # forstmt = self.create_expr(dast.ForStmt)
            # self.push_state(forstmt)
            # domain = self.create_expr(dast.DomainSpec)
            # r = self.current_scope.add_name('r')
            # domain.pattern = self.create_expr(dast.NameExpr, value=r)
            # domain.domain = self.create_expr(dast.NameExpr, value=result)
            # forstmt.domain = domain
            # # if r in $cspAST.objective.variables$ or r == 'objective':
            # ifstmt = self.create_expr(dast.IfStmt)
            # ifstmt.condition = self.create_expr(dast.LogicalExpr)
            # ifstmt.condition.operator = dast.OrOp
            # # r not in $cspAST.objective.variables$
            # testr = self.create_expr(dast.ComparisonExpr)
            # testr.comparator = dast.InOp
            # testr.left = self.create_expr(dast.NameExpr, value=r)
            # testr.right = self.create_expr(dast.ListExpr)
            # testr.right.subexprs = [self.create_expr(dast.ConstantExpr, value=x) for x in cspAST.objective.variables]
            # ifstmt.condition.subexprs.append(testr)
            # # r != 'objective'
            # testr2 = self.create_expr(dast.ComparisonExpr)
            # testr2.comparator = dast.EqOp
            # testr2.left = self.create_expr(dast.NameExpr, value=r)
            # testr2.right = self.create_expr(dast.ConstantExpr, value='objective')
            # ifstmt.condition.subexprs.append(testr2)
            # # rtn[r] = result[r]
            # asstmt = self.create_expr(dast.AssignmentStmt)
            # left = self.create_expr(dast.SubscriptExpr)
            # left.value = self.create_expr(dast.NameExpr,value=rtn)
            # left.index = self.create_expr(dast.NameExpr,value=r)
            # asstmt.targets = [left]
            # right = self.create_expr(dast.SubscriptExpr)
            # right.value = self.create_expr(dast.NameExpr,value=result)
            # right.index = self.create_expr(dast.NameExpr,value=r)
            # asstmt.value=right
            # forstmt.body.append(asstmt)
            # self.pop_state()
            # node.body.append(forstmt)

            # return result
            # rtnstmt = self.create_expr(dast.ReturnStmt)
            # rtnstmt.value = self.create_expr(dast.NameExpr, value=result)
            # node.body.append(rtnstmt)
            self.pop_state()
            return node
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

    def visit_SubscriptExpr(self, node):
        """ int[lb:ub:step] := set(range(lb, ub+1, step))
        do not support the following
                int[:ub] := <= ub
                int[lb:] := >= lb
        """
        if not isinstance(node.value, dast.NameExpr):
            return self.generic_visit(node)
        # print(node)
        # pprint(vars(node.value))
        t = node.value.name
        if t == 'int' and isinstance(node.index, dast.SliceExpr):
            # range(lb, ub+1, step)
            expr = self.create_expr(dast.CallExpr)
            expr.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('range'))
            lower = node.index.lower if isinstance(node.index.lower, dast.Expression) else \
                self.create_expr(dast.ConstantExpr, value=self.visit(node.index.lower))
            upper = node.index.upper if isinstance(node.index.upper, dast.Expression) else \
                self.create_expr(dast.ConstantExpr, value=self.visit(node.index.upper))
            upper1 = self.create_expr(dast.BinaryExpr)
            upper1.left = upper
            upper1.right = self.create_expr(dast.ConstantExpr, value=1)
            upper1.operator = dast.AddOp
            expr.args = [lower, upper1]
            if node.index.step:
                step = node.index.step if isinstance(node.index.step, dast.Expression) else \
                    self.create_expr(dast.ConstantExpr, value=self.visit(node.index.step))
                expr.args.append(step)
            expr.keywords = []
            # set(...)
            setexpr = self.create_expr(dast.CallExpr)
            setexpr.func = self.create_expr(dast.NameExpr, value=self.current_scope.find_name('set'))
            setexpr.args = [expr]
            setexpr.keywords = []
            return setexpr
        else:
            return self.generic_visit(node)

    def visit_Program(self, node):
        self.push_state(node)
        # add the import of infer at the front
        imptquery = self.create_expr(dast.ImportFromStmt)
        imptquery.module = 'da.constraints.query'
        imptquery.items.append(self.create_expr(dast.Alias, name=KW_QUERY))
        nobj = self.current_scope.add_name(KW_QUERY)
        nobj.add_assignment(imptquery)
        res = self.generic_visit(node)
        res.body.insert(0, imptquery)
        self.pop_state()
        return res


class CSPParser(NodeVisitor, CompilerMessagePrinter):
    def __init__(self, filename="", _parent=None):
        CompilerMessagePrinter.__init__(self, filename, _parent=_parent)
        NodeVisitor.__init__(self)
        self.domainParser = DomainParser(filename, self)
        self.current_constraint = None
        self.filename = filename
        self.moduleName = os.path.splitext(os.path.basename(self.filename))[0]

    def visit_Function(self, node):
        if node.name.startswith(KW_CONSTRAINT):
            self.current_constraint = cast.CSP(node.parent, node.ast)
            self.func_pars = {a.name for a in node.args.args}
            if get_docstring(node._ast):
                node.body = node.body[1:]
            for b in node.body:
                self.visit(b)

            all_vars = {n for n in self.current_constraint.variables}
            for n in self.current_constraint.variables:
                if n in self.func_pars:
                    self.current_constraint.variables[n].domain.parameter = True
                elif self.current_constraint.variables[n].value and \
                        all(n in self.func_pars for n in self.current_constraint.variables[n].value.names & all_vars):
                    self.current_constraint.variables[n].domain.parameter = True
                else:
                    self.current_constraint.variables[n].domain.parameter = False

            return self.current_constraint
        else:
            # constraints in forms of function
            # if node.args:
            # 	print(node.args)
            self.current_constraint.constraints[node.name] = cast.Constraint(node.name, [b.expr for b in node.body])

    def visit_AssignmentStmt(self, node):
        t = node.targets[0]
        if not isinstance(t, dast.NameExpr):
            self.error("Invalid assignment expression target. Only variables are allowed", node)
        for stmt, typectx in t.value.assignments:
            if stmt is node:
                if isinstance(typectx, dast.BooleanExpr) or isinstance(typectx, dast.CallExpr):
                    if len(node.targets) != 1:
                        self.error("SyntaxError: contraint can only be assigned to one target", node)
                    self.current_constraint.constraints[t.name] = cast.Constraint(t.name, [node.value])
                else:
                    domain = self.domainParser.visit(typectx)
                    self.current_constraint.variables[t.name] = cast.Variable(t.name, domain, node.value)
                break

    def visit_ReturnStmt(self, node):
        if not isinstance(node.value, dast.CallExpr):
            self.error("Malformed domain declaration: 5", node)

        funcid = node.value.func.name
        args = node.value.args
        if funcid == 'anyof':
            allFlag = True
        elif funcid == 'setof':
            allFlag = False
        else:
            self.error("Malformed domain declaration: 6", node)

        # the first arguemnt of target are the target variables
        var = args[0]
        if isinstance(var, dast.TupleExpr):
            variables = [v.subexprs[0].name if isinstance(v, dast.NameExpr) else v for v in var.subexprs]
        else:
            if isinstance(var, dast.NameExpr):
                variables = [var.subexprs[0].name]
            else:
                variables = [var]

        # variables that is the target of the problem are variables despite the declaration
        # for v in variables:
        # 	self.current_constraint.variables[v].domain.parameter = False
        self.func_pars -= set(variables)

        # active constraints
        constraints = []
        objective = None
        for c in args[1:]:
            if isinstance(c, dast.NameExpr):  # the name of constraint
                constraints.append(c.name)
            elif isinstance(c, dast.CallExpr):
                # ['func', 'args', 'keywords', 'starargs', 'kwargs']
                funcName = c.func.name
                if funcName == 'to_min' or funcName == 'to_max':  # the optimization goal
                    if funcName == 'to_min':
                        op = 'min'
                    else:
                        op = 'max'
                    if len(c.args) != 1:
                        self.error("line %s: wrong number of argument. expect 1." % node.lineno)
                        return None
                    objexpr = c.args[0]
                    if isinstance(objexpr, dast.NameExpr):
                        obj = objexpr.name
                    else:
                        obj = objexpr
                    objective = cast.Objective(op, obj)
                else:
                    constraints.append(c)  # global constraint or other self defined constraint
            elif isinstance(c, dast.BooleanExpr):  # boolean constraint
                constraints.append(c)
            else:
                self.error("line %s: invalid constraint" % node.lineno)
                return None

        cset = {c for c in constraints if isinstance(c, str)}
        delset = []
        for c in self.current_constraint.constraints:
            if c not in cset:
                delset.append(c)
        for c in delset:
            del self.current_constraint.constraints[c]

        self.current_constraint.objective = cast.Target(variables, constraints, objective, allFlag)


# DomainBasic: int, float, str, bool
# type:   string
# lowerbound: simple expr
# upperbound: simple expr
# step: simple expr
# DomainTuple:
# elements: a list of domains
# DomainMap or DomainDict:
# key: domain
# val: domain
# DomainSet:
# sub_domain: domain
# DomainMultiSet
# sub_domain: domain
class DomainParser(NodeVisitor, CompilerMessagePrinter):
    def __init__(self, filename="", _parent=None):
        CompilerMessagePrinter.__init__(self, filename, _parent=_parent)
        NodeVisitor.__init__(self)

    def visit_NameExpr(self, node):
        if node.name in {'int', 'float', 'str', 'bool'}:
            return cast.DomainBasic(node.name)
        else:
            return cast.DomainVar(node)

    # def visit_CallExpr(self, node):
    # 	# ints(lb,ub,step), floats(lb,ub)
    # 	lb = node.args[0]
    # 	ub = node.args[1]
    # 	if len(node.args) == 3:
    # 		step = node.args[2]
    # 	else:
    # 		step = None

    # 	if node.func.name == 'ints':
    # 		return cast.DomainBasic('int', lb, ub, step)
    # 	elif node.func.name == 'floats':
    # 		if step:
    # 			self.error("", node)
    # 		return cast.DomainBasic('float', lb, ub)
    # 	else:
    # 		self.error("", node)

    def visit_ExtSliceExpr(self, node):
        # only appears in declare of dict
        res = dict()
        for d in node.dims:
            try:
                assert isinstance(d, dast.SliceExpr)
                assert d.step is None
                key = d.lower.name
                val = self.visit(d.upper)
                res[key] = val
            except AssertionError as e:
                self.error("Malformed domain declaration", node)
        return res

    def visit_SubscriptExpr(self, node):
        """
        set[domain]
        dict[key:domain,val:domain]
        dict[domain, domain]
        int[lb:ub:step]
        float[lb:ub]
        """
        t = node.value.name
        if t == 'int' or t == 'float':
            try:
                assert isinstance(node.index, dast.SliceExpr)
                return cast.DomainBasic(t, node.index.lower, node.index.upper, node.index.step)
            except ValueError as e:
                self.error(e, node)
            except AssertionError as e:
                self.error("Malformed domain declaration: int", node)
        elif t == 'set':
            domain = self.visit(node.index)
            return cast.DomainSet(domain)
        elif t == 'dict':
            domain = self.visit(node.index)
            if isinstance(domain, cast.DomainTuple):
                if len(domain.elements) != 2:
                    self.error("Malformed domain declaration: dict domain has exactly 2 components", node)
                return cast.DomainMap(domain.elements[0], domain.elements[1])
            elif isinstance(domain, dict):
                try:
                    return cast.DomainMap(domain['key'], domain['val'])
                except:
                    self.error("Malformed domain declaration: dict domain contains only 'key' and 'val' components", node)
            else:
                self.error("Malformed domain declaration: dict", node)

    def visit_TupleExpr(self, node):
        # (domain, ...)
        elements = [self.visit(e) for e in node.subexprs]
        return cast.DomainTuple(elements)
