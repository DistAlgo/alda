import uuid
from .rule_io import write_file, read_answer, rule_path
import sys
import os
import subprocess
from pprint import pprint
from ast import literal_eval
from pathlib import PurePath
import importlib.util
from pprint import pformat
from .. import common

UniqueLowerCasePrefix = 'p'
xsb_path = PurePath.joinpath(PurePath(__file__).parent, 'xsb')
if os.name == 'nt':
    xsb_path = str(xsb_path).replace('\\', '\\\\')


class InferXSB():
    def __init__(self, rules, arity, bindings, queries):
        self.rules = rules
        self.arity = arity
        self.bindings = bindings
        self.queries = queries
        self.encoded = True      # whether the input is encoded as internal representation
        for _, val in bindings:  # assume the bindings are either all encoded or not encoded at all
            if not self.facts_encoded(val):
                self.encoded = False
                break
        self.ValueDict = dict()
        self.ValueIdDict = dict()
        self.generator = self.gensym()

    def facts_encoded(self, val):
        """ whether facts are encoded as internal presentation
        """
        if isinstance(val, (list, tuple, set)):
            for v in val:
                if not self.facts_encoded(v):
                    return False
        else:
            if not (isinstance(val, int) or isinstance(val, str)):
                return False
        return True

    def gen_unique_id(self):
        return str(uuid.uuid4())[:8]

    def eval_logicVar(self, v):
        if not self.encoded and isinstance(v, int):
            v = self.ValueDict[v]
        return eval(v) if v.isdigit() else \
            None if v == "'None'" else \
            False if v == "'False'" else \
            True if v == "'True'" else v

    def flatten(self, x):
        if isinstance(x, list):
            return [a for i in x for a in self.flatten(i)]
        else:
            return [x]

    def gensym(self):
        i = 0
        while True:
            i += 1
            yield int(i)

    def getid(self, node):
        buf = pformat(node)
        buf = buf.replace('\n', ' ')
        print('>>> encoding ', buf[:50], end='\r')  # TODO comment out to improve performance
        if node not in self.ValueIdDict:
            genid = next(self.generator)
            self.ValueIdDict[node] = genid
            self.ValueDict[genid] = node
            return genid
        else:
            return self.ValueIdDict[node]

    def LogicVarToXSB(self, v):
        if self.encoded:
            if isinstance(v, (list, tuple)):
                return ','.join(self.LogicVarToXSB(y) for x in v for y in self.flatten(x))
            # error if number is too large, yielding missed facts:
            # return str(v) if v == '_' or isinstance(v, int) or (isinstance(v,str) and v.isdigit()) else \
            return str(v) if v == '_' or (isinstance(v, str) and v.isdigit()) or (not isinstance(v, bool) and isinstance(v, int)) else \
                "'None'" if (v is None or v == 'None') else \
                "0" if (v is False or v == 'False') else \
                "1" if (v is True or v == 'True') else "'%s'" % v
        else:
            if isinstance(v, tuple):
                return str(self.getid(v))
            if isinstance(v, list):
                return ','.join(self.LogicVarToXSB(y) for x in v for y in self.flatten(x))
            if v == '_':
                return v
            # if v is None or v == 'None':
            #     return 'None'
            # if v is False or v == 'False':
            #     return 'False'
            # if v is True or v == 'True':
            #     return 'True'
            # if isinstance(v, str):
            #     return "'%s'" % v
            return str(self.getid(v))

    def gen_fact(self, pred, val):
        if isinstance(val, (list, tuple, set)):
            return UniqueLowerCasePrefix+pred+'(%s)' % ','.join(self.LogicVarToXSB(v) for v in val)
        else:
            return UniqueLowerCasePrefix+pred+'(%s)' % self.LogicVarToXSB(val)

    def time_dur(self, t1, t2, name):  # os.times t1 and t2, string name
        u1, s1, cu1, cs1, elapsed1 = t1
        u2, s2, cu2, cs2, elapsed2 = t2
        print(f'{name}\t{elapsed2-elapsed1}\t{u2-u1 + s2-s1 + cu2-cu1 + cs2-cs1}')

    def xsb_file_interface(self):
        t_start = os.times()

        # generate facts
        xsb_facts = ""
        rule_filename = self.rules+'_'+self.gen_unique_id()
        for key, val in self.bindings:  # pair of predicate name and tuple values
            if len(val) == 0:  # val is an empty predicate
                # generate a place holder where all logic vars are -1
                xsb_facts += self.gen_fact(key, ['-1']*self.arity[key])+'.\n'
            elif not isinstance(val, list) and not isinstance(val, set):  # val is a single value
                xsb_facts += self.gen_fact(key, val)+'.\n'
            else:  # val is a set or list
                for v in val:
                    xsb_facts += self.gen_fact(key, v)+'.\n'

        write_file(rule_filename+'.facts', xsb_facts)
        # print('\tnum_fact\tfile_size')
        # print('datasize\t%s\t%s' % (len(xsb_facts.split('\n')),
        #     os.path.getsize(PurePath.joinpath(rule_path,rule_filename+'.facts'))))

        t_facts = os.times()  # after prep and write facts

        # generate queries, a list of tuple (out_file_name, query)
        _queries = []
        for q in self.queries:
            if q.find('(') < 0:  # if queries are passed with only prediate names
                # complete the query in form of pred(_,...,_)
                qstr = q + '(' + ','.join('_'*self.arity[q]) + ')'
                _queries.append([PurePath.joinpath(rule_path, rule_filename+'.'+q).as_posix(), UniqueLowerCasePrefix+qstr])
            else:  # if queries are passed in full
                # convert each logic variable to valid format for XSB
                pred = q.split('(')[0]
                var = q.split('(')[1].split(')')[0]
                _queries.append([PurePath.joinpath(rule_path, rule_filename+'.'+pred).as_posix(),
                                self.gen_fact(pred, var.strip().split(','))])

        print('', flush=True)  # clear the print(end='\r') after effect

        rule_path_rule = PurePath.joinpath(rule_path, self.rules)
        rule_path_fact = PurePath.joinpath(rule_path, rule_filename)
        if os.name == 'nt':
            rule_path_rule = str(rule_path_rule).replace('\\', '\\\\')
            rule_path_fact = str(rule_path_fact).replace('\\', '\\\\')

        xsb_query = "extfilequery:external_file_query('{}','{}',{}).".format(rule_path_rule, rule_path_fact, "[%s]" % ",".join(
            "['%s',%s]" % (qfile, qstr) for qfile, qstr in _queries))
        # print(xsb_query)

        # check if xsb command can be run
        status, output = subprocess.getstatusoutput('xsb -h')
        if status != 0:
            if 'xsb: command not found' in output:
                print('** ERROR! Rule Engine Not Found. Check Your Installation. **')
            else:
                print('** ERROR! %s **' % output)
            if len(_queries) == 1:
                return []
            else:
                return (None,) * len(_queries)

        t_pre = os.times()  # before run xsb

        # output = subprocess.run(["xsb",
        output = subprocess.run(['xsb', '--nobanner', '--quietload', '--noprompt',
                                '-e', "add_lib_dir(a('{}')).".format(xsb_path),
                                 '-e', xsb_query],
                                stdout=subprocess.PIPE, text=True)

        t_post = os.times()  # after run xsb

        results = []
        for r, _ in _queries:
            rname = PurePath(r).name
            answers = read_answer(rname)
            tuples = {tuple(self.eval_logicVar(v) for v in a.split(','))
                      if len(a.split(',')) > 1
                      else self.eval_logicVar(a)
                      for a in answers.split("\n")[:-1]}
            results.append(tuples)

        if common.get_runtime_option('timing', default=False):
            t_res = os.times()  # after reading results

            # times for reading data and querying in xsb
            lines = output.stdout.split('\n')
            lines = [l for l in lines if (l and l != 'yes' and l != 'no')]
            print('timing\telapse\tcpu')
            print('xsb_load\t%s\t%s' % (lines[-4], lines[-3]))
            print('xsb_query\t%s\t%s' % (lines[-2], lines[-1]))

            t_end = os.times()  # after reading std outuput

            # times for intefacing with xsb
            self.time_dur(t_start, t_facts, 'write_data')
            self.time_dur(t_start, t_pre, 'preproc_xsb')
            self.time_dur(t_pre, t_post, 'subprocess_xsb')
            self.time_dur(t_post, t_res, 'read_results')
            self.time_dur(t_post, t_end, 'postproc_xsb')

        if len(results) == 0:
            return results
        if len(results) == 1:  # there is only one query
            return results[0]
        return tuple(results)

    def xsb_px_interface(self):
        px = importlib.import_module("px")
        # TODO
        # BOOLEAN translated into 0 & 1, not safe, perhaps we need to first transform boolean into string
        #   px_comp(’mod’,’pred’,’a’,’b’,vars=2)
        # calls
        #   mod:pred(a,b,X1,X2)
        # the logical variable must precede ground arguments,
        #   so additional rule for rewriting the query to and from this form might be needed


def _infer(rules, arity, bindings, queries):
    infer_xsb = InferXSB(rules, arity, bindings, queries)
    return infer_xsb.xsb_file_interface()
    # TODO uncomment after finish writing xsb_px_interface
    # if importlib.util.find_spec("px"):
    #     return infer_xsb.xsb_px_interface()
    # else:
    #     return infer_xsb.xsb_file_interface()
