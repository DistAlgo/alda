import sys
import ast
from ps import ps
from pprint import pprint
import logging.config
logging.config.fileConfig('logging.conf')
# logger = logging.getLogger()

if __name__ == '__main__':
    path = '/Users/phd/Downloads/numpy/numpy/ctypeslib.py'
    file_content = open(path, encoding='utf8').read()
    pyast = ast.parse(file_content, filename=path)

    output = dict()
    ps.read(source=pyast, scope=output, package='numpy/ctypeslib')
    pprint(output.keys())
