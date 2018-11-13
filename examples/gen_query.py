from gen import *
import random
from pprint import pprint
from itertools import permutations

import sys
sys.setrecursionlimit(1500)

numr = 900
numu = 10*numr
numq = 50


interval = 50
maxq = 1000
minq = 50
# q = [50,100,150,200,250,300,350,400,450,500,550,600,650,700,750,800,850,900,950,1000]


def genSep():
	users = set(range(numu))
	roles = set(range(numr))
	rh = eval(open('HR_'+str(numr)+'.py').read())
	ur = eval(open('UR_'+str(numr)+'.py').read())

	addUser = set()
	for i in range(numr):
		r = random.randrange(numu,numu*2)
		while r in addUser:
			r = random.randrange(numu,numu*2)
		addUser.add(r)

	# print('addUser =',addUser)
	fout = open('addUser_'+str(numr)+'.py','w')
	fout.write(repr(addUser))
	fout.close()

	delUser = random.sample(set(users),numr)

	# print('delUser =',delUser)
	fout = open('delUser_'+str(numr)+'.py','w')
	fout.write(repr(delUser))
	fout.close()

	
	addRole = set()
	for i in range(10):
		r = random.randrange(numr,numr*2)
		while r in addRole:
			r = random.randrange(numr,numr*2)
		addRole.add(r)

	# print('addRole =',addRole)
	fout = open('addRole_'+str(numr)+'.py','w')
	fout.write(repr(addRole))
	fout.close()


	delRole = random.sample(set(roles),10)

	# print('delRole =',delRole)
	fout = open('delRole_'+str(numr)+'.py','w')
	fout.write(repr(delRole))
	fout.close()


	addUR = set()
	for i in range(110):
		u = random.randrange(numu)
		r = random.randrange(numr)
		while((u,r) in ur or (u,r) in addUR):
			u = random.randrange(numu)
			r = random.randrange(numr)
		addUR.add((u,r))

	# print('addUR =',addUR)
	fout = open('addUR_'+str(numr)+'.py','w')
	fout.write(repr(addUR))
	fout.close()


	delUR = random.sample(ur,110)

	# print('delUR =',delUR)
	fout = open('delUR_'+str(numr)+'.py','w')
	fout.write(repr(delUR))
	fout.close()


	addInher = set()
	for i in range(11):
		r1 = random.randrange(numr)
		r2 = random.randrange(numr)
		while((r1,r2) in rh or (r1,r2) in addInher):
			r1 = random.randrange(numr)
			r2 = random.randrange(numr)
		addInher.add((r1,r2))

	# print('addInher =',addInher)
	fout = open('addInher_'+str(numr)+'.py','w')
	fout.write(repr(addInher))
	fout.close()


	delInher = random.sample(rh,11)

	# print('delInher =',delInher)
	fout = open('delInher_'+str(numr)+'.py','w')
	fout.write(repr(delInher))
	fout.close()

users = set(range(numu))
roles = set(range(numr))
rh = eval(open('./input/HR_'+str(numr)+'.py').read())
ur = eval(open('./input/UR_'+str(numr)+'.py').read())


def genWorkLoad():
	global numr
	global numu
	global interval
	global numq
	global q

	i = 0
	# l = len(q)
	queries = 0


	def AddUser():
		global users
		resultSet = set()
		l = len(users)
		choice = set(range(l*2+numq)) - users
		# for i in range(numq):
		# 	r = random.sample(choice,1)[0]
		# 	while r in users:
		# 		r = random.sample(choice,1)[0]
		# 	resultSet.add(r)
		# 	users.add(r)
		resultSet = random.sample(choice,numq)
		users |= set(resultSet)
		return resultSet

	def DeleteUser():
		try:
			global users
			global ur
			resultSet = random.sample(users,numq)
			users -= set(resultSet)
			UR = list(ur)
			for (u,r) in UR:
				if u not in users:
					ur -= {(u,r)}
			return resultSet
		except Exception as e:
			print('DeleteUser:',e)
			return False

	def AddRole():
		global roles
		resultSet = set()
		l = len(roles)
		choice = set(range(l*2+int(numq/10))) - roles
		# for i in range(int(numq/10)):
		# 	r = random.sample(choice,1)[0]
		# 	while r in roles:
		# 		r = random.sample(choice,1)[0]
		# 	resultSet.add(r)
		# 	roles.add(r)
		resultSet = random.sample(choice,int(numq/10))
		roles |= set(resultSet)
		return resultSet

	def DeleteRole():
		try:
			global roles
			global rh
			global ur
			resultSet = random.sample(roles,int(numq/10))
			roles -= set(resultSet)
			RH = list(rh)
			UR = list(ur)
			for (r1,r2) in RH:
				if r1 not in roles or r2 not in roles:
					rh -= {(r1,r2)}
			for (u,r) in UR:
				if r not in roles:
					ur -= {(u,r)}
			return resultSet
		except Exception as e:
			print('DeleteRole:',e)
			return False

	def AddUR():
		resultSet = set()
		for i in range(int(numq*1.1)):
			u = random.sample(users,1)[0]
			r = random.sample(roles,1)[0]
			while((u,r) in ur):
				u = random.sample(users,1)[0]
				r = random.sample(roles,1)[0]
			resultSet.add((u,r))
			ur.add((u,r))
		return resultSet

	def DeleteUR():
		try:
			global ur
			resultSet = random.sample(ur,int(numq*1.1))
			ur -= set(resultSet)
			return resultSet
		except Exception as e:
			print('DeleteUR:',e)
			return False

	def AddInheritance():
		resultSet = set()
		for i in range(int(numq*0.11)):
			r1 = random.sample(roles,1)[0]
			r2 = random.sample(roles,1)[0]
			while((r1,r2) in rh or (r2,r1) in rh):
				r1 = random.sample(roles,1)[0]
				r2 = random.sample(roles,1)[0]
			resultSet.add((r1,r2))
			rh.add((r1,r2))
		return resultSet

	def DeleteInheritance():
		try:
			global rh
			resultSet = random.sample(rh,int(numq*0.11))
			rh -= set(resultSet)
			return resultSet
		except Exception as e:
			print('DeleteInheritance:',e)
			return False

	

	def AuthorizedUsers(n):
		try:
			return random.choices(list(roles),k=n)
		except Exception as e:
			print('-------->AuthorizedUsers:',len(roles))
			return False


	
	#gen work load 1
	# operations = {'AddUser','DeleteUser','AddRole','DeleteRole','AddUR','DeleteUR','AddInheritance','DeleteInheritance','AuthorizedUsers'}
	# opString = ""
	# while i < l:
	# 	op = random.sample(operations,1)[0]
	# 	# if op != 'AuthorizedUsers':
	# 	print("op = ", op)
	# 	s = locals()[op]()
	# 	if not s:
	# 		continue

	# 	opString += '(\''+op+'\','+repr(s)+'),'

	# 	if op == 'AuthorizedUsers':
	# 		queries += interval
	# 		if queries == q[i]:
	# 			fout = open('./input/hrbacSequence_r'+str(numr)+'_q'+str(numq)+'_auth'+str(q[i])+'.py','w')
	# 			fout.write('[')
	# 			fout.write(opString)
	# 			fout.write(']')
	# 			fout.close()
	# 			i += 1

	
	# gen work load 2
	operations = ['AddUser','DeleteUser','AddRole','DeleteRole','AddUR','DeleteUR','AddInheritance','DeleteInheritance','AuthorizedUsers']

	# perm = list(permutations(operations))

	opString = ""
	allfout = {}
	for q in range(minq,maxq,interval):
		fout = open('./input/hrbacSequence_r'+str(numr)+'_q'+str(numq)+'_auth'+str(q)+'.py','w')
		fout.write('[')
		allfout[q] = fout
		
	
	# seq = random.choice(perm)
	seq = ['AddUser','AddRole','AddUR','AddInheritance','AuthorizedUsers','DeleteUser','DeleteRole','DeleteUR','DeleteInheritance']
	for op in seq:
		if op == 'AuthorizedUsers':
			s = AuthorizedUsers(maxq)
			for q in range(minq,maxq,interval):
				opString = '(\''+op+'\','+repr(s[:q])+'),'
				allfout[q].write(opString)
		else:
			s = locals()[op]()
			opString = '(\''+op+'\','+repr(s)+'),'
			for _,f in allfout.items():
				f.write(opString)

	for _,f in allfout.items():
		f.write(']')
		f.close()


				










if __name__ == "__main__":
	genWorkLoad()






