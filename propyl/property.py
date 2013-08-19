from command_generator import UniformCmds, CommandsGenerator
from variable_generator import _var_list
from error import PostConditionNotMet, Error, PreConditionNotMet
from util import RuntimeStates

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
			args, kws = call.caller.get_args(symb_args, symb_kws) # build args
			try:
				call.check_preconditions(args, kws)
			except PreConditionNotMet:
				return UNDEF
			retval = call.call_with_args(args, kws)
			try:
				call.check_postconditions(retval, args, kws)
			except PostConditionNotMet:
				return FAIL
		return OK
	def run_command(self):
		c = self.cmdgen.get_next()
		return c.wrapped()
	def setup(self): pass
	def teardown(self): pass
	def finalize(self): pass
	def test(self, N=1000, max_tries=50):
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
				else:
					raise AssertionError("Could not generate a valid call within %d tries." % (max_tries,))
			self.teardown()
		finally:
			self.finalize()
	def check(self):
		self.run_commands()
	def run_commands(self):
		result = self.run_command()

