from elements import Generator, UniformCmds
import random

# base types
class Integer(Generator):
	def __init__(self, lb=-1000, ub=1000):
		super(Generator, self).__init__()
		self.lb = lb
		self.ub = ub
		self.check_always = [0,1,-1]*3
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.check_always.pop()
		return random.randint(self.lb, self.ub)

class Float(Generator):
	def __init__(self, lb=-1000.0, ub=1000.0):
		super(Generator, self).__init__()
		self.lb = lb
		self.ub = ub
	def generate(self):
		return random.uniform(self.lb, self.ub)

class Element(Generator):
	def __init__(self, values):
		super(Generator, self).__init__()
		self.values = values
	def generate(self):
		return random.choice(values)

# structured types
class List(Generator):
	def __init__(self, *elements, **kws):
		super(Generator, self).__init__()
		self.elements = elements
		self.check_always=[[]]*3
		def get_maxlength(maxlength=100): return maxlength
		self.maxlength = get_maxlength(**kws)
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.check_always.pop()
		l = random.randint(0,self.maxlength)
		return [(random.choice(self.elements)).generate() for i in xrange(l)]

class Tuple(Generator):
	def __init__(self, *elements):
		super(Generator, self).__init__()
		self.elements = elements
	def generate(self):
		return tuple([e.generate for e in self.elements])

class Dictionary(Generator):
	def __init__(self, key_vals, maxlength=100):
		super(Generator, self).__init__()
		self.maxlength = maxlength
		self.key_vals = key_vals
	def generate(self):
		l = random.randint(0,self.maxlength)
		return dict([self.key_vals.generate() for i in xrange(l)])

# a sampling generator
class WeightedCmds(UniformCmds):
	def __init__(self, commands, weights):
		super(WeightedCmds, self).__init__(commands)
		self.keys = [c.name for c in commands] # sorted keys
		self.weights = weights
		self.s = float(sum(self.weights))
		assert len(self.weights)==len(self.keys)
	def get_next(self):
		r = random.uniform(0, self.s)
		acc = 0
		for i, w in enumerate(self.weights):
			acc+=w
			if r<acc:
				return self.commands[self.keys[i]]
