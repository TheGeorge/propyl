from command_generator import UniformCmds, CommandsGenerator
from variable_generator import _var_list
from error import PostConditionNotMet, Error
from util import RuntimeStates

import sys

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
	#def __getattr__(self, name):
		#return self.cmdgen.commands[name]
	def _wrap_call(self, name, args, kws):
		if not name in self.cmdgen.commands:
			raise NameError
		a,k = args, kws
		def wrapped():
			args, kws = a,k
			try:
				retval = self.cmdgen.commands[name].call_with_args(args, kws)
				# if the call didn't crash we have all the information to add it to the call history
				tr = (name, self.cmdgen.commands[name], retval, args, kws)
				self.command_list.append(tr)
				#self.cmdgen.commands[name].check_postconditions(retval, args, kws)
				try:
					self.cmdgen.commands[name].check_postconditions(retval, args, kws)
				except PostConditionNotMet as e:
					raise e
				except Exception as e:
					raise Error("crashed evaluating a postcondition: %s" % (e.message,))
			except PostConditionNotMet as e:
				if e.message:
					raise AssertionError("postcondition '%s' not met" %(e.message,))
				else:
					raise AssertionError("postcondition not met")
			except Error as e:
				raise e
			except:
				e  = sys.exc_info()[1]
				retval = None
				tr = (name, self.cmdgen.commands[name], retval, args, kws)
				self.command_list.append(tr)
				import traceback
				traceback.print_exc(file=sys.stdout)
				raise AssertionError("crashed")
			return (True, retval)
		return wrapped
	def run_list(self, command_list):
		RuntimeStates.reset_states()
		self.setup()
		for command in command_list:
			cn, call, retval, args, kws = command
			if not call.check_preconditions(args, kws):
				# TODO implement DD+ algorithm
				# also do something with the fsm
				return
			retval = call.call_with_args(args, kws)
			call.check_postconditions(retval, args, kws)

	@property
	def command(self):
		c, args, kws = self.cmdgen.get_next()
		return self._wrap_call(c.name, args, kws)
	def setup(self): pass
	def teardown(self): pass
	def finalize(self): pass
	def test(self, N=1000, max_tries=50):
		self.cmdgen.max_tries = max_tries
		try:
			self.setup()
			self.command_list = []
			for i in xrange(N):
				# for every run: reset var_list
				for var in _var_list:
					var.next_run()
				# now check the property
				self.check()
			self.teardown()
		finally:
			self.finalize()
	def check(self):
		self.run_commands()
	def run_commands(self):
		ok, result = self.command()
