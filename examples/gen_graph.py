from gen import *
import random
from pprint import pprint

import sys
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
  





if __name__ == "__main__":

  numr = 900

  USER,ROLE,UR,HR = gen_user_role(10*numr,numr,11*numr,int(1.1*numr),10,5)

  # USER,ROLE,UR,HR = gen_user_role(10*numr,numr,11*numr,int(1.1*numr),int(0.1*numr),int(0.05*numr))
  # USER,ROLE,UR,HR = gen_user_role(100,10,110,11,2,2)
  # pprint(USER)
  # pprint(ROLE)
  # pprint(UR)
  # pprint(HR)]
  # fout = open('URauth.py','w')
  # fout.write('{')
  # for u in UR:
  #   fout.write("('auth',("+str(u[0])+','+str(u[1])+")),")
  # fout.write('}')
  # fout.close()

  fout = open('./input/UR_'+str(numr)+'.py','w')
  fout.write('{')
  for u in UR:
    fout.write("("+str(u[0])+','+str(u[1])+"),")
  fout.write('}')
  fout.close()

  # fout = open('HRedge.py','w')
  # fout.write('{')
  # for r in HR:
  #   fout.write("('edge',("+str(r[0])+','+str(r[1])+")),")
  # fout.write('}')
  # fout.close()

  fout = open('./input/HR_'+str(numr)+'.py','w')
  fout.write('{')
  for r in HR:
    fout.write("("+str(r[0])+','+str(r[1])+"),")
  fout.write('}')
  fout.close()






