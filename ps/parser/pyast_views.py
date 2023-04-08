""" generate pickled facts for the input module: folder or file,
and a user readable version by file.
"""

from ..constants import *

import ast
import os
import sys
import shutil
import pickle
from collections.abc import Collection
from pprint import pprint, pformat

import logging
# logger = logging.getLogger()


ASTNodes = {
    # 'AST','mod',
    'Module', 'Interactive', 'Expression', 'Suite',
    # 'stmt',
    'FunctionDef', 'AsyncFunctionDef', 'ClassDef',
    'Return', 'Delete', 'Assign', 'AugAssign', 'AnnAssign',
    'For', 'AsyncFor', 'While', 'If', 'With', 'AsyncWith',
    'Raise', 'Try', 'Assert', 'Import', 'ImportFrom',
    'Global', 'Nonlocal', 'Expr', 'Pass', 'Break', 'Continue',
    # 'expr',
    'BoolOp', 'BinOp', 'UnaryOp', 'Lambda', 'IfExp',
    'Dict', 'Set', 'ListComp', 'SetComp', 'DictComp', 'GeneratorExp',
    'Await', 'Yield', 'YieldFrom', 'Compare', 'Call',
    'Num', 'Str', 'FormattedValue', 'JoinedStr', 'Bytes', 'NameConstant',
    'Ellipsis', 'Constant',
    'Attribute', 'Subscript', 'Starred', 'Name', 'List', 'Tuple',
    # 'expr_context',
    'Load', 'Store', 'Del', 'AugLoad', 'AugStore', 'Param',
    # 'slice',
    'Slice', 'ExtSlice', 'Index',
    # 'boolop',
    'And', 'Or',
    # 'operator',
    'Add', 'Sub', 'Mult', 'MatMult', 'Div', 'Mod', 'Pow', 'LShift', 'RShift', 'BitOr', 'BitXor', 'BitAnd', 'FloorDiv',
    # 'unaryop',
    'Invert', 'Not', 'UAdd', 'USub',
    # 'cmpop',
    'Eq', 'NotEq', 'Lt', 'LtE', 'Gt', 'GtE', 'Is', 'IsNot', 'In', 'NotIn',
    'comprehension',
    # 'excepthandler',
    'ExceptHandler',
    'arguments', 'arg', 'keyword', 'alias', 'withitem',
    # util nodes
    'is_Sub', 'Member', 'Context', 'ListLen',
}


class ViewAST:
    def __init__(self, source, scope, persist, persist_loc, update, package, ignore, encoding):
        self.ValueIdDict = dict()    # ValueIdDict[node] = id
        self.ValueDict = dict()      # ValueDict[id] = node
        self.FileDict = dict()       # FileDict[id] = file_id
        self.is_Sub = set()
        # type of values: int, float, str, bool, etc.
        self.valueTag = set()
        self.allFacts = set()
        self.specialTag = {'is_Sub', 'Member', 'Context', 'ListLen'}
        self.encoding = encoding

        self.ignoreField = ignore.get('fields', {})
        self.ignoreAttr = ignore.get('attributes', {})
        self.generator = self.gensym()
        self.pickleFolder = '_state'
        self.txtFolder = 'astFacts'
        self.txtRepFolder = 'text-rep'
        # self.checksumFolder = 'checksum'
        if not isinstance(source, str) and not isinstance(source, ast.AST):
            logging.error('source can only be a string path or an ast.AST object')
            sys.exit(0)
        self.source = source
        if not isinstance(scope, dict) and not isinstance(scope, object):
            logging.error('scope can only be a dict or an object')
            sys.exit(0)
        self.scope = scope
        self.persist = persist
        self.dbFolder = persist_loc if persist_loc else ''
        self.update = update
        self.package = package

        if persist:
            if not os.path.exists(self.dbFolder):
                os.mkdir(self.dbFolder)
        if not package:
            if isinstance(source, str):
                if os.path.isdir(source):
                    abspath = os.path.abspath(source)
                    self.package = os.path.basename(abspath)
                elif os.path.isfile(source):
                    self.package, _ = os.path.splitext(os.path.basename(source))
                else:
                    logging.error('source not exist')
                    sys.exit(0)
            elif persist:
                logging.error('package name must be provided to store the facts in the ast node to disk')
                sys.exit(0)
        if self.package:
            deli = '\\' if sys.platform == 'win32' else '/'
            self.package = self.package.replace(deli, '.')

    def start(self):
        logging.info("persist: %s, persist_loc: %s, update: %s, package: %s", self.persist, self.dbFolder, self.update, self.package)
        if self.persist and not self.update and self.package:
            dbPath = os.path.join(self.dbFolder, self.package)
            if os.path.exists(dbPath) and self.load(dbPath):
                logging.info('facts loaded from database')
                return
            # return

        if self.package:
            self.projectFolder = self.gen_folders(self.package)
        if isinstance(self.source, str):
            if os.path.exists(self.source):
                self.gen_facts(self.source)
            else:
                logging.error('source not exist')
                sys.exit(0)
        elif isinstance(self.source, ast.AST):
            self.allFacts = self.viewDast(self.source)
        else:
            logging.error('source can only be a string path or an ast.AST object')
            sys.exit(0)

        self.save_facts()

    def load(self, filename):
        """ load from database
        """
        logging.info('loading')
        bak = os.path.join(filename, '_state')
        if not (os.path.exists(bak) and os.listdir(bak)):
            return False
        for y in os.listdir(bak):
            if y.startswith('.'):
                continue
            if isinstance(self.scope, dict):
                self.scope[y] = pickle.load(open(os.path.join(bak, y), 'rb'))
            elif isinstance(self.scope, object):
                setattr(self.scope, y, pickle.load(open(os.path.join(bak, y), 'rb')))
        self.set_absent_facts()
        return True

    def getname(self, node):
        if isinstance(node, type):
            return node.__name__
        else:
            return node.__class__.__name__

    def gensym(self):
        i = 0
        while True:
            i += 1
            yield int(i)

    def getid(self, node):
        if isinstance(node, list):
            key = tuple(node)
            if not self.encoding:
                # return ('ListInAST',) + key
                return key
        else:
            key = node
            if not self.encoding:
                return key
        if key not in self.ValueIdDict:
            genid = next(self.generator)
            self.ValueIdDict[key] = genid
            self.ValueDict[genid] = key
            return genid
        else:
            return self.ValueIdDict[key]

    def viewDast(self, node, context=[]):
        classname = self.getname(node)
        nodeflag = isinstance(node, ast.AST) or (isinstance(node, type) and issubclass(node, ast.AST))

        if node is not None:
            if nodeflag:
                children = [(a, getattr(node, a))
                            for a in node._fields if hasattr(node, a)]
                attributes = [(a, getattr(node, a))
                              for a in node._attributes if hasattr(node, a)]
                subs = children+attributes
            else:
                self.valueTag.add(classname)
                return set()

            own_view = (
                classname,
                self.getid(node),
                tuple((n, self.getid(c)) for n, c in children),
                tuple((a, self.getid(b)) if nodeflag
                      else ((a, str(b)) if isinstance(b, str)
                            else (a, b))
                      for a, b in attributes))
            ctxFact = {('Context', self.getid(node), ctx) for ctx in context[1:]}
            if context:
                self.FileDict[self.getid(node)] = context[0]
            if classname in {'Module', 'Class', 'Function'}:
                context.append(self.getid(node))

            sub_views = set()
            for _, c in subs:
                if isinstance(c, Collection) and not isinstance(c, str) and not isinstance(c, bytes):
                    sub_views |= self.list_viewDast(c, context)
                else:
                    sub_views |= self.viewDast(c, context)
            try:
                return {own_view} | ctxFact | sub_views
            except:
                e = sys.exc_info()
                logging.error(pformat(e))
                logging.error(pformat(own_view))
                sys.exit(0)
        else:
            return set()

    def list_viewDast(self, ast_list, context=[]):
        elem_views = set()
        elem_views.add(('ListLen', self.getid(ast_list), len(ast_list)))
        ctxFact = {('Context', self.getid(ast_list), ctx)
                   for ctx in context[1:]}
        self.FileDict[self.getid(ast_list)] = context[0]

        count = 0
        for c in ast_list:
            if isinstance(c, Collection) and not isinstance(c, str) and not isinstance(c, bytes):
                elem_views |= self.list_viewDast(c, context)
            else:
                elem_views |= self.viewDast(c, context)
            elem_views.add(('Member', self.getid(ast_list), self.getid(c), count))
            ctxFact |= {('Context', self.getid(c), ctx) for ctx in context[1:]}
            self.FileDict[self.getid(c)] = context[0]
            count += 1
        return elem_views | ctxFact

    # def txtRepToSet(self, file):
    #     """ parse the text representation of each file to a dictionary of sets
    #     used for reading existing files
    #     """
    #     lines = open(file, 'r').readlines()
    #     facts = dict()
    #     for line in lines:
    #         t = ast.literal_eval(line)
    #         if t[0] in self.specialTag:
    #             ...
    #         else:
    #             ...

    def view_file(self, path, outputDir, prefix):
        extension = os.path.splitext(path)[1]
        logging.info("extension: %s, path: %s", extension, path)
        if extension == '.py':
            file_content = open(path, encoding='utf8').read()
            name = os.path.basename(path)
            purenmae = os.path.splitext(name)[0]
            _id = os.path.join(prefix, purenmae)

            # if self.persist or self.update == PA_CHECK:
            #     checksum = hashlib.md5(file_content).hexdigest()
            #     checksum_path = os.path.join(outputDir, self.checksumFolder, _id.replace(deli, '.')+'.py')
            #     deli = '\\' if sys.platform == 'win32' else '/'
            #     astFacts_path = os.path.join(outputDir, self.txtFolder, _id.replace(deli, '.')+'.py')
            # if self.update == PA_CHECK:
            #     if os.path.isfile(checksum_path):
            #         checksum_exist = open(checksum_path, encoding='utf8').read()
            #         if checksum == checksum_exist and os.path.isfile(astFacts_path):
            #             facts = self.txtRepToSet(astFacts_path)
            #             self.allFacts |= facts
            #             return

            pyast = ast.parse(file_content, filename=path)
            pkgid = self.getid(_id)
            facts = self.viewDast(pyast, [pkgid])
            self.allFacts |= facts
            if self.persist:
                # open(checksum_path, 'w').write(checksum)
                deli = '\\' if sys.platform == 'win32' else '/'
                astFacts_path = os.path.join(outputDir, self.txtFolder, _id.replace(deli, '.')+'.py')
                open(astFacts_path, 'w').write('\n'.join(repr(x) for x in facts))

    def view_directory(self, path, outputDir, prefix):
        logging.info("path: %s, outputDir: %s, prefix: %s",
                     path, outputDir, prefix)
        subfix = '.cpython-37m-darwin.so'
        for f in os.listdir(path):
            file = os.path.join(path, f)
            if os.path.isfile(file):
                if not (f.startswith('.') or f == 'desktop.ini'):
                    nonExt, Ext = os.path.splitext(f)
                    if Ext == '.py' or Ext == '.da':
                        self.is_Sub.add(('is_Sub', self.getid(os.path.join(prefix, nonExt)), self.getid(prefix)))
                        self.view_file(file, outputDir, prefix)
                    elif Ext == '.so':
                        self.is_Sub.add(('is_Sub', self.getid(os.path.join(prefix, f[:-len(subfix)])), self.getid(prefix)))
            if os.path.isdir(file):
                if not (f == '__pycache__' or f == 'tests' or f.startswith('.')):
                    self.is_Sub.add(('is_Sub', (self.getid(os.path.join(prefix, f))), self.getid(prefix)))
                    self.view_directory(file, outputDir, os.path.join(prefix, f))

    def gen_folders(self, project):
        projectFolder = os.path.join(self.dbFolder, project)
        if self.persist:
            if not os.path.exists(projectFolder):
                os.mkdir(projectFolder)
            for d in [self.pickleFolder, self.txtFolder, self.txtRepFolder]:  # , self.checksumFolder
                outDir = os.path.join(projectFolder, d)
                if os.path.exists(outDir):
                    shutil.rmtree(outDir)
                os.mkdir(outDir)
        return projectFolder

    def gen_facts(self, filename):
        """ Entry point of generate facts
        """
        logging.info("generating facts for file: %s", filename)
        if os.path.isdir(filename):
            abspath = os.path.abspath(filename)
            self.view_directory(abspath, self.projectFolder, self.package)
        elif os.path.isfile(filename):
            self.view_file(filename, self.projectFolder, '')

    def dump_facts(self, datafolder, varname, data):
        logging.info('dumping ' + varname)
        pickle.dump(data, open(os.path.join(datafolder, self.pickleFolder, varname), 'wb'))
        with open(os.path.join(datafolder, self.txtRepFolder, varname), 'w', encoding='utf8') as text_out:
            text_out.write(pformat(data))

    def save_facts(self):
        factdict = dict()
        logging.info('generating facts by node type...')
        for f in self.allFacts:
            if f[0] not in factdict:
                factdict[f[0]] = set()
            if f[0] in self.specialTag:
                factdict[f[0]].add(tuple(list(f)[1:]))
            else:
                _, id_, fields, attributes = f
                factdict[f[0]].add((id_,) +
                                   tuple([a if a else None for (b, a) in fields if b not in self.ignoreField]) +
                                   tuple([d if d else None for (c, d) in attributes if c not in self.ignoreAttr]))

        for key, value in factdict.items():
            if isinstance(self.scope, dict):
                self.scope[key] = value
            elif isinstance(self.scope, object):
                setattr(self.scope, key, value)
            if self.persist:
                self.dump_facts(self.projectFolder, key, value)

        for var in ['ValueDict', 'ValueIdDict', 'FileDict', 'is_Sub']:
            if isinstance(self.scope, dict):
                self.scope[var] = getattr(self, var)
            elif isinstance(self.scope, object):
                setattr(self.scope, var,  getattr(self, var))
            if self.persist:
                self.dump_facts(self.projectFolder, var, getattr(self, var))

        self.set_absent_facts()
        logging.info('value types: %s', self.valueTag)

    def set_absent_facts(self):
        for x in ASTNodes:
            if isinstance(self.scope, dict):
                if x not in self.scope:
                    self.scope[x] = set()
            elif isinstance(self.scope, object):
                if not hasattr(self.scope, x):
                    setattr(self.scope, x, set())
