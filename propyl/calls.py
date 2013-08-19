from hooks import *
from variable_generator import FromArguments
from error import * 
import sys
import copy

class Caller(object):
	def get_args(self, *args, **kws):
		raise NotImplemented
	def call_with_args(self, *args, **kws):
		raise NotImplemented
	def add_hook(self, hook):
		raise NotImplemented
	@property
	def name(self):
		raise NotImplemented

class FuncCall(Caller):
	def __init__(self, func):
		super(FuncCall, self).__init__()
		self.func = func
		self.hooks = []
	def add_hook(self, hook):
		assert isinstance(hook, Hook)
		self.hooks.append(hook)
	def get_args(self, args, kws):
		# generate call_args
		call_args = []
		rebuild_args = []
		for i, arg in enumerate(args):
			if isinstance(arg, FromArguments):
				rebuild_args.append((i,arg))
				call_args+=[None]
			else:
				call_args+=[arg.value]
		call_kws  = {}
		rebuild_kws = []
		for key in kws:
			if isinstance(kws[key], FromArguments):
				call_kws[key] = None
				rebuild_kws += [key]
		# build FromArguments elements
		for i,arg in rebuild_args:
			call_args[i] = arg.generate(args=call_args, kws=call_kws)
		for key in rebuild_kws:
			call_kws[key] = kws[key].generate(args=call_args, kws=call_kws)
		call_args = tuple(call_args)
		return call_args, call_kws
	def check_preconditions(self, call_args, call_kws):
		for pre in self.hooks:
			if not isinstance(pre, PreConditionHook):
				continue
			pre.hook_arguments(self, call_args, call_kws)
	def check_postconditions(self, retval, call_args, call_kws):
		for hook in self.hooks:
			hook.hook_result(self, retval, call_args, call_kws)
	def call_with_args(self, call_args, call_kws):
		for hook in self.hooks:
			hook.hook_call(self, call_args, call_kws)
		retval = self.func(*call_args, **call_kws)
		return retval
	@property
	def name(self):
		return self.func.__name__

class Call(object):
	def __init__(self, caller, args=(), kws={}, name = None):
		if name:
			self.name = name
		else:
			self.name = caller.name
		self.caller = caller
		self.symb_args = tuple(args)
		self.symb_kws = dict(kws)
		self.command_list = []
	def get_args(self):
		return self.caller.get_args(self.symb_args, self.symb_kws)
	def call_with_args(self, args, kws):
		return self.caller.call_with_args(args, kws)
	def check_preconditions(self, call_args, call_kws):
		self.caller.check_preconditions(call_args, call_kws)
	def check_postconditions(self, retval, call_args, call_kws):
		self.caller.check_postconditions(retval, call_args, call_kws)
	def wrapped(self):
		args, kws = self.get_args() # generate values
		self.check_preconditions(args, kws)
		tr_args = copy.deepcopy(self.symb_args)
		tr_kws = copy.deepcopy(self.symb_kws)
		try:
			retval = self.call_with_args(args, kws)
			tr = (self.name, self, retval, tr_args, tr_kws)
			self.command_list.append(tr)
			try:
				self.check_postconditions(retval, args, kws)
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
			tr = (self.name, self, retval, tr_args, tr_kws)
			self.command_list.append(tr)
			import traceback
			traceback.print_exc(file=sys.stdout)
			raise AssertionError("crashed")
		#return (True, retval)
		return retval
	def __call__(self, *args, **kws):
		self.symb_args = args
		self.symb_kws = kws
		return self.wrapped()
	def __repr__(self):
		return "<%s>" % (self.name,)
