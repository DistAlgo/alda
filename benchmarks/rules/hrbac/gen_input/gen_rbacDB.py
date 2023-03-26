""" HRBAC database generation

database: users, roles, ur relation, rh relation, 

constraints: 
	1. num_user = 10*num_roles
	2. num_UR = 11*num_role
	3. num_RH = 1.1*num_role
	4. each user can have <= 10 roles
	5. (a,d) and (d,a) can not be simutainously in rh, as well as the transitive closure of it
		=> only build rh relation with smaller number of roles with higher
	6. maximum height of rh = 5
		=> random sample the set of rh until all the height is <= 5
		=> and when generating the queries, random sample the set of queries until the height is <= 5
		=> depth first search to get the height
"""
import random, os, pickle

outfolder = '../input'
def write_graph(filename, data):
	""" input: v and e are numbers, data is a set of edges
		output: pickle dump data to file: outfolder/v{v}e{e}
	"""
	pickle.dump(data,open(os.path.join(outfolder, filename), 'wb'))
	open(os.path.join(outfolder, filename+'.py'), 'w').write(repr(data))

def get_max_depth(edges):
	depthDict = dict()
	def max_depth(k):
		if k in depthDict:
			return depthDict[k]
		child = [j for (i,j) in edges if i == k]
		if len(child) == 0:
			depthDict[k] = 0
			return 0
		else:
			depthDict[k] = max([max_depth(c) for c in child])+1
			return depthDict[k]

	vertices = {i for (i,j) in edges}
	for v in vertices:
		max_depth(v)
	return max(depthDict.values())

def gen_db(num_roles):
	USERS = set(range(10*num_roles))
	ROLES = set(range(num_roles))
	num_UR = 11*num_roles
	num_RH = int(1.1*num_roles)
	allUR = {(u,r) for u in USERS for r in ROLES}
	while True:
		UR = set(random.sample(allUR, num_UR))
		roleCount = {u: [r for (u1,r) in UR if u1 == u] for (u,_) in UR}
		if max([len(r) for r in roleCount.values()]) <= 10:
			break
	
	allRH = {(acs, desc) for acs in ROLES for desc in ROLES if acs < desc}
	while True:
		RH = set(random.sample(allRH, num_RH))
		if get_max_depth(RH) == 5:
			break
	write_graph('UR_%s' % num_roles, UR)
	write_graph('RH_%s' % num_roles, RH)

if __name__ == "__main__":
	# generate database: UR and RH
	gen_db(500)

