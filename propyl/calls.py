from hooks import *

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
	def get_args(self, args, kws):
		call_args = tuple([a.value for a in args])
		call_kws = dict([(key, kws[key].value) for key in kws])
		return call_args, call_kws
	def check_preconditions(self, call_args, call_kws):
		for pre in self.hooks:
			if not isinstance(pre, PreConditionHook):
				continue
			if not pre.hook_arguments(self, call_args, call_kws):
				return False
		return True
	def check_postconditions(self, retval, call_args, call_kws):
		for hook in self.hooks:
			hook.hook_result(self, retval, call_args, call_kws)
	def call_with_args(self, call_args, call_kws):
		for hook in self.hooks:
			hook.hook_call(self, call_args, call_kws)
		retval = self.func(*call_args, **call_kws)
		return retval

class Call(object):
	def __init__(self, name, caller, args=(), kws={}):
		self.name = name
		self.caller = caller
		self.symb_args = tuple(args)
		self.symb_kws = dict(kws)
	def get_args(self):
		return self.caller.get_args(self.symb_args, self.symb_kws)
	def call_with_args(self, args, kws):
		return self.caller.call_with_args(args, kws)
	def check_preconditions(self, call_args, call_kws):
		return self.caller.check_preconditions(call_args, call_kws)
	def check_postconditions(self, retval, call_args, call_kws):
		self.caller.check_postconditions(retval, call_args, call_kws)
