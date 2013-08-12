import random

_var_list = [] # global variable list
class Generator(object):
	def __init__(self):
		_var_list.append(self)
	def next_run(self): pass
	def generate(self):
		raise NotImplemented
	@property
	def value(self):
		return self.generate()

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

# Symbolic variables and some python class magic
class _Symbols(type):
	_syms_ = {}
	def __getattr__(cls, name):
		if not name in _syms_:
			raise AttributeError(name)
		else:
			return _syms_[name]
	def add(cls, var):
		cls._syms_[var.name] = var

class Symbols(object):
	__metaclass__ = _Symbols

class Symbol(Generator):
	""" This should generate the same value every time within a run
	"""
	def __init__(self, name, code):
		super(Symbol, self).__init__()
		self.name = name
		self.code = code
		self.value = None
		self.generate_new = True
		Symbols.add(self)
	def next_run(self):
		super(Symbol, self).next_run()
		# generate value once per run
		self.generate_new = True
	def generate(self):
		if self.generate_new:
			# check if the value for this turn has already been generated
			self.value = random.choice(eval(code))
			self.generate_new = False
		return self.value
