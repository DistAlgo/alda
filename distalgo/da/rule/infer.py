from .rule_io import write_file, read_answer, rule_path
import sys, os, subprocess
from pprint import pprint
from ast import literal_eval
from pathlib import PurePath

UniqueLowerCasePrefix = 'p'

def eval_logicVar(v):
    return eval(v) if v.isdigit() else \
              None if v == "'None'" else \
             False if v == "'False'" else \
              True if v == "'True'" else v

def LogicVarToXSB(v):
    return str(v) if v == '_' or isinstance(v, int) or (isinstance(v,str) and v.isdigit()) else \
         "'None'" if v is None or v == 'None' else \
        "'False'" if v is False or v == 'False' else \
         "'True'" if v is True or v == 'True'  else "'%s'" % v

def infer(self, bindings=[], queries=[], rule=None, _rules_object = None):
    if not _rules_object:
        _rules_object = self['_rules_object']

    if not rule:
        print('Rule Name Unknown')

    # print('============================ infering: %s ============================' % rule)
    allBindings = set(b for b,_ in bindings)

    if not rule in _rules_object:
        raise ValueError("infer: can't find rule: " + rule)

    remove = set()
    for u in _rules_object[rule]['Unbounded']:
        if u not in allBindings:
            if u in self:
                remove.add(u)
                _rules_object[rule]['RhsVars'].add(u)
            else:
                print("Unexpected error:", sys.exc_info()[0])
                raise ValueError("infer: not all predicates bond: " + u)

    _rules_object[rule]['Unbounded'] -= remove

    for r in _rules_object[rule]['RhsVars']:
        if r not in allBindings:
            bindings.append((r, self[r]))

    if len(queries) == 0:   # when no queries are passed in, return all the derived predicates
        for v in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
            qstr = v[0]+'(' + ','.join('_'*v[1]) + ')'
            queries.append([PurePath.joinpath(rule_path,v[0]).as_posix(),UniqueLowerCasePrefix+qstr])
    else:                   # processing queries arguments
        for (i, item) in enumerate(queries):
            # when queries are passed with only names, complete the query in form of pred(_,...,_) with information got while parsing
            if item.find('(') < 0:
                for v,a in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
                    if v == item:
                        qstr = v+'(' + ','.join('_'*a) + ')'
                        queries[i] = [PurePath.joinpath(rule_path,v).as_posix(), UniqueLowerCasePrefix+qstr]
                        break
            # when queries are passed in full, convert each logic variables to valid format as XSB
            else:
                pred = item.split('(')[0]
                var = item.split('(')[1].split(')')[0]
                queries[i] = [PurePath.joinpath(rule_path,pred).as_posix(), 
                              UniqueLowerCasePrefix+pred+'(%s)' % ','.join(LogicVarToXSB(vv.strip()) for vv in var.split(','))]

    xsb_facts = ""
    for b in bindings:
        # when b is an empty predicate, generate a place holder where all logic vars are -1
        if len(b[1]) == 0:
            xsb_facts += UniqueLowerCasePrefix+b[0]+'(%s).\n' % ','.join(['-1']*_rules_object[rule]['RhsAry'][b[0]])
        elif not isinstance(b[1], list) and not isinstance(b[1], set):    # when b is a single value
            if isinstance(b[1], tuple):
                xsb_facts += UniqueLowerCasePrefix+b[0]+'(%s)' % ','.join(LogicVarToXSB(vv) for vv in b[1])+'.\n'
            else:
                xsb_facts += UniqueLowerCasePrefix+b[0]+'('+LogicVarToXSB(b[1])+').\n'
        else:   # when b is a set/list
            for v in b[1]:
                if isinstance(v, tuple):
                    xsb_facts += UniqueLowerCasePrefix+b[0]+'(%s)' % ','.join(LogicVarToXSB(vv) for vv in v)+'.\n'
                else:
                    xsb_facts += UniqueLowerCasePrefix+b[0]+'('+LogicVarToXSB(v)+').\n'

    utime1, stime1, cutime1, cstime1, elapsed_time1 = os.times()
    write_file(rule+'.facts', xsb_facts)
    utime2, stime2, cutime2, cstime2, elapsed_time2 = os.times()    # timing: i/o: write input
    
    rule_path_rule = PurePath.joinpath(rule_path,rule)
    xsb_path = PurePath.joinpath(rule_path.parent,'xsb')
    if os.name == 'nt':
        rule_path_rule = str(rule_path_rule).replace('\\','\\\\')
        xsb_path = str(xsb_path).replace('\\','\\\\')
    xsb_query = "extfilequery:external_file_query('{}',{}).".format(rule_path_rule, 
                                                                    "[%s]" % ",".join("['%s',%s]" % (q[0],str(q[1])) for q in queries))
    output = subprocess.run(["xsb",'--nobanner', '--quietload', '--noprompt', '-e', "add_lib_dir(a('{}')).".format(xsb_path), "-e", xsb_query],
                            stdout=subprocess.PIPE,text=True)
    # output = subprocess.run(["xsb", '-e', "add_lib_dir(a('{}')).".format(xsb_path), "-e", xsb_query])#,
                            # stdout=subprocess.PIPE,text=True)
    utime3, stime3, cutime3, cstime3, elapsed_time3 = os.times()    # timing: xsb
    
    results = []
    for r,_ in queries:
        rname = PurePath(r).name
        answers = read_answer(rname)
        tuples = {tuple(eval_logicVar(v) for v in a.split(',')) if len(a.split(',')) > 1 
                                                                   else eval_logicVar(a)
                 for a in answers.split("\n")[:-1]}
        results.append(tuples)
    utime4, stime4, cutime4, cstime4, elapsed_time4 = os.times()     # timing: i/o: load output
    
    ## xsb query and i/o time
    # lines = output.stdout.split('\n')
    # lines = [l for l in lines if (l and l != 'yes' and l != 'no')]
    # print('datasize\t%s\t%s' % (len(xsb_facts.split('\n')), 
    #                             os.path.getsize(PurePath.joinpath(rule_path,rule+'.facts'))))
    # print('\telapse\tcpu')
    # print('write_input\t%s\t%s'%(elapsed_time2-elapsed_time1, utime2-utime1 + stime2-stime1 + cutime2-cutime1 + cstime2-cstime1))
    # print('subprocess_xsb\t%s\t%s'%(elapsed_time3-elapsed_time2, utime3-utime2 + stime3-stime2 + cutime3-cutime2 + cstime3-cstime2))
    # print('read_output\t%s\t%s'%(elapsed_time4-elapsed_time3, utime4-utime3 + stime4-stime3 + cutime4-cutime3 + cstime4-cstime3))
    # print('xsb_load\t%s\t%s'%(lines[-4],lines[-3]))
    # print('xsb_query\t%s\t%s'%(lines[-2],lines[-1]))

    if len(results) == 0:
        return results
    if len(results) == 1:
        return results[0]
    return tuple(results)




