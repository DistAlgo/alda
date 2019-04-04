import sys

sys.setrecursionlimit(10000)

def views(ast):  
    """ return a set-of-tuples view of distalgo ast.
        assume: ast root node is never a list or a leaf
    """
    print('====', ast)

    classname = type(ast)
    print('----classname', classname, classname._fields, ast.__dict__)

    children = [getattr(ast,f) for f in classname._fields]
    print('----children', children)

    own_view = (classname.__name__, id(ast)) +\
        tuple((id(c) if hasattr(c,'_fields') else str(c)) for c in children)
    print('----own_view', own_view)  # todo: when c is list, avoid use str(c)

    sub_views = {x for c in children 
                 if (hasattr(c,'_fields') or isinstance(c,list))
                 for x in (list_views(c) if isinstance(c,list) else views(c))}
    print('----sub_views', 
          sub_views if len(sub_views)<=20 else str(list(sub_views)[:20])+'...')

    return {own_view} | sub_views

def list_views(ast_list):
    """ return a set of tuples when ast_list is a list
    """
    print('========', ast_list)

    elem_views = {x for c in ast_list for x in views(c)}
    return elem_views

    # todo: build tuples/pairs for list spine, only needed when order matters
    if ast_list == []: return tuple('EmptyList')
    head = ast_list[0]
    list_views(ast_list[1:0])
    return set()

if __name__ == '__main__':
    from da.compiler.dast import *
    from da.compiler.ui import daast_from_file
    from da.compiler.ui import parse_compiler_args  # should use None, not this

    filename = sys.argv[1]
    daast = daast_from_file(filename, parse_compiler_args([]))
    print(daast)
    print('____\n', '\n'.join(str(x) for x in views(daast._ast)))

# todo's above are only for list, and are only needed when 
# the order of list elements matters for the analysis of interest
