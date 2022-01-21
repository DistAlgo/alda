import pickle
import numpy

m =  {
  'AddUser': 'AddUser',
  'AddRole': 'AddRole',
  'AddUR': 'AssignUser',
  'AddInheritance': 'AddInheritance',
  'AuthorizedUsers': 'AuthorizedUsers',
  'DeleteUser': 'DeleteUser',
  'DeleteRole': 'DeleteRole',
  'DeleteUR': 'DeassignUser',
  'DeleteInheritance': 'DeleteInheritance'
}
for size in range(50,550,50):
  workload = pickle.load(open(f'../../hrbac/input/hrbacSequence_r500_q50_auth{size}','rb'))
  wl = []
  for kind, l in workload:
    wl += [(m[kind],el) for el in l]
  
  pickle.dump([f'self.{kind}{el}' for kind,el in wl], open(f'../input/workload_fixednp_{size}','wb'))
  pickle.dump([f'print(self.{kind}{el})' if kind == 'AuthorizedUsers' else f'self.{kind}{el}' for kind,el in wl], open(f'../input/workload_fixed_{size}','wb'))

  while True:
    wl = numpy.asarray(wl, dtype=object)
    numpy.random.shuffle(wl)
    users = set(range(5000))
    roles = set(range(500))
    ur = pickle.load(open(f'../input/UR_500','rb'))
    rh = pickle.load(open(f'../input/RH_500','rb'))
    badpermutation = False
    for kind, el in wl:
      if kind == 'AddRole':
        roles.add(el[0])
      elif kind == 'DeleteRole':
        if el[0] not in roles:
          badpermutation = True 
          break
        roles.remove(el[0])
      elif kind == 'AuthorizedUsers':
        if el[0] not in roles:
          badpermutation = True
          break
      elif kind == 'AddUser':
        users.add(el[0])
      elif kind == 'DeleteUser':
        if el[0] not in users:
          badpermutation = True 
          break
        users.remove(el[0])
      elif kind == 'AssignUser':
        if el[0] not in users or el[1] not in roles:
          badpermutation = True
          break
        ur.add((el[0],el[1]))
      elif kind == 'DeassignUser':
        if el[0] not in users or el[1] not in roles or el not in ur:
          badpermutation = True
          break
        ur.remove((el[0],el[1]))
      elif kind == 'AddInheritance':
        if el[0] not in roles or el[1] not in roles:
          badpermutation = True
          break
        rh.add((el[0],el[1]))
      elif kind == 'DeleteInheritance':
        if el[0] not in roles or el[1] not in roles or el not in rh:
          badpermutation = True
          break
        rh.remove((el[0],el[1]))

    if badpermutation:
      continue
    else:
      pickle.dump([f'self.{kind}{el}' for kind,el in wl], open(f'../input/workload_randomnp_{size}','wb'))
      pickle.dump([f'print(self.{kind}{el})' if kind == 'AuthorizedUsers' else f'{kind}{el}' for kind,el in wl], open(f'../input/workload_random_{size}','wb'))
      break
