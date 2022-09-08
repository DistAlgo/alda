""" generate pickled facts for the input module: folder or file,
and a user readable version by file.
"""

import ast,os,sys,shutil,pickle
from collections.abc import Collection
from pprint import pprint, pformat

ValueIdDict = dict()    # ValueIdDict[node] = id
ValueDict = dict()      # ValueDict[id] = node
FileDict = dict()       # FileDict[id] = file_id
is_Sub = set()
valueTag = set()        # type of values: int, float, str, bool, etc.
allFacts = set()

def getname(node):
    if isinstance(node,type):
        return node.__name__
    else:
        return node.__class__.__name__

def gensym():
    i = 0
    while True:
        i += 1
        yield int(i)
generator = gensym()

def getid(node):
    if isinstance(node, list):
        key = tuple(node)
    else:
        key = node
    if key not in ValueIdDict:
        genid = next(generator)
        ValueIdDict[key] = genid
        ValueDict[genid] = key
        return genid
    else:
        return ValueIdDict[key]

def viewDast(node, context=[]):
    classname = getname(node)
    nodeflag = isinstance(node,ast.AST) or (isinstance(node,type) and issubclass(node,ast.AST))

    if node is not None:
        if nodeflag:
            children = [(a,getattr(node,a)) for a in node._fields if hasattr(node,a)]
            attributes = [(a,getattr(node,a)) for a in node._attributes if hasattr(node,a)]
            subs = children+attributes
        else:
            valueTag.add(classname)
            return set()

        own_view = (classname, getid(node), tuple((n,getid(c)) for n, c in children), tuple((a,getid(b)) if nodeflag else ((a,str(b)) if isinstance(b,str) else (a,b)) for a,b in attributes))
        ctxFact = {('Context', getid(node), ctx) for ctx in context[1:]}
        FileDict[getid(node)] = context[0]
        if classname in {'Module','Class','Function'}:
            context.append(getid(node))

        sub_views = set()
        for _,c in subs:
            if isinstance(c,Collection) and not isinstance(c,str) and not isinstance(c,bytes):
                sub_views |= list_viewDast(c, context)
            else:
                sub_views |= viewDast(c, context)
        try:
            return {own_view} | ctxFact | sub_views
        except:
            e = sys.exc_info()
            pprint(e)
            print(own_view)
            sys.exit(0)
    else:
        return set()

def list_viewDast(ast_list, context=[]):
    elem_views = set()
    elems = None
    elem_views.add(('ListLen', getid(ast_list), len(ast_list)))
    ctxFact = {('Context', getid(ast_list), ctx) for ctx in context[1:]}
    FileDict[getid(ast_list)] = context[0]

    count = 0
    for c in ast_list:
        if isinstance(c, Collection) and not isinstance(c,str) and not isinstance(c,bytes):
            elem_views |= list_viewDast(c, context)
        else:
            elem_views |= viewDast(c, context)
        elem_views.add(('Member', getid(ast_list), getid(c), count))
        ctxFact |= {('Context', getid(c), ctx) for ctx in context[1:]}
        FileDict[getid(c)] = context[0]
        count += 1
    return elem_views | ctxFact

def view_file(path, outputDir, prefix):
    global allFacts
    extension = os.path.splitext(path)[1]
    print(extension, path)
    if extension == '.py':
        pyast = ast.parse(open(path, encoding = 'utf8').read(), filename=path)
        name = os.path.basename(path)
        purenmae = os.path.splitext(name)[0]
        _id = os.path.join(prefix, purenmae)
        pkgid = getid(_id)
        facts = viewDast(pyast, [pkgid])
        allFacts |= facts
        deli = '\\' if sys.platform == 'win32' else '/'
        open(os.path.join(outputDir,_id.replace(deli,'.')+'.py'), 'w').write('\n'.join(repr(x) for x in facts))

def view_directory(path, outputDir, prefix):
    print(path, outputDir, prefix)
    subfix = '.cpython-37m-darwin.so'
    for f in os.listdir(path):
        file = os.path.join(path,f)
        if os.path.isfile(file):
            if not (f.startswith('.') or f == 'desktop.ini'):
                nonExt, Ext = os.path.splitext(f)
                if Ext == '.py' or Ext == '.da':
                    is_Sub.add(('is_Sub', getid(os.path.join(prefix,nonExt)), getid(prefix)))
                    view_file(file, outputDir, prefix)
                elif Ext == '.so':
                    is_Sub.add(('is_Sub', getid(os.path.join(prefix,f[:-len(subfix)])), getid(prefix)))
        if os.path.isdir(file):
            if not (f == '__pycache__' or f == 'tests' or f.startswith('.')):
                is_Sub.add(('is_Sub', (getid(os.path.join(prefix,f))), getid(prefix)))
                view_directory(file, outputDir, os.path.join(prefix,f))

pickleFolder = '_state'
txtFolder = 'astFacts'
txtRepFolder = 'text-rep'
dbFolder = '../data'
if not os.path.exists(dbFolder):
    os.mkdir(dbFolder)

def dump_facts(datafolder, varname, data):
    print('dumping '+ varname)
    pickle.dump(data,open(os.path.join(datafolder,pickleFolder,varname),'wb'))
    with open(os.path.join(datafolder,'text-rep',varname),'w', encoding='utf8') as text_out:
        text_out.write(pformat(data))

specialTag = {'is_Sub', 'Member','Context','ListLen'}
ignoreField = {'type_comment'}
ignoreAttr = {'lineno', 'col_offset', 'end_lineno', 'end_col_offset'}
def dump_vars(datafolder):
    factdict = dict()
    print('generating facts by node type...')
    for f in allFacts:
        if f[0] not in factdict:
            factdict[f[0]] = set()
        if f[0] in specialTag:
            factdict[f[0]].add(tuple(list(f)[1:]))
        else:
            _,id_,fields,attributes = f
            factdict[f[0]].add((id_,)+
                                tuple([a if a else None for (b,a) in fields if b not in ignoreField])+
                                tuple([d if d else None for (c,d) in attributes if c not in ignoreAttr]))

    for key, value in factdict.items():
        dump_facts(datafolder, key, value)

def gen_folders(project):
    projectFolder = os.path.join(dbFolder,project)
    if not os.path.exists(projectFolder):
        os.mkdir(projectFolder)
    for d in [pickleFolder, txtFolder, txtRepFolder]:
        outDir = os.path.join(projectFolder, d)
        if os.path.exists(outDir):
            shutil.rmtree(outDir)
        os.mkdir(outDir)
    return projectFolder

def gen_facts(filename):
    print(filename)
    if os.path.isdir(filename):
        abspath = os.path.abspath(filename)
        packName = os.path.basename(abspath)
        projectFolder = gen_folders(packName)
        view_directory(abspath, os.path.join(projectFolder, txtFolder), packName)
    elif os.path.isfile(filename):
        packName, ext = os.path.splitext(os.path.basename(filename))
        projectFolder = gen_folders(packName)
        view_file(filename, os.path.join(projectFolder, txtFolder), '')
    
    for var in ['ValueDict', 'ValueIdDict', 'FileDict', 'is_Sub']:
        dump_facts(projectFolder, var, eval(var))
    dump_vars(projectFolder)
    print('value types:',valueTag)

if __name__ == '__main__':
    filename = '/Users/yitong/Downloads/numpy' if len(sys.argv) < 2 else sys.argv[1]
    gen_facts(filename)




