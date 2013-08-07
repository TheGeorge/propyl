import random, sys

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
	def get_args(self, *args, **kws):
		raise NotImplemented
	def call_with_args(self, *args, **kws):
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
	def get_args(self, *args, **kws):
		call_args = tuple([a.value for a in args])
		call_kws = dict([(key, kws[key].value) for key in kws])
		return call_args, call_kws
		#return self.call_with_args(*call_args, **call_kws)
	def call_with_args(self, *call_args, **call_kws):
		for pre in self.hooks:
			pre.hook_arguments(self, call_args, call_kws)
		retval = self.func(*call_args, **call_kws)
		for hook in self.hooks:
			hook.hook_result(self, retval, call_args, call_kws)
		return retval

class Call(object):
	def __init__(self, name, caller, args=(), kws={}):
		self.name = name
		self.caller = caller
		self.symb_args = tuple(args)
		self.symb_kws = dict(kws)
	def get_args(self):
		return self.caller.get_args(*self.symb_args, **self.symb_kws)
	def call_with_args(self, *args, **kws):
		return self.caller.call_with_args(*args, **kws)

class Property(object):
	_commands_ = None
	def __init__(self):
		super(Property, self).__init__()
		cmds = type(self)._commands_
		if isinstance(cmds, list):
			self.cmdgen = UniformCmds(cmds)
		else:
			assert isinstance(cmds, CommandsGenerator)
			self.cmdgen = cmds
		self.command_list = []
		self.max_tries = 0
		self.precondition_tries = 0
	def __getattr__(self, name):
		return self._wrap_call(name)
	def _wrap_call(self, name):
		if not name in self.cmdgen.commands:
			raise NameError
		def wrapped():
			args = None
			kws = None
			try:
				args, kws = self.cmdgen.commands[name].get_args()
				retval = self.cmdgen.commands[name].call_with_args(*args, **kws)
			except PreConditionNotMet as e:
				return (False, None)
			except PostConditionNotMet as e:
				#args,kws = e.message
				retval = args[0]
				args = args[1:]
				tr = (name, self.cmdgen.commands[name], retval, args, kws)
				self.command_list.append(tr)
				if e.message:
					raise AssertionError("postcondition '%s' not met" %(e.message,))
				else:
					raise AssertionError("postcondition not met")
			except:
				e  = sys.exc_info()[1]
				retval = None
				tr = (name, self.cmdgen.commands[name], retval, args, kws)
				self.command_list.append(tr)
				raise AssertionError("crashed")
			tr = (name, self.cmdgen.commands[name], retval, args, kws)
			self.command_list.append(tr)
			return (True, retval)
		return wrapped
	@property
	def command(self):
		c = self.cmdgen.get_next()
		return self._wrap_call(c.name)
	def setup(self): pass
	def teardown(self): pass
	def finalize(self): pass
	def test(self, N=1000, max_tries=50):
		self.max_tries = max_tries
		self.precondition_tries = 0
		try:
			self.setup()
			self.command_list = []
			for i in xrange(N):
				self.check()
			self.teardown()
		finally:
			self.finalize()
	def check(self):
		self.run_commands()
	def run_commands(self):
		ok, result = self.command()
		if not ok:
			self.precondition_tries+=1
			if self.precondition_tries >= self.max_tries:
				raise AssertionError("Couldn't generate a call after %d tries" % (self.max_tries,))
		else:
			self.precondition_tries=0

# command generators
class CommandsGenerator(object):
	def __init__(self, commands):
		super(CommandsGenerator, self).__init__()
		self.commands = dict([(cmd.name, cmd) for cmd in commands])
	def get_next(self):
		raise NotImplemented

class UniformCmds(CommandsGenerator):
	def __init__(self, commands):
		super(UniformCmds, self).__init__(commands)
		self.keys = self.commands.keys()
	def get_next(self):
		return self.commands[random.choice(self.keys)]

# statem stuff
class RuntimeStates:
	states = {}
	@staticmethod
	def init_states(names):
		RuntimeStates.states = dict([(name, {}) for name in names])
	@staticmethod
	def reset_states():
		for key in RuntimeStates.states:
			RuntimeStates.states[key] = {}

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
	def __init__(self, call, name=None):
		super(postcondition, self).__init__()
		self.call = call
		self.name = name
	def __call__(self, hook_func):
		def wrapped(*args, **kws):
			if not hook_func(*args, **kws):
				raise PostConditionNotMet(self.name)
		hook = StateHook(wrapped)
		self.call.caller.add_hook(hook)
		return hook_func
