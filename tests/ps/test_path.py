import sys
from ps import ps, AST
from pprint import pprint
import logging.config
logging.config.fileConfig('logging.conf')
# logger = logging.getLogger()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(0)
    filename = '/Users/phd/Downloads/numpy' if len(sys.argv) < 2 else sys.argv[1]
    output = dict()
    ps.read(filename, target=output)
    pprint(output.keys())
    pprint(ps.decode(180, format=AST))
    ps.decode(180)
