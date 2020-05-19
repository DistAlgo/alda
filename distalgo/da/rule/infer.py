from .rule_io import write_file, read_answer, rule_path
import sys, os, subprocess
from pprint import pprint
from ast import literal_eval
from pathlib import PurePath

UniqueLowerCasePrefix = 'p'

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

    if len(queries) == 0:
        for v in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
            qstr = v[0]+'(' + ','.join('_'*v[1]) + ')'
            queries.append([PurePath.joinpath(rule_path,v[0]).as_posix(),UniqueLowerCasePrefix+qstr])
            # queries.append([PurePath.joinpath(rule_path,v[0]).as_posix(), "'%s'" % (UniqueLowerCasePrefix+qstr)])
    else:
        for (i, item) in enumerate(queries):
            if item.find('(') < 0:
                for v,a in _rules_object[rule]['UnboundedLeft']|_rules_object[rule]['LhsVars']:
                    if v == item:
                        qstr = v+'(' + ','.join('_'*a) + ')'
                        queries[i] = [PurePath.joinpath(rule_path,v).as_posix(), UniqueLowerCasePrefix+qstr]

    xsb_facts = ""
    for b in bindings:
        if len(b[1]) == 0:
            xsb_facts += UniqueLowerCasePrefix+b[0]+'(%s).\n' % ','.join(['-1']*_rules_object[rule]['RhsAry'][b[0]])
            continue
        if not isinstance(b[1], list) and not isinstance(b[1], set):
            if isinstance(b[1], tuple):
                xsb_facts += UniqueLowerCasePrefix+b[0]+str(b[1])+'.\n'
            else:
                xsb_facts += UniqueLowerCasePrefix+b[0]+'('+str(b[1])+').\n'
        else:
            for v in b[1]:
                if isinstance(v, tuple):
                    xsb_facts += UniqueLowerCasePrefix+b[0]+'(%s)' % ','.join(str(vv) for vv in v)+'.\n'
                else:
                    xsb_facts += UniqueLowerCasePrefix+b[0]+'('+str(v)+').\n'

    utime1, stime1, cutime1, cstime1, elapsed_time1 = os.times()
    write_file(rule+'.facts', xsb_facts)
    # timing: i/o: write input
    utime2, stime2, cutime2, cstime2, elapsed_time2 = os.times()
    
    # although written the replace(\ with \\), but there is no \ in unix/linux path, so seems compatible to all systems. 
    # but better do something according to the system
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
    # timing: xsb
    utime3, stime3, cutime3, cstime3, elapsed_time3 = os.times()
    
    results = []
    for r,_ in queries:
        rname = PurePath(r).name
        answers = read_answer(rname)
        tuples = [tuple(eval(v) if v.isdigit() 
                                else None if v == "'None'"
                                else False if v == "'False'"
                                else True if v == "'True'"
                                else v 
                    for v in a.split(',')) if len(a.split(',')) > 1 
                            else eval(a) if a.isdigit() 
                            else None if a == "'None'"
                            else False if a == "'False'"
                            else True if a == "'True'"
                            else a
                 for a in answers.split("\n")[:-1]]
        results.append(tuples)
    # timing: i/o: load output
    utime4, stime4, cutime4, cstime4, elapsed_time4 = os.times()
    
    # xsb query and i/o time
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




