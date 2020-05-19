# Compiler package for Distalgo
from .. import common
if common.get_runtime_option('rule', default=False):
	from .query import query
else:
	def query(): pass

__all__ = ['query']
