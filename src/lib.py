from elements import Generator, UniformCmds, CommandsGenerator
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

class Symbol(Generator): pass # use for symbolic variables

# a sampling generator
class WeightedCmds(UniformCmds):
	def __init__(self, commands, weights):
		super(WeightedCmds, self).__init__(commands)
		self.keys = [c.name for c in commands] # sorted keys
		self.weights = dict([(self.keys[i], weights[i]) for i in xrange(len(self.keys))])
		assert len(self.weights)==len(self.keys), ValueError("bad initializer")
	def get_next(self):
		tries = 0
		while tries<self.max_tries:
			choose_from = []
			for key in self.keys:
				args, kws = self.commands[key].get_args()
				if self.commands[key].check_preconditions(args, kws):
					choose_from.append((key, args, kws))
			if not choose_from:
				tries+=1
			else:
				lw = [self.weights[c[0]] for c in choose_from ]
				s = sum(lw)
				r = random.uniform(0, s)
				acc = 0
				for i, w in enumerate(lw):
					acc+=w
					if r<acc:
						name, args, kws = choose_from[i]
						return self.commands[name], args, kws
		raise AssertionError("Could not generate a valid call within %d tries." % (self.max_tries,))

# fsm generator
class State(object):
	def __init__(self, name):
		super(State, self).__init__()
		self.name = name
	def __gt__(self, other):
		return Transition(self, other)

class Transition(object):
	def __init__(self, from_state, to_state):
		super(Transition, self).__init__()
		self.from_state = from_state
		self.to_state = to_state
		self.functions = []
		self.preconditions = []
	def __call__(self, functions):
		self.functions = functions
		return self
	def get_calls(self):
		possible = []
		for f in self.functions:
			args, kws = f.get_args()
			if f.check_preconditions(args, kws):
				possible.append(f, args, kws) 
		return possible

class FSMCmds(CommandsGenerator):
	def __init__(self, transitions, starting_state, generator=None):
		super(FSMCmds, self).__init__()
		self.transitions = transitions
		self.state = starting_state
	def get_next(self):
		pass
		# todo