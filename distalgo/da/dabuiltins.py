import functools, operator

def prod(arg, start=1):
	""" multiply all the element in arg with a start value.
		arg should be a sequence """
	return start*functools.reduce(operator.mul, arg)

# aggregations
def sumof(arg):
	return sum(arg)

def prodof(arg):
	return prod(arg)

def lenof(arg):
	return len(arg)

def countof(arg):
	return len(arg)

def minof(arg):
	return min(arg)

def maxof(arg):
	return max(arg)

# comprehensions, currently not use these as builtins but keywords
def setof(arg):
	return arg

def listof(arg):
	return arg

def dictof(arg):
	return arg

def tupleof(arg):
	return tuple(arg)