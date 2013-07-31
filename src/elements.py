import random

# errors
class Error(Exception): pass
class PreConditionNotMet(Error): pass
class PostConditionNotMet(Error): pass

# base elements
class Generator(object):
	def generate(self):
		raise NotImplemented
	@property
	def value(self):
		return self.generate()

class Hook(object):
	def hook_arguments(self, call, args, kws):
		pass
	def hook_result(self, call, retval, args, kws):
		pass

class Caller(object):
	def __call__(self, *args):
		raise NotImplemented
	def add_hook(self, hook):
		raise NotImplemented

class FuncCall(Caller):
	def __init__(self, func):
		super(FuncCall, self).__init__()
		self.func = func
		self.hooks = []
	def add_hook(self, hook):
		assert isinstance(hook, Hook)
		self.hooks.append(hook)
	def __call__(self, *args, **kws):
		call_args = tuple([a.value for a in args])
		call_kws = dict([(key, kws[key].value) for key in kws])
		for pre in self.hooks:
			pre.hook_arguments(self, call_args, call_kws)
		retval = self.func(*call_args, **call_kws)
		for hook in self.hooks:
			hook.hook_result(self, retval, call_args, call_kws)
		return retval, call_args, call_kws

class Call(object):
	def __init__(self, name, caller, args=(), kws={}):
		self.name = name
		self.caller = caller
		self.symb_args = tuple(args)
		self.symb_kws = dict(kws)
	def __call__(self, *args, **kws):
		return self.caller(*self.symb_args, **self.symb_kws)

class TestException(Exception):
	def __init__(self, command_list, prop):
		super(TestException, self).__init__()
		self.command_list = command_list
		self.prop
	def shrink(self): pass
	def output_commands(self):
		for call in self.command_list:
			print("\t"+str(call))

class Property(object):
	_commands_ = None
	def __init__(self):
		super(Property, self).__init__()
		self.commands = dict([(cmd.name, cmd) for cmd in type(self)._commands_])
		self.command_list = []
	def __getattr__(self, name):
		if not name in self.commands:
			raise NameError
		def wrapped():
			try:
				retval, args, kws = self.commands[name]()
			except PreConditionNotMet as e:
				return (False, None)
			except PostConditionNotMet as e:
				args,kws = e.message
				retval = args[0]
				args = args[1:]
				tr = (name, self.commands[name], retval, args, kws)
				self.command_list.append(tr)
				raise AssertionError("postcondition not met")
			tr = (name, self.commands[name], retval, args, kws)
			self.command_list.append(tr)
			return (True, retval)
		return wrapped
	def setup(self): pass
	def teardown(self): pass
	def finalize(self): pass
	def test(self, N=1000):
		try:
			self.setup()
			self.command_list = []
			for i in xrange(N):
				self.check()
			self.teardown()
		finally:
			self.finalize()
	def check(self):
		raise NotImplemented

# statem stuff
class RuntimeStates:
	states = {}
	@staticmethod
	def init_states(names):
		RuntimeStates.states = dict([(name, {}) for name in names])
def get_state(name):
	return RuntimeStates.states[name]

# next_state
class StateHook(Hook):
	def __init__(self, func):
		super(StateHook, self).__init__()
		self.state_func = func
	def hook_result(self, call, retval, args, kws):
		self.state_func(retval, *args, **kws)

class next_state(object):
	def __init__(self, call):
		super(next_state, self).__init__()
		self.call = call
	def __call__(self, hook_func):
		hook = StateHook(hook_func)
		self.call.caller.add_hook(hook)
		return hook_func

# conditions
class PreConditionHook(Hook):
	def __init__(self, func):
		super(PreConditionHook, self).__init__()
		self.func = func
	def hook_arguments(self, call, args, kws):
		if not self.func(*args, **kws):
			raise PreConditionNotMet()

class precondition(object):
	def __init__(self, call):
		super(precondition, self).__init__()
		self.call = call
	def __call__(self, pre_func):
		hook = PreConditionHook(pre_func)
		self.call.caller.add_hook(hook)
		return pre_func

class postcondition(object):
	def __init__(self, call):
		super(postcondition, self).__init__()
		self.call = call
	def __call__(self, hook_func):
		def wrapped(*args, **kws):
			if not hook_func(*args, **kws):
				raise PostConditionNotMet((args,kws))
		hook = StateHook(wrapped)
		self.call.caller.add_hook(hook)
		return hook_func
