from gen import *
import os

def gen_graph(v,e,indir):
	"""
	generate a graph of v vertices and e edges
	and write to a file
	"""

	# Domain definitions
	#	 DomainVar = Domain(start, size)
	D1 = Domain(1, v)
	
	# Relation Definitions
	#	 RelVar = Relation("Name", D1, D2, ..., Dn)
	R1 = Relation("edge", D1, D1)
	
	# Constraints
	#	 RelVar.Set_Rel_Size(Number)
	#	 RelVar.Set_Attr_Sizes(N1, N2, ..., Nn)
	#	 RelVar.Set_Attr_Size(AttrPos, Number)
	#	 RelVar.Set_Attr_Size(AttrPos, 0)
	#	 RelVar.DefaultAttrSizes()
	#	 RelVar.Set_Max_Constr4(Attr1, Attr2, Number)
	#	 R1.Remove_Constr4(Attr1, Attr2, Number)
	#	 R1.Remove_All_Constr4()
	R1.Set_Rel_Size(e)
	#R1.Set_Attr_Sizes(2, 4)
	#R1.Set_Attr_Size(1, v*6/7)
	#R1.Set_Attr_Size(2, v*6/7)
	#R1.Set_Max_Constr4(1, 2, 10)
	#R1.Remove_Constr4(1, 2, 2)
	
	# Database definitions
	#	 DBVar = Database(Name)
	#	 DBVar.AddRelations(R1, R2, ..., Rn)
	DB1 = Database("testDB")
	DB1.Add_Relations(R1)
	
	# Database generation
	#	 DBVar.Generate()	 # equivalent to the following
	#		 R1.Generate() R2.Generate() ... Rn.Generate()
	DB1.Generate()
	
	# Statistics
	R1.Distr_Constr4()
	R1.Avg_Constr4()
	R1.Max_Constr4()
	R1.Min_Constr4()
	
	
	DB1.SaveGraph(os.path.join(indir,"v"+str(v)+"e"+str(e)))


if __name__ == "__main__":
	d1 = [(int(e/2),e) for e in range(10,110,10)]
	d2 = [(int(e/2),e) for e in range(100,1100,100)]
	if not os.path.exists('input'):
		os.mkdir('input')
	for (v,e) in d1+d2:
		gen_graph(v,e,'input')
