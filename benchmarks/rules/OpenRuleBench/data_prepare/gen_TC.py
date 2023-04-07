from gen import *

filenamePrefix = "tc_d1000_par"
D = Domain(1, 1000)
sizes = range(10000, 100001, 10000)
for size in sizes:
    R = Relation("par", D, D)
    R.Set_Rel_Size(size)
    DB = Database("")
    DB.Add_Relations(R)
    DB.Generate()
    DB.SavePrologGraph(['xsb'], filenamePrefix + str(size))
