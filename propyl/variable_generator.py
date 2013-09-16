import random

# import everything important
from util import * 
from variable_generator import * 

import copy

NOCOPY, COPY, DEEPCOPY = range(3)

_var_list = [] # global variable list
class Generator(object):
	def __init__(self, copy=COPY):
		_var_list.append(self)
		self.generate_new = True
		self.val = None
		self.copy = copy
	def next_run(self):
		self.generate_new = True
	def generate(self):
		raise NotImplemented
	@property
	def value(self):
		if self.generate_new:
			self.val = self.generate()
			self.generate_new = False
		return self.val
	def __repr__(self):
		return "<g %s>" % (repr(self.val),)
	def dublicate(self):
		if self.copy==NOCOPY:
			return self
		elif self.copy==COPY:
			return copy.copy(self)
		else:
			return copy.deepcopy(self)

# base types
class Integer(Generator):
	def __init__(self, lb=-1000, ub=1000):
		super(Integer, self).__init__()
		self.lb = lb
		self.ub = ub
		self.check_always = [0,1,-1]*3
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.check_always.pop()
		return random.randint(self.lb, self.ub)

class Float(Generator):
	def __init__(self, lb=-1000.0, ub=1000.0):
		super(Float, self).__init__()
		self.lb = lb
		self.ub = ub
	def generate(self):
		return random.uniform(self.lb, self.ub)

class Str(Generator):
	def __init__(self, characters=None, maxlength=128):
		super(CStr, self).__init__()
		self.characters = characters
		self.maxlength = 128
		self.check_always = [""]*3
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.ctype(self.check_always.pop())
		l = random.randint(0,self.maxlength)
		if not self.characters:
			return reduce(operator.add, [chr(random.randint(0,255)) for i in xrange(l)])
		else:
			return reduce(operator.add, [random.choice(self.characters) for i in xrange(l)])

class Element(Generator):
	def __init__(self, values, copy=COPY):
		super(Element, self).__init__(copy=copy)
		self.values = values
	def generate(self):
		return random.choice(values)

# structured types
class List(Generator):
	def __init__(self, *elements, **kws):
		def pa(copy=COPY, maxlength=100): return copy, maxlength
		copy, maxlength =pa(**kws)
		super(List, self).__init__(copy=copy)
		self.elements = elements
		self.check_always=[[]]*3
		self.maxlength =maxlength
		self.val = []
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.check_always.pop()
		l = random.randint(0,self.maxlength)
		return [(random.choice(self.elements)).generate() for i in xrange(l)]
	@property
	def value(self):
		if self.generate_new:
			self.val = self.generate()
			self.generate_new = False
		return copy.copy(self.val)
	def __repr__(self):
		if len(self.val)<5:
			return "<g List %s>" % (repr(self.val),)
		else:
			b = "["
			for i in self.val[:5]:
				b+=repr(i)+", "
			b+="...]"
			return "<g List %s>" % (repr(b),)

class Tuple(Generator):
	def __init__(self, *elements):
		super(Tuple, self).__init__()
		self.elements = elements
	def generate(self):
		return tuple([e.generate for e in self.elements])

class Dictionary(Generator):
	def __init__(self, key_vals, maxlength=100):
		super(Dictionary, self).__init__()
		self.maxlength = maxlength
		self.key_vals = key_vals
	def generate(self):
		l = random.randint(0,self.maxlength)
		return dict([self.key_vals.generate() for i in xrange(l)])

class GenGenerator(Generator):
	def __init__(self, generator):
		super(GenGenerator, self).__init__()
		self.g = generator
	def generate(self):
		return self.g

# Symbolic variables and some python class magic
class _Symbols(type):
	_syms_ = {}
	def __getattr__(cls, name):
		if not name in Symbols._syms_:
			raise AttributeError(name)
		else:
			return Symbols._syms_[name].generate()
	def add(cls, var):
		cls._syms_[var.name] = var

class Symbols(object):
	__metaclass__ = _Symbols

class Symbol(Generator):
	""" This should generate the same value every time within a run
	"""
	def __init__(self, name, code, ns={}):
		super(Symbol, self).__init__(copy=COPY)
		self.name = name
		self.code = code
		self.ns = ns
		Symbols.add(self)
	def generate(self):
		if isinstance(self.code, Generator):
			return self.code.generate()
		else:
			if callable(self.code):
				return self.code()
			else:
				return eval(self.code, globals(), self.ns)
			if self.val:
				return random.choice(self.val)
			else:
				return None

class FromArguments(Generator):
	def __init__(self, func):
		super(FromArguments, self).__init__()
		self.func = func
	def generate(self, args=(), kws={}):
		return self.func(*args, **kws)

class GenericGenerator(Generator):
	def __init__(self, code, **kws):
		super(GenericGenerator, self).__init__()
		self.code = code
		self.ns = {}
		for key in kws:
			setattr(self, key, kws[key])
	def generate(self):
		if isinstance(self.code, Generator):
			return self.code.generate()
		elif callable(self.code):
			return self.code()
		else:
			return random.choice(eval(self.code, globals(), self.ns))
