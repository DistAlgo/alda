from gen import *
import sys

# get the system List
sysList = []
for arg in sys.argv[1:]:
    sysList.append(arg)

if len(sysList) == 0:
    sys.exit()

# generate date files for tc
filenamePrefix = "tc_d1000_parsize"
D = Domain(1, 1000)
sizes = [50000, 250000, 500000]
for i in range(len(sizes)):
    R = Relation("par", D, D)
    R.Set_Rel_Size(sizes[i])
    DB = Database("testDB")
    DB.Add_Relations(R)
    DB.Generate()
    DB.SavePrologGraph(sysList,filenamePrefix+str(sizes[i]))

D = Domain(1, 2000)
filenamePrefix = "tc_d2000_parsize"
sizes = [500000, 1000000]
for i in range(len(sizes)):
    R = Relation("par", D, D)
    R.Set_Rel_Size(sizes[i])
    DB = Database("testDB")
    DB.Add_Relations(R)
    DB.Generate()
    DB.SavePrologGraph(sysList,filenamePrefix+str(sizes[i]))


# generate date files for sg
D = Domain(1, 500)
filenamePrefix = "sg_d500_parsize"
sizes1 = [5000, 10000, 20000]
sizes2 = [1000, 2000, 4000]
for i in range(len(sizes1)):
    R1 = Relation("par", D, D)
    R2 = Relation("sib", D, D)
    R1.Set_Rel_Size(sizes1[i])
    R2.Set_Rel_Size(sizes2[i])
    DB = Database("testDB")
    DB.Add_Relations(R1)
    DB.Add_Relations(R2)
    DB.Generate()
    DB.SavePrologGraph(sysList,filenamePrefix + str(sizes1[i]) + "_sibsize" + str(sizes2[i]))

D = Domain(1, 1000)
filenamePrefix = "sg_d1000_parsize"
sizes1 = [5000, 10000]
sizes2 = [1000, 2000]
for i in range(len(sizes1)):
    R1 = Relation("par", D, D)
    R2 = Relation("sib", D, D)
    R1.Set_Rel_Size(sizes1[i])
    R2.Set_Rel_Size(sizes2[i])
    DB = Database("testDB")
    DB.Add_Relations(R1)
    DB.Add_Relations(R2)
    DB.Generate()
    DB.SavePrologGraph(sysList,filenamePrefix + str(sizes1[i]) + "_sibsize" + str(sizes2[i]))
