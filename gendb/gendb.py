# Constraints:
# 1st - dom size	   number of elements in "dom"
# 2nd - rel size	   number of tuples in "rel"
# 3rd - rel.attr size	   number of elements for "attr" of "rel"
# 4th - rel.attr2/attr1 size	number of elements for "attr2" per "attr1" of "rel"

import random, sys, copy, time, pickle
from isprime import *
random.seed()

# --------------------------------------------------------------------------------------------

class Database:
# ======================================================================================== #			
# ------------ Initialization
	def __init__(self, _name):
		self.lRelations = []	# Container to store relations
		self.name = _name
    	
# ======================================================================================== #			
# ------------ saves generated tuples to files in all formats, if fileName is not specified - it's database name
	def SaveAll(self, _fileName = ""):
		self.SavePrologGraph(_fileName)
		self.SaveAptsGraph(_fileName)
		self.SavePattonGraph(_fileName)
		self.SaveLiuPyGraph(_fileName)
		self.SaveStollerCGraph(_fileName)
		self.SavePickle(_fileName)

# ======================================================================================== #			
# ------------ saves generated tuples to a file in PrologGraph format
	def SavePrologGraph(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "Prolog.P"
		fout = open(_fileName, 'w')
		for _relation in self.lRelations:
			for _tuple in _relation.rel_content:
				fout.write(_relation.name + str(tuple(_tuple)).replace(" ", "") + ".\n")
		fout.close()
		print self.name, "- Saving Database in PrologGraph format - to file:", _fileName

# ======================================================================================== #			
# ------------ saves generated tuples to a file	in AptsGraph format
	def SaveAptsGraph(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "Apts"
		fout = open(_fileName, 'w')
		for _relation in self.lRelations:
			fout.write(_relation.name + "{")
			for _tuple in _relation.rel_content[:-1]:
				fout.write(str(_tuple).replace(" ", "") + ",")
			fout.write(str(_relation.rel_content[-1]).replace(" ", "")+ "}\n")
		fout.close()
		print self.name, "- Saving Database in AptsGraph format - to file:", _fileName

# ======================================================================================== #			
# ------------ saves generated tuples to a file in PattonGraph format
	def SavePattonGraph(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "PattonGraph"
		fout = open(_fileName, 'w')
		for _relation in self.lRelations:
			fout.write(_relation.name + "{")
			for _tuple in _relation.rel_content[:-1]:
				fout.write(str(tuple(_tuple)).replace(" ", "") + ",")
			fout.write(str(tuple(_relation.rel_content[-1])).replace(" ", "")+ "}\n")
		fout.close()
		print self.name, "- Saving Database in PattonGraph format - to file:", _fileName

# ======================================================================================== #
	def SaveLiuPyGraph(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "LiuPy.py"
		fout = open(_fileName, 'w')
		fout.write("givenFacts = [")
		for _relation in self.lRelations:
			for _tuple in _relation.rel_content:
				fout.write("('"+_relation.name+"'," + str(tuple(_tuple)).replace(" ", "") + "),")
		fout.write("]")
		fout.close()
		print self.name, "- Saving Database in LiuP(yGraph format - to file:", _fileName

# ======================================================================================== #			
# ------------ saves generated tuples to a file in StollerCGraph format
	def SaveStollerCGraph(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "StollerC"
		fout = open(_fileName, 'w')
		for _relation in self.lRelations:
			fout.write("(" + _relation.name + ")\n")
			for _tuple in _relation.rel_content:
				fout.write(str(tuple(_tuple)).replace(" ", "") + "\n")
			fout.write("()\n")
		fout.close()
		print self.name, "- Saving Database in StollerCGraph format - to file:", _fileName

# ======================================================================================== #			
# ------------  Saves generated tuples to a Pickle file
	def SavePickle(self, _fileName = ""):
		if _fileName == "":
			_fileName = self.name
		_fileName += "Pickle"
		fout = open(_fileName, 'w')
		_pickle = pickle.Pickler(fout)
		_pickle.dump(self.lRelations)
		print self.name, "- Saving Database in a Picke format - to file:", _fileName

# ======================================================================================== #			
# ------------  loads generated tuples from a Pickle file    	
	def LoadPickle(self, _fileName):
		fin = open(_fileName, 'r')
		_pickle = pickle.Unpickler(fin)
		self.lRelations = _pickle.load()
		print self.name, "- Loading Saved Database from a Pickle format file:", _fileName

# ======================================================================================== #			
# ------------ Invokes Generate() method of all  relations in the database
	def Generate(self):
		print "Generating database", self.name
		for _relation in self.lRelations:
			_relation.Generate()

# ======================================================================================== #			
# ------------ Adds relations in the database
	def Add_Relations(self, *_relations):
		for _relation in _relations:
			if _relation not in self.lRelations:
				self.lRelations += [_relation]
				print "Relation:", _relation.name, "has been added to database:", self.name
			else:
				print "FYI - Add_Relations:", _relation.name, "already exists in database:", self.name


# ======================================================================================== #			
# --------------------------------------------------------------------------------------------
# ======================================================================================== #			

class Relation:

# ======================================================================================== #			
# ------------ Initialization
	def __init__(self, _name, *_doms):
		self.name = _name
		self.doms_def = _doms
		self.rel_content = []
		self.doms_content = []
		self.attr_num = len(_doms)
		self.RANGE_ATTR_NUM = range(self.attr_num)
		self.range_len_4constr = [] # number of 4th constraints
		self.attr_sizes = [] 	# 3rd constraint
		self.primed_attr_sizes = []
		self.def_4constr = []	# 4th constraint definitions
		self.data_4constr = []	# 4th constraint tracking data 
		self.size = 1		# 2nd constraint
		self.maxSize = 0	# 2nd constraint

		self.reflexive = 1	# the graph can be reflexive

		for _dom in _doms:
			self.size *= _dom.size # Setting 2nd constraint to maximum possible number of tuples
			self.attr_sizes += [_dom.size] # setting 3rd constraint to none
			self.primed_attr_sizes += [_dom.size]

		print "Relation named", "'" + self.name + "'", "has been created..."
		if self.attr_sizes == []:
			self.size = 0
			print "FYI: Initialization of", self.name, "- It is an empty relation..."
		print self.name, "- Default attribute sizes (Domain sizes) are:", self.attr_sizes
		print self.name, "- Default relation size is set to:", self.size

# ======================================================================================== #			
# ------------ Prohibits reflexivity in the graph if set to 0, default: 1 
	def Set_Reflexive(self, _reflex):
		self.reflexive = _reflex
		print self.reflexive

# ======================================================================================== #			
# ------------ Creates domain contents based on its specifications
	def CreateDomainContent(self):
		self.doms_content = []
		for _dom in self.doms_def:
			self.doms_content += [range(_dom.domainStart, _dom.domainStart + _dom.size)] # create domains

# ======================================================================================== #			
# ------------ Set 2nd constraint - rel size	   number of tuples in "rel"
     	def Set_Rel_Size(self, _size):
     		self.size = _size
		print self.name, "- 2nd constraint (Relation Size) has been set to:", self.size 

# ======================================================================================== #			
# ------------ Set 3rd constraint to the attribute at _pos - if size is 0, restore the default
# 3rd - rel.attr size	   number of elements for "attr" of "rel"
     	def Set_Attr_Size(self, _pos, _size):
	# Check parameters
		if _pos < 1 or _pos > self.attr_num:
			print "Error-Set_Attr_Size():", self.name, "- Invalid attribute number is specified!"
			sys.exit()

		_pos -= 1

	# check 3rd vs. 1st constraints here because 1st constraint is constant
	 	if _size > self.doms_def[_pos].size:
				print "Error-Set_Attr_Size():", self.name, "- Size of an attribute cannot exceed the domain size!"
				sys.exit()

		if _size == 0: # resore the default
			_size = self.doms_def[_pos].size

	# set 3rd constraint
		self.attr_sizes[_pos] = _size
		print self.name, "- 3rd constraint (attr sizes) has been set to: ", self.attr_sizes 

# ======================================================================================== #			
# ------------ Set 3rd constraints to all - if any size is 0, leave it unchanged
     	def Set_Attr_Sizes(self, *_sizes):
	# Check parameters
		if len(_sizes) != self.attr_num:
			print "Error-Set_Attr_Sizes():", self.name, "\nNumber of arguments has to be equal to the number of attributes in the Relation!"
			sys.exit()

	# check 3rd vs. 1st constraints here because 1st constraint is constant
		for _size, _dom in zip(_sizes, self.doms_def):
		 	if _size > _dom.size:
				print "Error-Set_Attr_Sizes():", self.name, "- Size of an attribute exceeds the domain size!"
				sys.exit()

	# set 3rd constraint
		for i in self.RANGE_ATTR_NUM:
			if _sizes[i] != 0: # if any size is 0, leave it unchanged
				self.attr_sizes[i] = _sizes[i]
			
		print self.name, "- 3rd constraint (attr sizes) has been set to: ", self.attr_sizes 

# ======================================================================================== #			
# ------------ Restores default attribute sizes (Domain sizes)
	def DefaultAttrSizes(self):
		for i in self.RANGE_ATTR_NUM:
			self.attr_sizes[i] = self.doms_def[i].size

# ======================================================================================== #			
# ------------ Set 4th constraint - rel.attr2/attr1 size	number of elements for "attr2" per "attr1" of "rel"
     	def Set_Max_Constr4(self, _pos1, _pos2, _num):
	# Check parameters
		if _pos1 == _pos2:
			print "Error: Set_Max_Constr4():", self.name, "- attr1 has to be different from attr2!"
			sys.exit()
		if _pos1 < 1 or _pos1 > self.attr_num or _pos2 < 1 or _pos2 > self.attr_num:
			print "Set_Max_Constr4():", self.name, "- Invalid attribute number is specified!"
			sys.exit()
		if _num > self.doms_def[_pos2-1].size:
			print "Set_Max_Constr4():", self.name, "- The number of unique elements in an attribute cannot exceed the domain size for that attribute!"
			sys.exit()

		print self.name, "- Adding 4th constraint:"
		print "	For an element in attr", _pos1, "produce a max of:", _num, "unique elements in attr", _pos2

		if [_pos1-1, _pos2-1, _num] in self.def_4constr:
			print "FYI: Set_Max_Constr4() in", self.name, "- This constraint has already been set"
			return

		for i in self.range_len_4constr: # override constraint if exists
			if self.def_4constr[i][0] == _pos1 - 1 and self.def_4constr[i][1] == _pos2 - 1:
				self.def_4constr.pop(i)
				self.data_4constr.pop(i)
				print "FYI: Set_Max_Constr4() in", self.name, "- Overriding constraint"
				break

		self.def_4constr += [[_pos1-1, _pos2-1, _num]]
		self.data_4constr += [{}]
		self.range_len_4constr = range(len(self.def_4constr))

# ======================================================================================== #			
# ------------- removes a particular instance of 4th constraint
	def Remove_Constr4(self, _pos1, _pos2, _num):
		if [_pos1-1, _pos2-1, _num] in self.def_4constr:
			self.def_4constr.remove([_pos1-1, _pos2-1, _num])
			print self.name, "- An instance of 4th constraint has been successfully removed:"
			print "	For an element in attr", _pos1, "produce a max of:", _num, "unique elements in attr", _pos2
			self.range_len_4constr.pop()
		else:
			print "FYI: Remove_Constr4() in", self.name, "- Can't remove specified 4th constraint - it has not been set..."

# ======================================================================================== #			
# ------------- removes all instances of 4th constraint
	def Remove_All_Constr4(self):
		for i in self.range_len_4constr:
			self.def_4constr.pop(i)
			self.data_4constr.pop(i)
		self.range_len_4constr = []
		print self.name, "- All instances of the 4th constraint have been removed..."


# ======================================================================================== #			
# ------------- finds maximums for all instances of 4th constraint
	def Max_Constr4(self):
		for i in self.range_len_4constr:
			print self.name, "- Maximum for the 4th constraint:"
			print "For an element in attr1 =", self.def_4constr[i][0] + 1, "produce a max of:", \
				self.def_4constr[i][2], "unique elements in attr2 =", self.def_4constr[i][1] + 1
			_Max = 0
			for _attr1, _lattr2 in self.data_4constr[i].iteritems():
				if _Max < len(_lattr2):
					_Max = len(_lattr2)
			print "Maximum of len(Attr2) per N Attr1 is:", _Max

# ======================================================================================== #			
# ------------- finds minimums for all instances of 4th constraint
	def Min_Constr4(self):
		for i in self.range_len_4constr:
			print self.name, "- Minimum for the 4th constraint:"
			print "For an element in attr1 =", self.def_4constr[i][0] + 1, "produce a max of:", \
				self.def_4constr[i][2], "unique elements in attr2 =", self.def_4constr[i][1] + 1
			_Min = self.def_4constr[i][2]
			for _attr1, _lattr2 in self.data_4constr[i].iteritems():
				if _Min > len(_lattr2):
					_Min = len(_lattr2)
			print "Minimum of len(Attr2) per N Attr1 is:", _Min


# ======================================================================================== #			
# ------------- prints out distribution for all instances of 4th constraint
	def Distr_Constr4(self):
		for i in self.range_len_4constr:
			print self.name, "- Distribution for the 4th constraint:"
			print "For an element in attr1 =", self.def_4constr[i][0] + 1, "produce a max of:", \
				self.def_4constr[i][2], "unique elements in attr2 =", self.def_4constr[i][1] + 1
			dDistr = {}
			for j in xrange(1, self.def_4constr[i][2] + 1): # initialize all values in distribution to 0
				dDistr[j] = 0
			for _attr1, _lattr2 in self.data_4constr[i].iteritems():
				dDistr[len(_lattr2)] += 1
			print "len(Attr2) per N Attr1"
			for _attr2, _attr1 in dDistr.iteritems():
				print _attr2,"	", _attr1

# ======================================================================================== #			
# ------------- prints out average for all instances of 4th constraint
	def Avg_Constr4(self):
		for i in self.range_len_4constr:
			numerator = 0.0
			denominator = 0.0
			print self.name, "- Average for the 4th constraint:"
			print "For an element in attr1 =", self.def_4constr[i][0] + 1, "produce a max of:", \
				self.def_4constr[i][2], "unique elements in attr2 =", self.def_4constr[i][1] + 1
			dDistr = {}
			for j in xrange(1, self.def_4constr[i][2] + 1): # initialize all values in distribution to 0
				dDistr[j] = 0
			for _attr1, _lattr2 in self.data_4constr[i].iteritems():
				dDistr[len(_lattr2)] += 1
			for _attr2, _attr1 in dDistr.iteritems():
				numerator += _attr1 * _attr2
				denominator += _attr1

			print "On average there are", numerator/denominator, "Attr2 per Attr1"
		
# ======================================================================================== #			
# ------------ check constraints before generation
     	def Check_Constraints(self):

	# estimating number of tuples - calculating adjustment of 3rd constraint by the 4th constraint
		_costr_attr_sizes = copy.copy(self.attr_sizes)
		for i in self.range_len_4constr:
			_pos2 = self.def_4constr[i][1]
			_num  = self.def_4constr[i][2]
			if _num < _costr_attr_sizes[_pos2]:
				_costr_attr_sizes[_pos2] = _num

	# Calculating maximum possible relations based on attribute sizes and constraints
		max_poss_rel = 1
		for i in self.RANGE_ATTR_NUM: 
			max_poss_rel *= _costr_attr_sizes[i]

		print self.name, "- Estimated number of possible tuples is:", max_poss_rel

	# check 3rd vs. 2nd constraints
		self.maxSize = self.size
		if self.maxSize >= max_poss_rel: 
			self.maxSize = max_poss_rel
			print "FYI-Check_Constraints(): in", self.name, "- relation will have all possible tuples!"

			
# ======================================================================================== #			
# ------------ preprocess domains for generation
	def Preprocess(self):
	# shorten domains according to 3rd constraint by picking the specified number of random integers from domain
		dPrimeDoms = {}
		random.jumpahead(1) 
		for i in self.RANGE_ATTR_NUM:
			if self.attr_sizes[i] != self.doms_def[i].size:
				self.doms_content[i] = random.sample(self.doms_content[i], self.attr_sizes[i])
		# create a dictionary linking attribute sizes and domains
			while(dPrimeDoms.has_key(self.primed_attr_sizes[i])):
				self.primed_attr_sizes[i] += 1 # avoid similar keys, the new size will never exceed the primed size
			dPrimeDoms[self.primed_attr_sizes[i]] = self.doms_content[i]

	# starting with the smallest domain extend it to the closest larger prime number, disallowing same sizes
		self.primed_attr_sizes.sort()
		min_prime = 0
		for i in self.primed_attr_sizes:
			if i < min_prime: # make sure we don't get equal primed sizes
				prime = self.FindPrime(min_prime)
			else:
				prime = self.FindPrime(i)
			min_prime = prime + 1
			while len(dPrimeDoms[i]) < prime: # extend the domain with 0's
				dPrimeDoms[i] += [0]
			random.shuffle(dPrimeDoms[i])

	# reconstruct self.primed_attr_sizes
		self.primed_attr_sizes = []
		for _dom in self.doms_content:
			self.primed_attr_sizes += [len(_dom)]

#		print self.name, "Primed attribute sizes after preprocessing are:", self.primed_attr_sizes 

# ======================================================================================== #			
# ------------ dynamically checks tuple against the 4th constraint
	def Check_4Constr(self, _tuple):
	# check the 4th constraint
		for i in self.range_len_4constr:
			_pos1 = self.def_4constr[i][0]
			_pos2 = self.def_4constr[i][1]
			_num  = self.def_4constr[i][2]
			_dict = self.data_4constr[i]
			if _dict.has_key(_tuple[_pos1]):
				if len(_dict[_tuple[_pos1]]) == _num and (_tuple[_pos2] not in _dict[_tuple[_pos1]]):
#					print "discard", _tuple
					return 0
				
	# update constraint data
		for i in self.range_len_4constr:
			_pos1 = self.def_4constr[i][0]
			_pos2 = self.def_4constr[i][1]
			_num  = self.def_4constr[i][2]
			_dict = self.data_4constr[i]
			if _dict.has_key(_tuple[_pos1]):
				if _tuple[_pos2] not in _dict[_tuple[_pos1]]:
					_dict[_tuple[_pos1]] += [_tuple[_pos2]]
			else:
				_dict[_tuple[_pos1]] = [_tuple[_pos2]]
		return 1
			
# ======================================================================================== #			
# ------------ finds a larger or equal prime number 
     	def FindPrime(self, x):
     		while(not isPrime(x)):
     			x += 1
		return x

# ======================================================================================== #			
# ------------ generates random tuples
     	def Generate(self):

		self.CreateDomainContent() # do this before preprocess
	     	self.Check_Constraints() # do this before preprocessing because some structures change in preprocessing
		self.Preprocess()
		self.rel_content = []
		discardReflexive = 0
		maxNum = 1
		i = 0
		zero = 0
		startTime = time.time()
		intermTime = startTime
		for _size in self.primed_attr_sizes:
			maxNum *= _size # Calculate the maximum possible number of tuples

		print self.name, "- Starting generation phase...be patient..."
		while len(self.rel_content) < self.maxSize and i < maxNum:
			_tuple = []
			for j in self.RANGE_ATTR_NUM:
				_tuple += [self.doms_content[j][i % self.primed_attr_sizes[j]]]
			i += 1

			# this section controls whether the graph is reflexive or not based in Set_Reflexive setting
			if self.reflexive == 0:
				discardReflexive = 1
				for j in range(self.attr_num - 1):
					if _tuple[j] != _tuple[j+1]:
						discardReflexive = 0
						break
			
			if 0 not in _tuple and discardReflexive == 0: # test for ZERO
				if self.Check_4Constr(_tuple) != 0:
					self.rel_content += [_tuple]

				if len(self.rel_content) % 10000 == 0:
					print self.name, "- Tuples generated so far:", len(self.rel_content), "Time:" , time.time() - intermTime
					intermTime = time.time()
			else:
#				print "discard", _tuple
				zero += 1

		print self.name, "- Total time to generate:", time.time() - startTime, "sec"
		print self.name, "- Number of unique tuples generated:", len(self.rel_content)
#		print self.name, "- Zero tuples discarded:", zero
#		print self.rel_content

		"""
		
		for i in self.range_len_4constr:
			print
			print self.def_4constr[i]
			print self.data_4constr[i]
		"""
# ======================================================================================== #			
# --------------------------------------------------------------------------------------------
# ======================================================================================== #			

class Domain:
# ======================================================================================== #			
# ------------ Domain Initialization
	def __init__(self, _domainStart, _size):
		if _domainStart < 1:
			print "Error-Domain Definition: Domains are restricted to integers > 0!"
			sys.exit()
		if _size < 1:
			print "Error-Domain Definition: Domains have to include at least one integer!"
			sys.exit()
		self.size = _size
		self.domainStart = _domainStart
		print "Domain of integers (", _domainStart, "-", _domainStart + _size - 1, ") ( size =", _size, ") has been created"

# --------------------------------------------------------------------------------------------
