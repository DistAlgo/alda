import os

PS_LOCAL = 'local'
PS_GLOBAL = 'global'
PS_CLASS = 'class'
PS_CHECK = 'check'
CODE = 'code'
AST = 'ast'
DEFAULT_DB = os.path.join(os.path.expanduser('~'), 'ps_db')
#DEFAULT_DB = './ps_db'
DEFAULT_CONFIG = {
    'source': None,
    'target': None,
    'db_path': DEFAULT_DB,
    'db_name': None,
    'db_update': False,
    'omit': {
        'attributes': {'lineno', 'col_offset', 'end_lineno', 'end_col_offset'},
        'fields': {'type_comment'}
    },
    'encode': True
}
