from command_generator import UniformCmds, CommandsGenerator, OneGen, GeneratorMessage
from variable_generator import _var_list, GenGenerator, Symbol
from error import PostConditionNotMet, Error, PreConditionNotMet, TestFailed
from util import RuntimeStates
from calls import Call, FuncCall

import sys

OK, FAIL, UNDEF = range(3)

class Property(object):
	_commands_ = []
	def __init__(self):
		super(Property, self).__init__()
		cmds = type(self)._commands_
		if isinstance(cmds, list):
			self.cmdgen = UniformCmds(cmds)
		else:
			assert isinstance(cmds, CommandsGenerator)
			self.cmdgen = cmds
		self.command_list = []
	def run_list(self, command_list):
		RuntimeStates.reset_states()
		self.setup()
		self.cmdgen.setup()
		for command in command_list:
			cn, call, retval, symb_args, symb_kws = command
			if not self.cmdgen.test_call(call):
				return UNDEF
			# all symbolic args need to rebuild
			for sa in symb_args:
				if isinstance(sa, Symbol):
					sa.next_run()
			# now build current args
			args, kws = call.caller.get_args(symb_args, symb_kws) # build args
			try:
				call.check_preconditions(args, kws)
			except PreConditionNotMet:
				return UNDEF
			try:
				retval = call.wrapped(iargs=args, ikws=kws, record=False)
			except GeneratorMessage as e:
				try:
					self.cmdgen.check_exception(e)
				except:
					return FAIL
			except TestFailed as e:
				return FAIL
		return OK
	def run_command(self):
		c = self.cmdgen.get_next()
		return c.wrapped()
	def setup(self): pass
	def teardown(self): pass
	def finalize(self): pass
	def test(self, N, max_tries):
		self.cmdgen.max_tries = max_tries
		try:
			self.setup()
			self.command_list = []
			for commands in self.cmdgen.commands.values():
				commands.command_list = self.command_list
			for i in xrange(N):
				# for every run: reset var_list
				for var in _var_list:
					var.next_run()
				# now check the property
				for i in range(max_tries):
					try:
						self.check()
						break
					except PreConditionNotMet:
						for var in _var_list:
							var.next_run() # reset variable generators
					except GeneratorMessage as e:
						self.cmdgen.check_exception(e)
						break
				else:
					raise AssertionError("Could not generate a valid call within %d tries." % (max_tries,))
			self.teardown()
		finally:
			self.finalize()
	def check(self):
		self.run_command()

class SimpleProperty(Property):
	def __init__(self, command):
		self.cmdgen = OneGen(command)
		self.cmds = [command]

test_props = {}

class test_property(object):
	def __init__(self, test_name, *args, **kws):
		super(test_property, self).__init__()
		self.name = test_name
		self.args = args
		self.kws = kws
	def __call__(self, prop):
		if type(prop)==type and issubclass(prop, Property):
			if not self.name in test_props:
				test_props[self.name] = []
			test_props[self.name].append(prop(*self.args, **self.kws))
		elif callable(prop):
			# func
			assert not self.kws
			prop_call = Call(FuncCall(prop), tuple([g for g in prop.__defaults__]))
			if not self.name in test_props:
				test_props[self.name] = []
			test_props[self.name].append(SimpleProperty(prop_call))
		else:
			raise Error(repr(prop)+" is not a valid property")
		return prop