from .rule_io import write_file, read_answer, rule_path
import sys, os, subprocess
from pprint import pprint
from ast import literal_eval
from pathlib import PurePath

UniqueLowerCasePrefix = 'p'
xsb_path = PurePath.joinpath(PurePath(__file__).parent,'xsb')
if os.name == 'nt':
    xsb_path = str(xsb_path).replace('\\','\\\\')

def eval_logicVar(v):
    return eval(v) if v.isdigit() else \
              None if v == "'None'" else \
             False if v == "'False'" else \
              True if v == "'True'" else v

def flatten(x):
    if isinstance(x, list):
        return [a for i in x for a in flatten(i)]
    else:
        return [x]

def LogicVarToXSB(v):
    if isinstance(v, (list,tuple)):
        return ','.join(LogicVarToXSB(y) for x in v for y in flatten(x))
    return str(v) if v == '_' or isinstance(v, int) or (isinstance(v,str) and v.isdigit()) else \
         "'None'" if v is None or v == 'None' else \
        "'False'" if v is False or v == 'False' else \
         "'True'" if v is True or v == 'True'  else "'%s'" % v

def gen_fact(pred, val):
    if isinstance(val, (list,tuple,set)):
        return UniqueLowerCasePrefix+pred+'(%s)' % ','.join(LogicVarToXSB(v) for v in val)
    else:
        return UniqueLowerCasePrefix+pred+'(%s)' % LogicVarToXSB(val)

def _infer(rule, arity, bindings, queries):
    # generate facts
    xsb_facts = ""
    for key, val in bindings:
        # when b is an empty predicate, generate a place holder where all logic vars are -1
        if len(val) == 0:
            xsb_facts += gen_fact(key,['-1']*arity[key])+'.\n'
        elif not isinstance(val, list) and not isinstance(val, set):    # when b is a single value
            xsb_facts += gen_fact(key, val)+'.\n'
        else:   # when b is a set/list
            for v in val:
                xsb_facts += gen_fact(key, v)+'.\n'
    
    utime1, stime1, cutime1, cstime1, elapsed_time1 = os.times()
    write_file(rule+'.facts', xsb_facts)
    utime2, stime2, cutime2, cstime2, elapsed_time2 = os.times()    # timing: i/o: write input

    # generate queries, a list of tuple (out_file_name, query)
    _queries = []
    for q in queries:
        # when queries are passed with only names, complete the query in form of pred(_,...,_)
        if q.find('(') < 0:
            qstr = q +'(' + ','.join('_'*arity[q]) + ')'
            _queries.append([PurePath.joinpath(rule_path,rule+'.'+q).as_posix(), UniqueLowerCasePrefix+qstr])

        # when queries are passed in full, convert each logic variables to valid format as XSB
        else:
            pred = q.split('(')[0]
            var = q.split('(')[1].split(')')[0]
            _queries.append([PurePath.joinpath(rule_path,rule+'.'+pred).as_posix(), 
                             gen_fact(pred, var.strip().split(','))])
                          

    rule_path_rule = PurePath.joinpath(rule_path,rule)
    if os.name == 'nt':
        rule_path_rule = str(rule_path_rule).replace('\\','\\\\')

    xsb_query = "extfilequery:external_file_query('{}',{}).".format(rule_path_rule, 
                    "[%s]" % ",".join("['%s',%s]" % (qfile,qstr) for qfile, qstr in _queries))
    # print(xsb_query)
    output = subprocess.run(["xsb",'--nobanner', '--quietload', '--noprompt', 
                            '-e', "add_lib_dir(a('{}')).".format(xsb_path), "-e", xsb_query],
                            stdout=subprocess.PIPE,text=True)
    # output = subprocess.run(["xsb", '-e', "add_lib_dir(a('{}')).".format(xsb_path), "-e", xsb_query],
    #                         stdout=subprocess.PIPE,text=True)
    utime3, stime3, cutime3, cstime3, elapsed_time3 = os.times()    # timing: xsb
    results = []
    for r,_ in _queries:
        rname = PurePath(r).name
        answers = read_answer(rname)
        tuples = {tuple(eval_logicVar(v) for v in a.split(',')) if len(a.split(',')) > 1 
                                                                   else eval_logicVar(a)
                 for a in answers.split("\n")[:-1]}
        results.append(tuples)
    utime4, stime4, cutime4, cstime4, elapsed_time4 = os.times()     # timing: i/o: load output
    
    # xsb query and i/o time
    lines = output.stdout.split('\n')
    lines = [l for l in lines if (l and l != 'yes' and l != 'no')]
    print('\tnum_fact\tfile_size')
    print('datasize\t%s\t%s' % (len(xsb_facts.split('\n')), 
                                os.path.getsize(PurePath.joinpath(rule_path,rule+'.facts'))))
    print('timing\telapse\tcpu')
    print('write_input\t%s\t%s'%(elapsed_time2-elapsed_time1, utime2-utime1 + stime2-stime1 + cutime2-cutime1 + cstime2-cstime1))
    print('subprocess_xsb\t%s\t%s'%(elapsed_time3-elapsed_time2, utime3-utime2 + stime3-stime2 + cutime3-cutime2 + cstime3-cstime2))
    print('read_output\t%s\t%s'%(elapsed_time4-elapsed_time3, utime4-utime3 + stime4-stime3 + cutime4-cutime3 + cstime4-cstime3))
    print('xsb_load\t%s\t%s'%(lines[-4],lines[-3]))
    print('xsb_query\t%s\t%s'%(lines[-2],lines[-1]))

    if len(results) == 0:
        return results
    if len(results) == 1:
        return results[0]
    return tuple(results)




