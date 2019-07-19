import random
# from pprint import pprint

import sys,os
sys.setrecursionlimit(30000)


def gen_user_role(_u,_r,nu,nr,cu,cr):
  USER = set(range(_u))
  ROLE = set(range(_r))
  UR = set()
  HR = set()

  def depthSearchEnd(r2):
    
    endset = [e for (s,e) in HR if s == r2]
    if len(endset) == 0:
      return 0,set()
    count = []
    afterset = set()
    for e in endset:
      c,s = depthSearchEnd(e)
      count.append(c)
      afterset = afterset.union(s)
    return max(count)+1,afterset
    

  def depthSearchStart(r1):
    startset = [s for (s,e) in HR if e == r1]
    if len(startset) == 0:
      return 0,set()
    count = []
    beforeset = set()
    for s in startset:
      c,_s = depthSearchStart(s)
      count.append(c)
      beforeset = beforeset.union(_s)
    return max(count)+1,beforeset


  startLenDict = {}
  endLenDict = {}
  for i in range(nu):
    while(1):
      user = random.randrange(_u)
      role = random.randrange(_r)
      if not (user,role) in UR:
        if len([(u,r) for (u,r) in UR if u == user]) < cu:
          UR.add((user,role))
          break

  for j in range(nr):
    while(1):
      r1 = random.randrange(_r)
      r2 = random.randrange(_r)
      if r1 != r2 and not (r1,r2) in HR:
        ce,se = depthSearchEnd(r2)
        cs,ss = depthSearchStart(r1)
        if ce+cs < cr and not r1 in se and not r2 in ss:
          HR.add((r1,r2))
          break
      
  return USER,ROLE,UR,HR


def gen_graph(num_role):
  USER,ROLE,UR,HR = gen_user_role(10*num_role,num_role,11*num_role,int(1.1*num_role),10,5)

  fout = open('./input/UR_'+str(num_role)+'.py','w')
  fout.write('{')
  for u in UR:
    fout.write("("+str(u[0])+','+str(u[1])+"),")
  fout.write('}')
  fout.close()


  fout = open('./input/HR_'+str(num_role)+'.py','w')
  fout.write('{')
  for r in HR:
    fout.write("("+str(r[0])+','+str(r[1])+"),")
  fout.write('}')
  fout.close()

  return UR, HR



class genWorkLoad():
  def __init__(self,num_role,num_user,num_query,rh,ur,min_auth_query,max_auth_query,auth_interval):
    self.num_user = num_user
    self.num_role = num_role
    self.num_query = num_query
    self.rh = rh
    self.ur = ur
    self.min_auth_query = min_auth_query
    self.max_auth_query = max_auth_query
    self.auth_interval = auth_interval
    self.users = set(range(num_user))
    self.roles = set(range(num_role))
    
  def gen(self):
    seq = ['AddUser','AddRole','AddUR','AddInheritance','AuthorizedUsers','DeleteUser','DeleteRole','DeleteUR','DeleteInheritance']

    opString = ""
    allfout = {}
    for q in range(self.min_auth_query,self.max_auth_query+1,self.auth_interval):
      fout = open('./input/hrbacSequence_r'+str(self.num_role)+'_q'+str(self.num_query)+'_auth'+str(q)+'.py','w')
      fout.write('[')
      allfout[q] = fout
      
    for op in seq:
      if op == 'AuthorizedUsers':
        s = self.AuthorizedUsers(self.max_auth_query)
        for q in range(self.min_auth_query,self.max_auth_query+1,self.auth_interval):
          opString = '(\''+op+'\','+repr(s[:q])+'),'
          allfout[q].write(opString)
      else:
        s = getattr(self,op)()
        opString = '(\''+op+'\','+repr(s)+'),'
        for _,f in allfout.items():
          f.write(opString)

    for _,f in allfout.items():
      f.write(']')
      f.close()

  def AddUser(self):
    resultSet = set()
    l = len(self.users)
    choice = set(range(l*2+self.num_query)) - self.users
    resultSet = random.sample(choice,self.num_query)
    self.users |= set(resultSet)
    return resultSet

  def DeleteUser(self):
    try:
      resultSet = random.sample(self.users,self.num_query)
      self.users -= set(resultSet)
      UR = list(self.ur)
      for (u,r) in UR:
        if u not in self.users:
          self.ur -= {(u,r)}
      return resultSet
    except Exception as e:
      print('DeleteUser:',e)
      return False

  def AddRole(self):
    resultSet = set()
    l = len(self.roles)
    choice = set(range(l*2+int(self.num_query/10))) - self.roles
    resultSet = random.sample(choice,int(self.num_query/10))
    self.roles |= set(resultSet)
    return resultSet

  def DeleteRole(self):
    try:
      resultSet = random.sample(self.roles,int(self.num_query/10))
      self.roles -= set(resultSet)
      RH = list(self.rh)
      UR = list(self.ur)
      for (r1,r2) in RH:
        if r1 not in self.roles or r2 not in self.roles:
          self.rh -= {(r1,r2)}
      for (u,r) in UR:
        if r not in self.roles:
          self.ur -= {(u,r)}
      return resultSet
    except Exception as e:
      print('DeleteRole:',e)
      return False

  def AddUR(self):
    resultSet = set()
    for i in range(int(self.num_query*1.1)):
      u = random.sample(self.users,1)[0]
      r = random.sample(self.roles,1)[0]
      while((u,r) in self.ur):
        u = random.sample(self.users,1)[0]
        r = random.sample(self.roles,1)[0]
      resultSet.add((u,r))
      self.ur.add((u,r))
    return resultSet

  def DeleteUR(self):
    try:
      resultSet = random.sample(self.ur,int(self.num_query*1.1))
      self.ur -= set(resultSet)
      return resultSet
    except Exception as e:
      print('DeleteUR:',e)
      return False

  def AddInheritance(self):
    resultSet = set()
    for i in range(int(self.num_query*0.11)):
      r1 = random.sample(self.roles,1)[0]
      r2 = random.sample(self.roles,1)[0]
      while((r1,r2) in self.rh or (r2,r1) in self.rh):
        r1 = random.sample(self.roles,1)[0]
        r2 = random.sample(self.roles,1)[0]
      resultSet.add((r1,r2))
      self.rh.add((r1,r2))
    return resultSet

  def DeleteInheritance(self):
    try:
      resultSet = random.sample(self.rh,int(self.num_query*0.11))
      self.rh -= set(resultSet)
      return resultSet
    except Exception as e:
      print('DeleteInheritance:',e)
      return False


  def AuthorizedUsers(self,n):
    try:
      return random.choices(list(self.roles),k=n)
    except Exception as e:
      print('-------->AuthorizedUsers:',len(self.roles))
      return False

  


"""
gen_graph:
5000 users and 500 roles, and randomly generate a user-role assignment UR of size 5500 with a maximum of 10 roles per user
and a role hierarchy RH of size 550 and height 5

genWorkLoad:
operations in each iteration: 
  adding/deleting user (each 50 times), 
  adding/deleting role (each 5 times), 
  adding/deleting UR pair (each 55 times), 
  adding/deleting RH pair (each 5 times), 
  and querying authorized users (n times), for n up to 500 at intervals of 50

measure the running time of the workload for each n.
"""
if __name__ == "__main__":
  if not os.path.exists('input'):
    os.mkdir('input')

  num_role = 500
  num_user = 10*num_role
  num_query = 50

  max_auth_query = 500
  min_auth_query = 50
  auth_interval = 50

  UR, RH = gen_graph(num_role)
  g = genWorkLoad(num_role,num_user,num_query,RH,UR,min_auth_query,max_auth_query,auth_interval)
  g.gen()


  
  


  
  





