import random
from error import PreConditionNotMet, TransitionError

# command generators
class CommandsGenerator(object):
	def __init__(self, commands):
		super(CommandsGenerator, self).__init__()
		self.commands = dict([(cmd.name, cmd) for cmd in commands])
		self.max_tries = 50
	def get_next(self):
		raise NotImplemented
	def test_call(self, call):
		return True # usually calls are accepted when replaying
	def setup(self): pass

class UniformCmds(CommandsGenerator):
	def __init__(self, commands):
		super(UniformCmds, self).__init__(commands)
	def get_next(self):
		return random.choice(self.commands.values())

#s a sampling generator
class WeightedCmds(UniformCmds):
	def __init__(self, commands, weights):
		super(WeightedCmds, self).__init__(commands)
		self._commands = commands
		self.weights = weights
		assert len(self.weights)==len(self._commands), Error("bad initializer for generator, weights must match the amount of calls")
	def get_next(self):
		s = sum(self.weights)
		r = random.uniform(0, s)
		acc = 0
		for i, w in enumerate(self.weights):
			acc+=w
			if r<acc:
				return self._commands[i]

class OneGen(CommandsGenerator):
	def __init__(self, command):
		super(OneGen, self).__init__([command])
		self.command = command
	def get_next(self):
		return self.command

# fsm generator
class State(object):
	def __init__(self, name):
		super(State, self).__init__()
		self.name = name
	def __gt__(self, other):
		return Transition(self, other)

class Transition(object):
	def __init__(self, from_state, to_state):
		super(Transition, self).__init__()
		self.from_state = from_state
		self.to_state = to_state
		self.functions = []
		self.preconditions = []
	def __call__(self, functions):
		self.functions = functions
		return self
	def get_calls(self):
		return self.functions

class FSMCmds(CommandsGenerator):
	def __init__(self, transitions, starting_state):
		super(FSMCmds, self).__init__([])
		self.states = {}
		for transition in transitions:
			fs = transition.from_state
			if fs in self.states:
				self.states[fs].append(transition)
			else:
				self.states[fs] = [transition]
			for c in transition.functions:
				self.commands[c.name] = c
		self.starting_state = starting_state
		self.state = starting_state
	def do_transition(self, call, collected=None):
		if not collected:
			collected = self._get_calls()
		if call in collected:
			transition = collected[call]
			self.state = transition.to_state
		else:
			raise TransitionError
	def _get_calls(self):
		transitions = self.states[self.state]
		collected = {}
		for transition in transitions:
			calls = transition.get_calls()
			for call in calls:
				assert not call in collected, KeyError("too many targets")
				collected[call] = transition
		return collected
	def get_next(self):
		collected = self._get_calls()
		selected = random.choice(collected.keys())
		self.do_transition(selected, collected=collected)
		return selected
	def test_call(self, call):
		try:
			self.do_transition(call)
			return True
		except TransitionError:
			return False
	def setup(self):
		self.state = self.starting_state