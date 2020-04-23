from da.compiler.parser import *
from da.compiler import parser
from . import constraint_ast as cast

from pprint import pprint
import json


KW_CONSTRAINT = 'constraint'

def gensym(prefix):
	i = 0
	while True:
		i += 1
		yield prefix+str(i)

generator = gensym('obj_')


class Parser(parser.Parser):

	def __init__(self, filename="", options=None, execution_context=None,
				 _package=None, _parent=None):
		super().__init__(filename, options, execution_context,
				 _package, _parent)
		self.current_constraint = None
		self.have_variable = False


	def visit_Name(self,node):
		rt = super().visit_Name(node)
		var = self.current_scope.find_name(node.id)
		if self.current_constraint:
			for i in var._indexes:
				if i[0] == dast.AssignmentCtx:	
					if isinstance(i[1][0], dast.AssignmentStmt):
						# only in this case the Name is a parameter or variable
						if not node.id in self.current_constraint['parameter']:
							self.have_variable = True
							break
		return rt


	def visit_AnnAssign(self,node):
		stmtobj = self.create_stmt(dast.AssignmentStmt, node)
		self.current_context = Assignment(stmtobj,
										  type=self.visit(node.annotation))
		stmtobj.targets = [self.visit(node.target)]
		if node.value is not None:
			self.current_context = Read(stmtobj)
			self.have_variable = False
			stmtobj.value = self.visit(node.value)
			if not self.have_variable:
				for t in stmtobj.targets:
					self.current_constraint['parameter'].add(t.name)
			self.have_variable = False
		self.pop_state()

	def visit_FunctionDef(self,node):
		if node.name == KW_CONSTRAINT:
			self.current_constraint = dict()
			for i in range(len(node.args.args)):
				if node.args.args[i].arg == 'name':
					cname = node.args.defaults[i].s
				if node.args.args[i].arg == 'parameter':
					self.current_constraint['parameter'] = {e.id for e in node.args.defaults[i].elts}
					self.current_constraint['required_parameter'] = {e for e in self.current_constraint['parameter']}
				
			rt =  super().visit_FunctionDef(node)
			if not hasattr(self.program, 'constraint_options'):
				self.program.constraint_options = dict()
			self.program.constraint_options[cname] = self.current_constraint
			self.current_constraint = None
			return rt
		else:
			return super().visit_FunctionDef(node)
		

	def visit_Call(self,node): 
		if isinstance(node.func, Name) and node.func.id == 'query':
			if not hasattr(self.program, 'constraint_info'):
				self.program.constraint_info = set()
			for k in node.keywords:
				if k.arg != 'constraint':
					if isinstance(k.value, Name):
						par = self.current_scope.find_name(k.value.id)
						if par:
							for i in par._indexes:
								if i[0] == dast.AssignmentCtx or i[0] == dast.UpdateCtx:
									# in this case, the argument of the function appears at an assignment/update statement in current scope
									# the assignment of variable need some additional actions 
									# for rules, inspecting variable changes and trigger infer
									# for constraints, need to add a _ = None before each assignment 
									#	in case the assignment uses '_' to pressent empty
									# print(i[1][0])
									self.program.constraint_info.add(i[1][0])
		return super().visit_Call(node)










