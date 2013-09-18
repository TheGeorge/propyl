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

# set stuff
def intersect(a,b):
	if not a:
		return []
	if not b:
		return []
	return [e for e in a if e in b]
