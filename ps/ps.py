from .constants import *
from .parser.pyast_views import ViewAST
import json
import os
import sys
import ast
from da.compiler.utils import to_source

import logging


class PS:
    def __init__(self, config_path=None):
        self.conf = DEFAULT_CONFIG
        self.config_file = None
        if config_path:
            self.config(file=config_path)

    def load_config(self, file):
        self.config_file = file
        self.config(file=file)

    def save_config(self):
        if self.config_file:
            # TODO write config back to file
            pass

    def config(self, *, file=None, source=None, target=None, db_path='', db_update=None,
               db_name=None, omit=None, encode=None, multiset_disc=None):
        """ Configuration of ps fact generator

        The configuration can be either given as a json file or passed in as parameters

        Parameters are the same as :py:meth:`.ps.PS.read`

        If file and any other parameters are set, those set in parameters will override those in files
        """

        if file:
            if not os.path.exists(file):
                logging.error("config file not exist")
                sys.exit(0)

            with open(file, 'rb') as f:
                conf = json.load(f)
                for key, val in conf.items():
                    if key in DEFAULT_CONFIG:
                        self.conf[key] = val

        # process arguments passed in as parameters
        for key, val in locals().items():
            if key in DEFAULT_CONFIG:
                if key == 'db_path':
                    if val != '':
                        self.conf[key] = val
                else:
                    if val != None:
                        self.conf[key] = val

    def read(self, *, source=None, target=None, db_path='', db_update=None,
             db_name=None, omit=None, encode=None, multiset_disc=None):
        """ Read python module or file and generate sets of facts of AST nodes
        - multiset_disc: WIP. whether performing multiset discrimination when generating facts, so that facts with recursively identify structures are considered the same.
        """
        conf = dict()
        for key, val in self.conf.items():
            if key == target:
                continue
            if key == 'db_path':
                if locals()[key] != '':
                    conf[key] = locals()[key]
                else:
                    conf[key] = val
            else:
                conf[key] = locals()[key] if (key in locals() and locals()[key] != None) else val

        if not conf['source']:
            logging.error('A file path or an AST node must be provided as source')
            sys.exit(0)
        if target == None:
            # if conf['target'] == None:
            #     conf['target'] = dict()
            logging.error('target must be provided to store all the generated facts')
            sys.exit(0)
        elif not isinstance(conf['source'], str):
            logging.error('source can only be a string path or an ast.AST object')
            sys.exit(0)
        if not isinstance(conf['omit'], dict):
            logging.error('omit must be a dictionary indicating which fields and attributes to be omit respectively')
            sys.exit(0)

        ViewAST(conf['source'], target, conf['db_path'] != None, conf['db_path'],
                conf['db_update'], conf['db_name'], conf['omit'], conf['encode']).start()

    def get_target_attribute(self, attr, target=None):
        if target == None:
            logging.error('target not defined')
            sys.exit(0)

        if isinstance(target, dict):
            if attr not in target:
                logging.error('target contains no facts')
                sys.exit(0)
            result = target[attr]
        elif isinstance(target, object):
            if not hasattr(target, attr):
                logging.error('target contains no facts')
                sys.exit(0)
            result = getattr(target, attr)
        else:
            logging.error('invalid target')
            sys.exit(0)
        return result

    def decode(self, ir, *, format=CODE, target=None):
        """ Display the text or return the ast node of the node with id.

        Keyword-only arguments:
        - internal/format/target: output target, takes the following values:
            - CODE: default, return the program corresponding to the ast node in string 
            - AST:  returns the ast node itself
        - target/target:  the target to find the node.
            By default, target refers to the last used target.
        """
        valueDict = self.get_target_attribute('ValueDict', target)
        if ir not in valueDict:
            logging.warning('ir not exist in target')
            return None

        if format == AST:
            return valueDict[ir]
        elif format == CODE:
            node = valueDict[ir]
            if isinstance(node, ast.AST):
                #or (isinstance(node, type) and issubclass(node, ast.AST)):
                return to_source(node)
            elif isinstance(node, tuple):
                return '\n\n\n'.join(to_source(x) for x in node)
            else: return node
        else:
            logging.error('invalid format, accept only AST and CODE')
            sys.exit(0)

    def encode(self, value, *, target=None):
        """ Return the internal representation of a literal value. The value must be presented in the original program
        """
        valueIDDict = self.get_target_attribute('ValueIDDict', target)
        if value not in valueIDDict:
            logging.warning('value not exist in target')
            return None
        return valueIDDict[value]
