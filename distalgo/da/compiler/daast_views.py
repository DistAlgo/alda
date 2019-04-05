import sys
from pprint import pprint
import da.compiler.dast as dast

sys.setrecursionlimit(10000)


NodeDict = dict()


def views(ast):  
    """ return a set-of-tuples view of distalgo ast.
        assume: ast root node is never a list or a leaf
    """
    # print('====', ast)
    # pprint(ast)
    # pprint(vars(ast))

    classname = type(ast)
    print('----classname', classname, classname._fields, ast.__dict__)

    children = [getattr(ast,f) for f in classname._fields]
    # print('----children', children)

    own_view = (classname.__name__, id(ast)) +\
        tuple((id(c) if hasattr(c,'_fields') else str(c)) for c in children)
    # print('----own_view', own_view)  # todo: when c is list, avoid use str(c)

    sub_views = {x for c in children 
                 if (hasattr(c,'_fields') or isinstance(c,list))
                 for x in (list_views(c) if isinstance(c,list) else views(c))}
    # print('----sub_views', 
    #       sub_views if len(sub_views)<=20 else str(list(sub_views)[:20])+'...')

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

def getname(ast):
    return ast.__class__.__name__

def viewDast(ast):
    classname = getname(ast)
    print('==============================', classname, '==============================')

    # if not hasattr(ast,'_fields'):
    #     own_view = (classname, id(ast))
    #     return {own_view}

    children = list(filter(None,[getattr(ast,a) for a in ast._fields if hasattr(ast,a)]))

    own_view = (classname, id(ast)) +\
        tuple(((getname(c), id(c)) if isinstance(c,dast.DistNode) else str(c)) for c in children)
    # print('------------------------ own_view ------------------------')
    pprint(own_view)

    # print('•••••••••••••••• children ••••••••••••••••')
    # pprint(children)

    sub_views = {x for c in children 
                 if (isinstance(c,dast.DistNode) or isinstance(c,list))
                 for x in (list_viewDast(c) if isinstance(c,list) else viewDast(c))}
    # print('sub_views')
    # pprint(sub_views)

    return {own_view} | sub_views  

def list_viewDast(ast_list):
    elem_views = set()
    for c in ast_list:
        if isinstance(c,dast.DistNode):
            x = viewDast(c)
            elem_views |= x
        else:
            elem_views.add(c)
    # elem_views = {x for x in viewDast(c) if hasattr(c,'_fields') else c for c in ast_list  }
    return elem_views

if __name__ == '__main__':
    from da.compiler.dast import *
    from da.compiler.ui import daast_from_file
    from da.compiler.ui import parse_compiler_args  # should use None, not this

    filename = sys.argv[1]
    daast = daast_from_file(filename, parse_compiler_args([]))
    # print(daast)
    # print()
    # print(daast.__class__.__name__)
    # # pprint(vars(daast._ast))
    # for i in daast.body:
    #     pprint(i._fields)
    #     pprint(vars(i))
    # views(daast._ast)
    # print('____\n', '\n'.join(str(x) for x in viewDast(daast)))
    pprint(viewDast(daast))

# todo's above are only for list, and are only needed when 
# the order of list elements matters for the analysis of interest
