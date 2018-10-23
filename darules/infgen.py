import ruleast as ast
import subprocess
import inspect
from pprint import pprint

UniqueUpperCasePrefix = 'V'
#DefaultFileName = 'tmp' #can use one fixed name if all done dynamically
INDENT = ' ' * 4

class InfGenerator: pass

class XSBGenerator (InfGenerator):

    def __init__(self): pass
    
    def test(self):
        print(self.__class__.__name__)
        print(vars()) 
        print(globals()) 

    #print(vars())
    #print(globals())
    #if 'self' in vars() or 'self' in globals():
    #    print('self:', self)

def to_xsb(node):
        """
        called on a Rules node, write rules into XSB rules
        """
        if isinstance(node, ast.Rules):
            return '\n'.join(to_xsb(rule) for rule in node.rules)
        if isinstance(node, ast.Rule):
            if node.conds == None: return to_xsb(node.concl) + '.'
            return to_xsb(node.concl) + ' :- ' + \
                ','.join(to_xsb(assrtn) for assrtn in node.conds) + '.'
        if isinstance(node, ast.Assertion):
            return to_xsb(node.pred) + '(' + \
                ','.join(to_xsb(arg) for arg in node.args) + ')'
        if isinstance(node, ast.LogicVar):
            return UniqueUpperCasePrefix + node.name
        if isinstance(node, ast.Constant):
            return node.name

def write_file(filename, string):
    file = open(filename,'w')
    file.write(string)
    file.close()

def get_classname(node): 
        """
        return name of the enclosing class, if any, of the Rules node, and
        return name of enclosing module if there is no enclosing class;
        in general, need something unique for the entire program.
        """
        return 'tmp'

def get_modulename(node):
#       return __name__
        frm = inspect.stack()[1]  # caller's stack frame
        mod = inspect.getmodule(frm[0])
        print(mod.__name__ == __name__)
        return mod.__name__

def compile_rules(node):
        """
        called on a Rules node, write the rules in a file
        """
        # for now assume there is only one set of rules in each class,
        # and use the class name as file name;
        # later add the name of the Rules node within the class.
        # so rule files can be written at compile time.
        filename = get_classname(node)  # need to connect with da
        xsb_rules = ':- auto_table.\n'
        xsb_rules += to_xsb(node) 
        write_file(filename+'.rules', xsb_rules)

FACTS_TEMPLATE = """
for v in {VAL}:
    xsb_facts += "{PRED_NAME}" + str(v) + ".\\n"
"""

QUERY_TEMPLATE = """
xsb_query = "extfilequery:external_file_query(" + filename + "," + "{QUERY_STR}" + ")."
subprocess.run(["xsb", '-e', "add_lib_dir(a('../xsb')).", "-e", xsb_query])
answers = open(filename+".answers","r").read()
tuples = [tuple(eval(a)) for a in answers.split("\\n")[:-1]]
"""

#could move all three into compile_infer
indent_level = 2
gen = ''
def code(str): 
    global gen
    gen += INDENT * indent_level + str + '\n'

def compile_infer(node):
        """
        called on an InferStmt node, generate stmts to replace the infer stmt
        to execute the inference using XSB
        """
        global indent_level
        #code('filename = self.__class__.__name__')  # need to connect with da
        code('xsb_facts = ""')
        for (pred,val) in node.bindings:
            # code('for v in '+ val + ':')
            # indent_level += 1
            # code('xsb_facts += "'+ pred +'" + str(v) + ".\\n"')
            # indent_level -= 1
            code(FACTS_TEMPLATE.format(PRED_NAME=pred, VAL=val))
        code('write_file(filename+".facts", xsb_facts)')
        code('')
        for query in node.queries:
            # code('xsb_query = "extfilequery:external_file_query(" + filename + "," + "'+ query + '" + ")."')
            # # code('subprocess.run(["xsb", "-e", xsb_query])')
            # code('')
            # code('answers = open(filename+".answers","r").read()')
            # code('tuples = [tuple(eval(a)) for a in answers.split("\\n")[:-1]]')
            #code('setattr(self, query, tuples)')  # need to connect with da
            #or setlocalvar()?
            code(QUERY_TEMPLATE.format(QUERY_STR=query))
        return(gen)

#mixture of static and dynamic separated as above
#def compile_infer_stmt_to_execute_query(node):  
def execute_infer(node):
        filename = self.__class__.__name__  # assume rules are in a class
        xsb_facts = ''
        for (pred,val) in node.bindings:  # this line is static
            print(pred,val)
            for v in val: 
                xsb_facts += pred + str(v) + '.\n' 
            #xsb_facts += '\n'.join(pred + str(v) + '.' for v in val)
        write_file(filename+'.facts', xsb_facts)

# assume query is an entire relation for now, i.e., is a name of relation/set
        for query in node.queries:  # this line is static
#           xsb_query = '"external_file_query('+ filename +','+ query +')."'
            xsb_query = "extfilequery:external_file_query(tmp,path(1,X))."
            subprocess.run(['xsb', '-e', xsb_query], stdout=subprocess.PIPE)

            answers = open(filename+'.answers','r').read()
            tuples = [tuple(eval(a)) for a in answers.split('\n')]
            setattr(self, query, tuples)
            #setlocalvar()?


#g = XSBGenerator()
#g.test()
#print(get_modulename(g))

c = ast.Constant('path')
#print(to_xsb(c))

x = ast.LogicVar('X')
#print(to_xsb(x))

r1 = ast.Rule(ast.Assertion(ast.Constant('path'),
                             [ast.LogicVar('X'), ast.LogicVar('Y')]), 
              [ast.Assertion(ast.Constant('edge'),
                              [ast.LogicVar('X'),ast.LogicVar('Y')])])
#print(to_xsb(r1))

r2 = ast.Rule(ast.Assertion(ast.Constant('path'),
                             [ast.LogicVar('X'), ast.LogicVar('Y')]), 
              [ast.Assertion(ast.Constant('edge'),
                              [ast.LogicVar('X'),ast.LogicVar('Z')]),
               ast.Assertion(ast.Constant('path'),
                              [ast.LogicVar('Z'),ast.LogicVar('Y')])])
#print(to_xsb(r2))

r3 = ast.Rule(ast.Assertion(ast.Constant('path'),
                             [ast.LogicVar('X'), ast.LogicVar('Y')]), 
              [ast.Assertion(ast.Constant('path'),
                              [ast.LogicVar('Z'),ast.LogicVar('Y')]),
               ast.Assertion(ast.Constant('edge'),
                              [ast.LogicVar('X'),ast.LogicVar('Z')])])
#print(to_xsb(r3))


r0 = ast.Rule(ast.Assertion(ast.Constant('edge'),
                             [ast.Constant('5'),ast.Constant('8')]))
#print(to_xsb(r0))
#xsb restriction: edge cannot be added with rules and added as facts,
#unless special directives are used.

rs = ast.Rules('',[r1,r3])
print('==== rules ===='); print(rs); print(to_xsb(rs))

i = ast.InferStmt([('edge','RH')],['path(2,_)'])


compile_rules(rs)
indent_level = 0
gen = compile_infer(i)
print('==== generated code ===='); print(gen)


print('==== running generated code ====')
filename = 'tmp'
#RH = {(1,8), (2,9), (1,2)}
#RH = {(1,8), (2,9), (1,2), (2,3), (4,5), (5,6)}
RH = {(x,y) for x in range(100) for y in range(100)}
# pprint(globals())
exec(gen, globals())
#print(answers)
print('==== inferred tuples ===='); print(tuples)


#1/31/18 xsb command line, from my 307 assignment
# xsb -e "[a6],load_dyn('a6input1facts'),a6run,halt." > a6output1.txt

#1/31/18 running command line in python
# subprocess.run(['ls', '-l'], stdout=subprocess.PIPE).stdout.decode('utf-8')
# result = subprocess.run(['ls', '-l'], stdout=subprocess.PIPE)
# print(result.stdout.decode('utf-8'))

#2/1/18 David: xsb implementation of call
#python(Fn, Query) :-
#  consult(FN.in), 
#  open(FN.out,write, ostr),
#  term_vars(Query,Vars)
#  (do_all
#     call(Query), writeq(ostr,Vars), NL(ostr))
#  close(ostr).

#2/2/18 David: xsb command line for call
# xsb --nobanner -e "extfilequery:external_file_query(path,path(a,X))."

#2/2/18 test running xsb command line in python
#xsb_query = "extfilequery:external_file_query(path,path(Y,X))."
#subprocess.run(['xsb', '-e', xsb_query], stdout=subprocess.PIPE)
