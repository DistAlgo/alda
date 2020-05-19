from da.compiler.parser import *
import da.compiler.parser as parser
from ast import *
from . import ruleast
from da.compiler.utils import printe

KW_RULES = "rules"
KW_COND = "if_"
KW_INFER = "infer"

class Parser(parser.Parser):

    def __init__(self, filename="", options=None, execution_context=None,
                 _package=None, _parent=None):
        super().__init__(filename, options, execution_context, _package, _parent)
        self.current_rule = None

    # Rules:
    def create_assersion(self,node,lhs = False):
        args = []
        n = self.current_scope.find_name(node.func.id)
        # pprint(n)
        if n is not None:
            if lhs:
                self.current_rule['LhsVars'].add(n)
                self.current_rule['LhsAry'][n] = len(node.args)
            else:
                self.current_rule['RhsVars'].add(n)
                self.current_rule['RhsAry'][n] = len(node.args)
        else:
            if lhs:
                 self.current_rule['Unboundedleft'].add(node.func.id)
                 self.current_rule['UnboundedleftAry'][node.func.id] = len(node.args)
            else:
                 self.current_rule['Unboundedright'].add(node.func.id)


        for a in node.args:
            if isinstance(a,Call):
                assers = self.create_assersion(a,lhs)
                args.append(assers)
            elif isinstance(a, Name):
                args.append(ruleast.LogicVar(a.id))
            elif isinstance(a, Num):
                # pprint(vars(a))
                args.append(ruleast.LogicVar(a.n))
            elif isinstance(a, Str):
                # pprint(vars(a))
                args.append(ruleast.LogicVar("'%s'" % a.s))
            elif isinstance(a, UnaryOp):
                if isinstance(a.op, USub):
                    v = -1 * a.operand.n
                elif isinstance(a.op, UAdd):
                    v = a.operand.n
                else:
                    print('create_assersion: isinstance(a, UnaryOp) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    pprint(a)
                    pprint(vars(a))
                    raise NotImplementedError
                args.append(ruleast.LogicVar(v))
            elif isinstance(a, NameConstant):   # None, True, False
                args.append(ruleast.LogicVar("'%s'" % str(a.value)))
            else:
                print('create_assersion: else !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                pprint(a)
                pprint(vars(a))
                raise NotImplementedError
        a = ruleast.Assertion(ruleast.Constant(node.func.id),args)

        return a


    def create_condition(self,node):
        if node.func.id == KW_COND:
            assersions = []
            for a in node.args:
                assers = self.create_assersion(a)
                assersions.append(assers)
            return assersions
        else:
            self.error('Invalid Rule')
        

    def visit_Rule(self,node):
        r = None
        if (isinstance(node, Tuple)):   # conclusion, condition
            concl = self.create_assersion(node.elts[0],True)
            conds = self.create_condition(node.elts[1])
            r = ruleast.Rule(concl,conds)

        elif (isinstance(node, Call)):  # only condition
            conds = self.create_condition(node)
            r = ruleast.Rule(None,conds)
        return r


    def create_rules(self, rulecls, ast, decls, nopush=False):
        self.current_rule = dict()
        self.current_rule['LhsVars'] = set()
        self.current_rule['LhsAry'] = dict()
        self.current_rule['RhsVars'] = set()
        self.current_rule['RhsAry'] = dict()
        self.current_rule['Unboundedleft'] = set()
        self.current_rule['UnboundedleftAry'] = dict()
        self.current_rule['Unboundedright'] = set()
        self.current_rule['Unbounded'] = set()
        rules = []
        for r in ast.body:
            rules.append(self.visit_Rule(r.value))

        self.current_rule['RhsVars'] -= self.current_rule['LhsVars']
        self.current_rule['Unbounded'] = self.current_rule['Unboundedright'] - self.current_rule['Unboundedleft']
        # print('============== create_rules ==============')
        if len(self.current_rule['Unbounded']) == 0:
            for rv in self.current_rule['RhsVars']:
                rv.triggerInfer.add(decls)
                # print('============== added to triggerInfer ==============')
                # print(rv)

        rulesobj = rulecls(decls, rules)
        rulesobj.label = self.current_label
        self.current_label = None

        return rulesobj


    def visit_FunctionDef(self, node):
        if (node.name == KW_RULES):
            numArgs = len(node.args.args)
            decl = ''
            if numArgs > 0:
                for i in range(numArgs):
                    if node.args.args[i].arg == 'name':
                        decl = node.args.defaults[i].s
                        break
            if not decl:
                try:
                    decl = str(self.state_stack[-1][0].name)
                except:
                    self.error("Empty rule name not allowed.")

            s = self.create_rules(ruleast.Rules, node, decl)

            if not hasattr(self.current_parent,'RuleConfig'):
                self.current_parent.RuleConfig = dict()
            self.current_parent.RuleConfig[decl] = self.current_rule

            if hasattr(self.current_parent,'rules'):
                self.current_parent.rules.append(s)
            else:
                self.current_parent.rules = [s]

            self._dummy_process = None

        else:
            return super().visit_FunctionDef(node)

