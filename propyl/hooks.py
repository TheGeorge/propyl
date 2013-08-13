from error import PostConditionNotMet

class Hook(object):
	def hook_arguments(self, call, args, kws):
		pass
	def hook_result(self, call, retval, args, kws):
		pass

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
		return self.func(*args, **kws)


class precondition(object):
	def __init__(self, call):
		super(precondition, self).__init__()
		self.call = call
	def __call__(self, pre_func):
		hook = PreConditionHook(pre_func)
		self.call.caller.add_hook(hook)
		return pre_func

class postcondition(object):
	_counter_ = 0
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
