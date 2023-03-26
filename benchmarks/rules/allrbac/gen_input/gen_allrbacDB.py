""" allRBAC database and query generation

database: users, roles, ops, objs, perms, ur, rh, pr

constraints: 
	1. num_user = 10*num_roles
	2. num_UR = 11*num_role
	3. num_RH = 1.1*num_role
	4* num_ops = 5
	5* num_objs = int(num_perms/num_ops)
	6* at least one user has >= 10 roles
	7. (a,d) and (d,a) can not be simutainously in rh, # as well as the transitive closure of it
		=> only build rh relation with smaller number of roles with higher
	8. maximum height of rh = 5
		=> random sample the set of rh until all the height is <= 5
		=> and when generating the queries, random sample the set of queries until the height is <= 5
	9. when generating PRs with the same number of roles and varies perms,
		the smaller PR is contained within the larger one
"""
import random, os, pickle, math, sys
from copy import deepcopy

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

def gen_db_pr(num_roles, num_perms):
	ROLES = set(range(num_roles))
	USERS = set(range(10*num_roles))
	num_UR = 11*num_roles
	num_RH = int(1.1*num_roles)

	allUR = {(u,r) for u in USERS for r in ROLES}
	greater10User = random.choice(list(USERS))
	numRole = random.randint(10, max(20, num_roles))
	greater10UR = set(random.sample({(u,r) for u,r in allUR if u == greater10User}, numRole))
	UR = set(random.sample(allUR - greater10UR, num_UR - numRole)) | greater10UR

	allRH = {(acs, desc) for acs in ROLES for desc in ROLES if acs < desc}
	while True:
		RH = set(random.sample(allRH, num_RH))
		if get_max_depth(RH) == 5:
			break
	write_graph('allUR_%s' % num_roles, UR)
	write_graph('allRH_%s' % num_roles, RH)

	num_ops = 5
	OPS = set(range(num_ops))
	PR = set()
	for p in sorted(num_perms):
		num_objs = int(p/num_ops)
		OBJS = set(range(num_objs))
		PERMS = [(op, obj) for op in OPS for obj in OBJS]
		num_PR = int(math.sqrt(p*num_roles))
		allPR = {(pm, r) for pm in PERMS for r in ROLES} - PR
		PR = set(random.sample(allPR, num_PR - len(PR))) | PR
		write_graph('PR_r%s_p%s' % (num_roles, p), PR)

def gen_db_role(num_roles, num_perms):
	num_ops = 5
	OPS = set(range(num_ops))
	num_objs = int(num_perms/num_ops)
	OBJS = set(range(num_objs))
	PERMS = [(op, obj) for op in OPS for obj in OBJS]
	PR = set()
	UR = set()
	RH = set()
	depthDict = dict()

	num_roles = sorted(num_roles)
	allUR = {(u,r) for u in set(range(10*num_roles[0])) for r in set(range(num_roles[0]))}
	greater10User = random.choice(list(set(range(10*num_roles[0]))))
	numRole = random.randint(10, max(20, num_roles[0]))
	greater10UR = set(random.sample({(u,r) for u,r in allUR if u == greater10User}, numRole))
	
	for r in num_roles:
		print('number of role:',r)
		ROLES = set(range(r))
		USERS = set(range(10*r))
		num_UR = 11*r
		num_RH = int(1.1*r)

		allUR = {(u,rl) for u in USERS for rl in ROLES}
		UR = set(random.sample(allUR - greater10UR - UR, num_UR - numRole - len(UR))) | greater10UR | UR
		write_graph('allUR_%s' % r, UR)
		
		num_PR = int(math.sqrt(num_perms*r))
		allPR = {(p, rl) for p in PERMS for rl in ROLES} - PR
		PR = set(random.sample(allPR, num_PR - len(PR))) | PR
		write_graph('PR_r%s_p%s' % (r, num_perms), PR)

		allRH = {(acs, desc) for acs in ROLES for desc in ROLES if acs < desc}
		if r is num_roles[0]:
			while True:
				RH = set(random.sample(allRH, num_RH))
				if get_max_depth(RH) == 5:
					break
		else:
			total = num_RH - len(RH)
			while total > 0:
				asc, desc = random.choice(list(allRH - RH))
				if get_max_depth(RH | {(asc, desc)}) == 5:
					RH.add((asc, desc))
					total -= 1
				allRH -= {(asc, desc)}

		write_graph('allRH_%s' % r, RH)


if __name__ == "__main__":
	# generate database: UR, RH and PR
	gen_db_pr(500, range(100, 3100, 100))
	gen_db_role([100, 200, 300, 400, 600, 700, 800, 900, 1000], 1000)

