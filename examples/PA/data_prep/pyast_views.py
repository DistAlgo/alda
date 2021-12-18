""" generate pickled facts for the input module: 'folder or file,
and a user readable version by file.
"""

import ast,os,sys,shutil,pickle
from collections.abc import Collection
from pprint import pprint


class Generator:
    def __init__(self):
        self.reset()
        self.pickleFolder = '_state'
        self.txtFolder = 'astFacts'
        self.dbFolder = '../data'
        if not os.path.exists(self.dbFolder):
            os.mkdir(self.dbFolder)
    
    def reset(self):
        def gensym():
            i = 0
            while True:
                i += 1
                yield int(i)
        self.generator = gensym()
        self.ValueIdDict = dict()    # ValueIdDict[node] = id
        self.ValueDict = dict()      # ValueDict[id] = node
        self.FileDict = dict()       # FileDict[id] = file_id
        self.is_Sub = set()
        self.valueTag = set()        # type of values: 'int, float, str, bool, etc.
        self.allFacts = set()

    

    def getid(self, node):
        if isinstance(node, list):
            key = tuple(node)
        else:
            key = node
        if key not in self.ValueIdDict:
            genid = next(self.generator)
            self.ValueIdDict[key] = genid
            self.ValueDict[genid] = key
            return genid
        else:
            return self.ValueIdDict[key]

    def viewDast(self, node, context=[]):
        def getname(node):
            if isinstance(node,type):
                return node.__name__
            else:
                return node.__class__.__name__

        classname = getname(node)
        nodeflag = isinstance(node,ast.AST) or (isinstance(node,type) and issubclass(node,ast.AST))

        if node is not None:
            if nodeflag:
                children = [(a,getattr(node,a)) for a in node._fields if hasattr(node,a)]
                attributes = [(a,getattr(node,a)) for a in node._attributes if hasattr(node,a)]
                subs = children+attributes
            else:
                self.valueTag.add(classname)
                return set()
            
            own_view = (classname, self.getid(node), tuple((n,self.getid(c)) for n, c in children), tuple((a,self.getid(b)) if nodeflag else ((a,str(b)) if isinstance(b,str) else (a,b)) for a,b in attributes))
            ctxFact = {('Context', self.getid(node), ctx) for ctx in context[1:]}
            self.FileDict[self.getid(node)] = context[0]
            if classname in {'Module','Class','Function'}:
                context.append(self.getid(node))

            sub_views = set()
            for _,c in subs:
                if isinstance(c,Collection) and not isinstance(c,str) and not isinstance(c,bytes):
                    sub_views |= self.list_viewDast(c, context)
                else:
                    sub_views |= self.viewDast(c, context)
            try:
                return {own_view} | ctxFact | sub_views
            except:
                e = sys.exc_info()
                pprint(e)
                print(own_view)
                sys.exit(0)
        else:
            return set()

    def list_viewDast(self, ast_list, context=[]):
        elem_views = set()
        elems = None
        elem_views.add(('ListLen', self.getid(ast_list), len(ast_list)))
        ctxFact = {('Context', self.getid(ast_list), ctx) for ctx in context[1:]}
        self.FileDict[self.getid(ast_list)] = context[0]

        count = 0
        for c in ast_list:
            if isinstance(c, Collection) and not isinstance(c,str) and not isinstance(c,bytes):
                elem_views |= self.list_viewDast(c, context)
            else:
                elem_views |= self.viewDast(c, context)
            elem_views.add(('Member', self.getid(ast_list), self.getid(c), count))
            ctxFact |= {('Context', self.getid(c), ctx) for ctx in context[1:]}
            self.FileDict[self.getid(c)] = context[0]
            count += 1
        return elem_views | ctxFact

    def view_file(self, path, outputDir, prefix):
        extension = os.path.splitext(path)[1]
        print(extension, path)
        if extension == '.py':
            pyast = ast.parse(open(path, encoding = 'utf8').read(), filename=path)
            # pprint(pyast)
            name = os.path.basename(path)
            purenmae = os.path.splitext(name)[0]
            _id = os.path.join(prefix, purenmae)
            pkgid = self.getid(_id)
            facts = self.viewDast(pyast, [pkgid])
            self.allFacts |= facts
            deli = '\\' if sys.platform == 'win32' else '/'
            open(os.path.join(outputDir,_id.replace(deli,'.')+'.py'), 'w').write('\n'.join(repr(x) for x in facts))

    def view_directory(self, path, outputDir, prefix):
        print(path, outputDir, prefix)
        subfix = '.cpython-37m-darwin.so'
        for f in os.listdir(path):
            file = os.path.join(path,f)
            if os.path.isfile(file):
                if not (f.startswith('.') or f == 'desktop.ini'):
                    nonExt, Ext = os.path.splitext(f)
                    if Ext == '.py' or Ext == '.da':
                        self.is_Sub.add(('is_Sub', self.getid(os.path.join(prefix,nonExt)), self.getid(prefix)))
                        self.view_file(file, outputDir, prefix)
                    elif Ext == '.so':
                        self.is_Sub.add(('is_Sub', self.getid(os.path.join(prefix,f[:-len(subfix)])), self.getid(prefix)))
            if os.path.isdir(file):
                if not (f == '__pycache__' or f == 'tests' or f.startswith('.')):
                    self.is_Sub.add(('is_Sub', (self.getid(os.path.join(prefix,f))), self.getid(prefix)))
                    self.view_directory(file, outputDir, os.path.join(prefix,f))


    def gen_facts(self, filename):
        def gen_folders(project):
            projectFolder = os.path.join(self.dbFolder,project)
            if not os.path.exists(projectFolder):
                os.mkdir(projectFolder)
            for d in [self.pickleFolder, self.txtFolder]:
                outDir = os.path.join(projectFolder, d)
                if os.path.exists(outDir):
                    shutil.rmtree(outDir)
                os.mkdir(outDir)
            return projectFolder
        def dump_facts(datafolder, varname, data):
            print('dumping '+ varname)
            if varname != 'ValueDict123' and varname != "ValueIdDict123":
                pickle.dump(data,open(os.path.join(datafolder,self.pickleFolder,varname),'wb'))
                if not os.path.exists(os.path.join(datafolder,'text-rep')):
                    os.mkdir(os.path.join(datafolder,'text-rep'))
                text_out = open(os.path.join(datafolder,'text-rep',varname),'w', encoding='utf8')
                text_out.write(str(data))
                text_out.close()
        def dump_vars(datafolder):
            specialTag = {'is_Sub', 'Member','Context','ListLen'}
            ignoreAttr = {'lineno', 'col_offset', 'end_lineno','end_col_offset'}
            factdict = dict()
            print('generating facts by node type...')
            for f in self.allFacts:
                if f[0] not in factdict:
                    factdict[f[0]] = set()
                if f[0] in specialTag:
                    factdict[f[0]].add(tuple(list(f)[1:]))
                else:
                    _,id_,fields,attributes = f
                    factdict[f[0]].add((id_,)+
                                        tuple([a if a else None for (_,a) in fields])+
                                        tuple([d if d else None for (c,d) in attributes if c not in ignoreAttr]))

            for key, value in factdict.items():
                dump_facts(datafolder, key, value)
        print(filename)
        if os.path.isdir(filename):
            abspath = os.path.abspath(filename)
            packName = os.path.basename(abspath)
            projectFolder = gen_folders(packName)
            self.view_directory(abspath, os.path.join(projectFolder, self.txtFolder), packName)
        elif os.path.isfile(filename):
            packName, ext = os.path.splitext(os.path.basename(filename))
            projectFolder = gen_folders(packName)
            self.view_file(filename, os.path.join(projectFolder, self.txtFolder), '')
        
        for var in ['ValueDict', 'ValueIdDict', 'FileDict', 'is_Sub']:
            dump_facts(projectFolder, var, eval(f'self.{var}'))
        dump_vars(projectFolder)
        print('value types:',self.valueTag)


if __name__ == '__main__':
    paper = True

    def run_repo(repo):
        if paper:
            os.system(f'git clone {repo_map[repo]}')
            os.system(f'cd {repo} && git checkout {repo_branch[repo]}')
        else:
            os.system(f'git clone --depth=1 {repo_map[repo]}')
        g.reset()
        g.gen_facts(repo)    
    
    repos = ['https://github.com/numpy/numpy',
    'https://github.com/scipy/scipy',
    'https://github.com/matplotlib/matplotlib',
    'https://github.com/pandas-dev/pandas',
    'https://github.com/sympy/sympy',
    'https://github.com/django/django',
    'https://github.com/scikit-learn/scikit-learn',
    'https://github.com/pytorch/pytorch',
    'https://github.com/blender/blender']

    repo_map = {}
    for repo in repos:
        repo_map[repo.split('/')[-1]] = repo

    repo_branch = { 'blender' : '56ff9540307e0dee7478bbc4241d5e024ba1d8b3'
     ,'django' : '97e9a84d2746f76a635455c13bd512ea408755ac'
     ,'matplotlib': '59732ace84f3e4a0fb94084ee11598c655467d62'
     ,'numpy' : '0e10696f55576441fd820279d9ec10cd9f2a4c5d'
     ,'pandas' : '9db55a75243adbb1acaf49d2ce76cbd89a89c2e5'
     ,'pytorch' : '7142b0b033dfdc5821fb4ac47103df60a2ed14d4'
     ,'scikit-learn' : '594b1f70fcdb0fa7143c681dad1ffc1b24755dbd'
     ,'scipy' : '9a504cd27ad6f7b3c0590f2c7fef9f329ef56508'
     ,'sympy' : '4489b4c7c51a65966b1a95f2af6f7e0c8c461794'
    }

    g = Generator()
    if len(sys.argv) > 1:
        run_repo(sys.argv[1])
    else:
        for repo in repo_map:
            run_repo(repo)