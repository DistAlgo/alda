import ast
import os,sys
from pprint import pprint
from collections.abc import Collection
import uuid
import shutil
import pickle

ValueIdDict = dict()    #ValueIdDict[node] = id
ValueDict = dict()      #ValueDict[id] = node
valueTag = set()

dbFolder = './data'
# ObjectDict = dict()

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
    # if isinstance(node,ast.AST) or (isinstance(node,type) and issubclass(node,ast.AST)):
    #     return id(node)
    # else:
    #     return uuid.uuid3(uuid.NAMESPACE_DNS, str(node)).fields[0]
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
    
        # print(ValueIdDict)

        
    


def viewDast(node, package=None):
    classname = getname(node)
    nodeflag = isinstance(node,ast.AST) or (isinstance(node,type) and issubclass(node,ast.AST))

    if node is not None:
        if nodeflag:
            children = [(a,getattr(node,a)) for a in node._fields if hasattr(node,a)]
            attributes = [(a,getattr(node,a)) for a in node._attributes if hasattr(node,a)]
            subs = children+attributes
        else:
            valueTag.add(classname)
            # children = []
            # attributes = [('value',node)]
            # subs = []
            return set()
        
        own_view = (classname, getid(node), tuple((n,getid(c)) for n, c in children), tuple((a,getid(b)) if nodeflag else ((a,str(b)) if isinstance(b,str) else (a,b)) for a,b in attributes)) + (package,)

        sub_views = set()
        for _,c in subs:
            if isinstance(c,Collection) and not isinstance(c,str) and not isinstance(c,bytes):
                sub_views |= list_viewDast(c, package)
            else:
                sub_views |= viewDast(c, package)
        try:
            return {own_view} | sub_views
        except:
            e = sys.exc_info()
            pprint(e)
            print(own_view)
            sys.exit(0)
    else:
        return set()

def list_viewDast(ast_list, package=None):
    elem_views = set()
    elems = None
    elem_views.add(('ListLen' ,getid(ast_list),len(ast_list),package))
    count = 0

    for c in ast_list:
        if isinstance(c, Collection) and not isinstance(c,str) and not isinstance(c,bytes):
            elem_views |= list_viewDast(c, package)
        else:
            elem_views |= viewDast(c, package)
        elems = getid(c)
        elem_views.add(('Member', getid(ast_list), elems, count, package))
        count += 1
    return elem_views


def view_file(path, outputDir, prefix):
    extension = os.path.splitext(path)[1]
    print(extension, path)
    if extension == '.py':
        f = open(path)
        pyast = ast.parse(f.read(), filename=path)
        f.close()
        # pprint(pyast)
        name = os.path.basename(path)
        _id = os.path.splitext(prefix+name)[0]
        pkgid = getid(_id)
        #('str', 3482164824, (), (('value', 'diff'),), 'sympy.algebras.quaternion')
        # pkgNode = ('str', pkgid, (), (('value', _id),), pkgid)
        f = open(os.path.join(outputDir,prefix+name), 'w')
        f.write('\n'.join(str(x) for x in viewDast(pyast, pkgid)))
        f.close()

def view_directory(path, outputDir, prefix):
    print(path, outputDir, prefix)
    subfix = '.cpython-37m-darwin.so'
    for f in os.listdir(path):
        
        file = os.path.join(path,f)
        if os.path.isfile(file):
            if not (f.startswith('.') or f == 'desktop.ini'):
                nonExt, Ext = os.path.splitext(f)
                if Ext == '.py':

                    packageFD.write("('is_Sub', '%s', '%s')\n" % (getid(prefix+nonExt), getid(prefix[:-1])))
                    view_file(file, outputDir, prefix)
                elif f.endswith(subfix):
                    packageFD.write("('is_Sub', '%s', '%s')\n" % (getid(prefix+f[:-len(subfix)]), getid(prefix[:-1])))
        if os.path.isdir(file):
            if not (f == '__pycache__' or f == 'tests' or f.startswith('.')):
                packageFD.write("('is_Sub', '%s', '%s')\n" % (getid(prefix+f), getid(prefix[:-1])))
                view_directory(file, outputDir, prefix+f+'.')

def gen_facts(filename):
    print(filename)
    if os.path.isdir(filename):
        path = os.path.abspath(filename)
        packName = os.path.basename(path)
        if not os.path.exists(dbFolder):
            os.mkdir(dbFolder)
        projectFolder = os.path.join(dbFolder,packName)
        if not os.path.exists(projectFolder):
            os.mkdir(projectFolder)
        outDir = os.path.join(projectFolder,'astFacts')
        if os.path.exists(outDir):
            shutil.rmtree(outDir)
        os.mkdir(outDir)
        global packageFD
        packageFD = open(os.path.join(outDir,'pkginfo_'+packName+'.py'), 'w')
        view_directory(path, outDir, packName+'.')
        packageFD.close()

        datafolder = os.path.join(projectFolder,'_state')
        if os.path.exists(datafolder):
            shutil.rmtree(datafolder)
        os.mkdir(datafolder)
        f = open(os.path.join(datafolder,'ValueDict'),'wb')
        pickle.dump(ValueDict,f)
        f.close()
        f = open(os.path.join(datafolder,'ValueIdDict'),'wb')
        pickle.dump(ValueIdDict,f)
        f.close()

        datafolder = os.path.join(projectFolder,'pickleFacts')
        if os.path.exists(datafolder):
            shutil.rmtree(datafolder)
        os.mkdir(datafolder)
        f = open(os.path.join(datafolder,'valueTag'),'wb')
        pickle.dump(valueTag,f)
        f.close()
        pprint(valueTag)
        return projectFolder

    elif os.path.isfile(filename):
        if not os.path.exists('./output/'):
            os.mkdir('./output/')
        view_file(filename, './output/', 'ast_')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        filename = '/Users/COTTON/Downloads/numpy'
    else:
        filename = sys.argv[1]
    gen_facts(filename)




