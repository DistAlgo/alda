from da.compiler.pygen import *
import da.compiler.pygen as pygen

from . import ruleast
from .rule_io import write_file

from pprint import pprint

RULES_OBJECT_NAME = "_rules_object"
UniqueUpperCasePrefix = 'V'
UniqueLowerCasePrefix = 'p'


class PythonGenerator(pygen.PythonGenerator):

    def __init__(self, filename="", options=None):
        super().__init__(filename, options)
        self.current_triggered_rules = set()
        self.current_setup = False

    def compile_rules(self, node):
        """
        called on a Rules node, write the rules in a file
        """
        # for now assume there is only one set of rules in each class,
        # and use the class name as file name;
        # later add the name of the Rules node within the class.
        # so rule files can be written at compile time.
        # filename = get_classname(node.decls)  # need to connect with da
        # print('=========== compile_rules ============')
        xsb_rules = ':- auto_table.\n'
        xsb_rules += self.to_xsb(node) 
        # print(xsb_rules)
        write_file(node.decls+'.rules', xsb_rules)


    def to_xsb(self, node):
        """
        called on a Rules node, write rules into XSB rules
        """
        if isinstance(node, ruleast.Rules):
            return '\n'.join(self.to_xsb(rule) for rule in node.rules)
        if isinstance(node, ruleast.Rule):
            if node.conds == None: return self.to_xsb(node.concl) + '.'
            return self.to_xsb(node.concl) + ' :- ' + \
                ','.join(self.to_xsb(assrtn) for assrtn in node.conds) + '.'
        if isinstance(node, ruleast.Assertion):
            return self.to_xsb(node.pred) + '(' + \
                ','.join(self.to_xsb(arg) for arg in node.args) + ')'
        if isinstance(node, ruleast.LogicVar):
            if node.name == '_':
                return node.name
            elif not isinstance(node.name,str) or node.name.startswith("'"):
                # print(node.name)
                return str(node.name)
            else:
                return UniqueUpperCasePrefix + node.name
            
        if isinstance(node, ruleast.Constant):
            return UniqueLowerCasePrefix + node.name


    def visit(self, node):
        if isinstance(node, ruleast.Rules):
            self.compile_rules(node)
            return
        else:
            return super().visit(node)

    # TODO: couldn't find a way to insert into original code without copy the whole code here
    def visit_Program(self,node):
        self.module_args = node._compiler_options
        mainbody = self.body(node.body)
        if node.nodecls is not None:
            # `nodecls` is the `Node_` process:
            nodeproc = self.visit(node.nodecls)
        body = list(self.preambles)
        body.append(self.generate_config(node))
        if hasattr(node,'rules'):
            imptinfer = ImportFrom('da.rule',[alias('infer', None)],0)
            body.append(imptinfer)
            body.extend(self.body(node.rules))
            ruleobj = self._generate_rules(node,True)
            body.extend(ruleobj)

        for stmt in body:
            stmt.lineno = 1
        body.extend(mainbody)
        if node.nodecls is not None:
            body.extend(nodeproc)
       
        body.extend(self.postambles)

        importList = [Import([alias(t[0], t[1] if len(t)>1 else None)]) for t in self.importSet]
        fromImportList = [ImportFrom(t[0], [alias(t[1], t[2] if len(t)>2 else None)], 0) for t in self.fromImportSet]

        return [Module(importList+fromImportList+body)]

    # generate rule object containing information of rules defined in current scope
    # self._rules_object
    def _generate_rules(self,node,globalRule=False):
        if globalRule:
            target = pyName(RULES_OBJECT_NAME, Store())
        else:
            target = pyAttr('self',RULES_OBJECT_NAME, Store())

        a = pyAssign(  [target], 
                        Dict([Str(key) for key, _ in node.RuleConfig.items()],
                             [Dict( [Str('LhsVars'),Str('RhsVars'),Str('Unbounded'),Str('UnboundedLeft')],
                                    [Set([pyTuple([Str(v.name), Num(val['LhsAry'][v])]) for v in val['LhsVars']]),
                                     Set([Str(v.name) for v in val['RhsVars']]),
                                     Set([Str(v) for v in val['Unbounded']]),
                                     Set([pyTuple([Str(v), Num(val['UnboundedleftAry'][v])]) for v in val['Unboundedleft']])
                                     ])
                              for _, val in node.RuleConfig.items()]))
        fire_rules = []
        for key, val in node.RuleConfig.items():
            if len(val['Unbounded']) == 0 and len(val['LhsVars']) > 0:
                fire_rules.append(key)

        if not globalRule:
            inferStmt = self._generate_infer(node, fire_rules)
            return [a]+inferStmt
        else:
            return [a]
        

    def _generate_infer(self, node, fire_rules):
        callInfer = []
        parent_process = node
        while not (isinstance(parent_process, dast.Process) or isinstance(parent_process, dast.Program)):
            if not hasattr(parent_process, 'process'):
                parent_process = parent_process.parent
            else:
                parent_process = parent_process.process
        if isinstance(parent_process, dast.Program):
            target = 'infer'
            inferarg = [pyCall(pyName('globals'))]
        else:
            target = pyAttr("self", 'infer')
            inferarg = []
        if hasattr(parent_process,'RuleConfig'):
            ruleConfig = parent_process.RuleConfig
            if len(fire_rules) > 0:
                for r in fire_rules:
                    query = ruleConfig[r]['LhsVars']
                    for q in query:
                        if target == 'infer':
                            lhs_target = pyName(q.name, Store())
                        else:
                            lhs_target = pyAttr(pyAttr("self", STATE_ATTR_NAME),q.name,Store())
                        arity = ruleConfig[r]['LhsAry'][q]
                        qstr = q.name+'(' + ','.join('_'*arity) + ')'
                        inferStmt = pyAssign([lhs_target],pyCall(target, args=inferarg, keywords=[('rule',Str(r)),('queries',pyList([Str(qstr)]))]))
                        copy_location(inferStmt, node)
                        callInfer.append(inferStmt)

        return callInfer


    def visit_Process(self, node):
        printd("Compiling process %s" % node.name)
        printd("has methods:%r" % node.methods)
        cd = ClassDef()
        cd.name = node.name
        cd.bases = [self.visit(e) for e in node.bases]

        if node is node.immediate_container_of_type(dast.Program).nodecls:
            cd.bases.append(pyAttr("da", "NodeProcess"))
        else:
            cd.bases.append(pyAttr("da", "DistProcess"))
        if node.ast is not None and hasattr(node.ast, 'keywords'):
            # ########################################
            # TODO: just pass these through until we figure out a use for them:
            cd.keywords = node.ast.keywords
            # ########################################
        else:
            cd.keywords = []
            cd.starargs = []
            cd.kwargs = []
        cd.body = [self.generate_init(node)]
        if node.configurations:
            cd.body.append(self.generate_config(node))
        
        if node.setup is not None:
            cd.body.extend(self.visit(node.setup))
        elif hasattr(node, 'RuleConfig') and len(node.RuleConfig) > 0:
            fd = self._create_setup(node)
            cd.body.append(fd)

        self.current_setup = True
        if node.entry_point is not None:
            cd.body.extend(self._entry_point(node.entry_point))

        cd.decorator_list = [self.visit(d) for d in node.decorators]
        cd.body.extend(self.body(node.staticmethods))
        cd.body.extend(self.body(node.methods))
        if hasattr(node,'rules'):
            cd.body.extend(self.body(node.rules))

        if hasattr(node, 'RuleConfig') and len(node.RuleConfig) > 0:
            cd.body.extend(self._generate_override_functions(node))


        cd.body.extend(self.generate_handlers(node))
        self.current_setup = False
        return [cd]

    def _create_setup(self,node):
        parent = node
        while not parent.setup:
            for i in parent.parent.processes:
                if i.name == parent.bases[0].subexprs[0].name:
                    parent = i
                    break
        fd = FunctionDef()
        fd.name = 'setup'
        fd.args = self.visit(parent.args)
        fd.body = []
        superargs = [pyName(argname.arg) for argname in fd.args.args]
        setupExp = pyExpr(pyCall(pyAttr(pyCall('super'),"setup"),args=superargs))
        ruleStmt = self._generate_rules(node)
        fd.body += [setupExp]+ruleStmt
        fd.decorator_list = []
        fd.returns = None
        fd.args.args.insert(0, arg("self", None))
        return fd

    # for a class a inherit b, if variables are changed in functions of b, but rules related to a, 
    # generate a override function in a that first call super.func_in_b(), then call infer
    def _generate_override_functions(self,node):
        addFunctions = dict()
        for rule in node.RuleConfig:
            if len(node.RuleConfig[rule]['Unbounded']) == 0 and len(node.RuleConfig[rule]['LhsVars']) > 0:
                # updates of right hand side variables will trigger automatic infer
                for rhs in node.RuleConfig[rule]['RhsVars']:
                    for ctx, stmt in rhs._indexes:
                        # updates happen at Assignment context and Update context
                        if ctx == dast.AssignmentCtx or ctx == dast.UpdateCtx:
                            # find the statement of assignment or update
                            for s in stmt:
                                if s:
                                    # find the function containing this statement
                                    parent = s.parent
                                    while not isinstance(parent,dast.Function):
                                        parent = parent.parent
                                    # collect all the local defined methods
                                    # if the parent function is not override by local function, 
                                    # collects needed information for adding infer
                                    localMethod = set(m.name for m in node.methods)
                                    if parent.name != 'setup' and not parent.name in localMethod:
                                        if parent.name not in addFunctions:
                                            addFunctions[parent.name] = dict()
                                            addFunctions[parent.name]['origFunc'] = parent._ast
                                            addFunctions[parent.name]['args'] = self.visit(parent.args)
                                            addFunctions[parent.name]['rules'] = set()
                                        addFunctions[parent.name]['rules'].add(rule)
        # pprint(node)
        # pprint(addFunctions)
        funcs = []
        for func, info in addFunctions.items():
            fd = FunctionDef()      # create a new function inherits the parent's function
            fd.name = func
            fd.args = info['args']  # function args the same as parents args
            fd.body = []
            funcargs = [pyName(argname.arg) for argname in fd.args.args]
            # 1. call super.parent_function with orig arguments
            # ???? TODO, may contain bugs. not only args, but keywords and keyargs
            fd.body.append(pyExpr(pyCall(pyAttr(pyCall('super'),fd.name),args=funcargs)))
            # 2. call infer
            fd.body.extend(self._generate_infer(node, info['rules']))
            fd.decorator_list = []
            # set the return value the same as supers return value
            # ???? TODO, may contain bugs. may need to add an assignment statement to orig function
            fd.returns = info['origFunc'].returns
            fd.args.args.insert(0, arg("self", None))
            funcs.append(fd)

        return funcs


    # add inference of rules at the end of setup function
    def visit_Function(self, node):
        fd = super().visit_Function(node)[0]
        ruleStmt = []
        if isinstance(node.parent, dast.Process) and node.name == "setup" and hasattr(node.parent,'RuleConfig') and len(node.parent.RuleConfig) > 0:
            ruleStmt = self._generate_rules(node.parent)
        fd.body += ruleStmt
        return [fd]

    def visit_BuiltinCallExpr(self, node):
        if node.func == 'infer':
            parent = node
            while not(isinstance(parent,dast.Process) or isinstance(parent,dast.Program)):
                parent = parent.parent
            if isinstance(parent,dast.Program): 
                return pyCall(node.func,
                         [pyCall(pyName('globals'))]+[self.visit(a) for a in node.args],
                         [(key, self.visit(value)) for key, value in node.keywords],
                         self.visit(node.starargs)
                         if node.starargs is not None else None,
                         self.visit(node.kwargs)
                         if node.kwargs is not None else None)
        return super().visit_BuiltinCallExpr(node)

    def visit_NamedVar(self, node):
        if self.current_context in {Store, Del}:
            if len(node.triggerInfer) > 0:
                self.current_triggered_rules |= node.triggerInfer
        else:
            self.current_triggered_rules = set()
        return super().visit_NamedVar(node)

    def visit_AssignmentStmt(self, node):
        if node.value is None:
            # This is a "pure" annotation (since Python 3.6), don't generate
            # anything:
            return []
        self.current_context = Store
        targets = [self.visit(tgt) for tgt in node.targets]
        fire_rules = self.current_triggered_rules
        self.current_context = Load
        val = self.visit(node.value)
        assignStmt = pyAssign(targets, val)

        if self.current_setup:
            callInfer = self._generate_infer(node,fire_rules)
        else:
            callInfer = []

        return [assignStmt]+callInfer


    def visit_OpAssignmentStmt(self, node):
        self.current_context = Store
        target = self.visit(node.target)
        fire_rules = self.current_triggered_rules
        self.current_context = Load
        val = self.visit(node.value)
        if self.current_setup:
            callInfer = self._generate_infer(node,fire_rules)
        else:
            callInfer = []
        return [pyAugAssign(target, OperatorMap[node.operator], val)] + callInfer


    def visit_DeleteStmt(self, node):
        self.current_context = Del
        targets = [self.visit(tgt) for tgt in node.targets]
        fire_rules = self.current_triggered_rules
        self.current_context = Load

        if self.current_setup:
            callInfer = self._generate_infer(node,fire_rules)
        else:
            callInfer = []

        return [propagate_fields(Delete(targets))] + callInfer


    def visit_SimpleStmt(self, node):
        simpleresult = super().visit_SimpleStmt(node)[0]
        value = simpleresult.value
        inferStmt = []
        if isinstance(value, Call) and isinstance(value.func, Attribute) and isinstance(value.func.value, Name):
            changed = value.func.value.id
            op = value.func.attr
            if op in KnownUpdateMethods:
                parent = node.parent
                while not (isinstance(parent, dast.Process) or isinstance(parent, dast.Program)):
                    parent = parent.parent
                if len(parent.RuleConfig) > 0:
                    fire_rules = set()
                    for r in parent.RuleConfig:
                        rhs = set(v.name for v in parent.RuleConfig[r]['RhsVars'])
                        if changed in rhs:
                            fire_rules.add(r)
                            # break
                    inferStmt = self._generate_infer(parent,fire_rules)
        return [simpleresult]+inferStmt

