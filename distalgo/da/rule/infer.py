from .rule_io import write_file, read_answer, rule_path
import sys, os, subprocess
from pprint import pprint
from ast import literal_eval

UniqueLowerCasePrefix = 'p'

def infer(self, bindings=[], queries=[], rule=None, _rules_object = None):
    if not _rules_object:
        _rules_object = self['_rules_object']

    if not rule:
        print('Rule Name Unknown')

    print('=================================== infering ===================================')
    # print(self)
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

    if len(queries) == 0:
        for v in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
            qstr = v[0]+'(' + ','.join('_'*v[1]) + ')'
            queries.append(([os.path.join(rule_path,v[0]),"'"+UniqueLowerCasePrefix+qstr+"'"]))
    else:
        for (i, item) in enumerate(queries):
            if item.find('(') < 0:
                for v,a in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
                    if v == item:
                        qstr = v+'(' + ','.join('_'*a) + ')'
                        queries[i] = [os.path.join(rule_path,v), "'"+UniqueLowerCasePrefix+qstr+"'"]

    xsb_facts = ""
    for b in bindings:
        if not isinstance(b[1], list) and not isinstance(b[1], set):
            if isinstance(b[1], tuple):
                xsb_facts += UniqueLowerCasePrefix+b[0]+str(b[1])+'.\n'
            else:
                xsb_facts += UniqueLowerCasePrefix+b[0]+'('+str(b[1])+').\n'
        else:
            for v in b[1]:
                if isinstance(v, tuple):
                    xsb_facts += UniqueLowerCasePrefix+b[0]+str(v)+'.\n'
                else:
                    xsb_facts += UniqueLowerCasePrefix+b[0]+'('+str(v)+').\n'

    write_file(rule+'.facts', xsb_facts)

    results = []
    # utime1, stime1, cutime1, cstime1, elapsed_time1 = os.times()
    xsb_query = "extfilequery:external_file_query('{}',{}).".format(os.path.join(rule_path,rule),queries)
    xsb_path = os.path.join(rule_path,'..','xsb')
    print(rule_path)
    subprocess.run(["xsb", '-e', "add_lib_dir(a('{}')).".format(xsb_path), "-e", xsb_query])
    for r,_ in queries:
        rname = os.path.basename(r)
        answers = read_answer(rname)
        tuples = [tuple(literal_eval(v) for v in a.split(',')) if len(a.split(',')) > 1 else literal_eval(a) for a in answers.split("\n")[:-1]]
        results.append(tuples)
    # utime, stime, cutime, cstime, elapsed_time = os.times()
    # return elapsed_time-elapsed_time1, utime-utime1 + stime-stime1 + cutime-cutime1 + cstime-cstime1
    if len(results) == 0:
        return results
    if len(results) == 1:
        return results[0]
    return tuple(results)




