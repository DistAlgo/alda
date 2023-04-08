import sys
from ps import ps, AST, CODE
from pprint import pprint
import logging.config
logging.config.fileConfig('logging.conf')
# logger = logging.getLogger()

if __name__ == '__main__':
    filename = '/Users/phd/Downloads/numpy' if len(sys.argv) < 2 else sys.argv[1]
    output = dict()
    ps.read(source=filename, target=output, encode=False, db_update=True)
    pprint(output.keys())
    pprint(ps.decode(180, format=AST, target=output))
    pprint(ps.decode(180, format=CODE, target=output))
    # pa.decode(180)
