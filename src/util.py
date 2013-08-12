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

