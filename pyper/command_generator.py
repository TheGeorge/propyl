import random

# command generators
class CommandsGenerator(object):
	def __init__(self, commands):
		super(CommandsGenerator, self).__init__()
		self.commands = dict([(cmd.name, cmd) for cmd in commands])
		self.max_tries = 50
	def get_next(self):
		raise NotImplemented

class UniformCmds(CommandsGenerator):
	def __init__(self, commands):
		super(UniformCmds, self).__init__(commands)
		self.keys = self.commands.keys()
	def get_next(self):
		# evaluate all preconditions
		tries = 0
		while tries<self.max_tries:
			choose_from = []
			for key in self.keys:
				args, kws = self.commands[key].get_args()
				if self.commands[key].check_preconditions(args, kws):
					choose_from.append((self.commands[key], args, kws))
			if choose_from:
				return random.choice(choose_from)
			tries += 1
		raise AssertionError("Could not generate a valid call within %d tries." % (self.max_tries,))

#s a sampling generator
class WeightedCmds(UniformCmds):
	def __init__(self, commands, weights):
		super(WeightedCmds, self).__init__(commands)
		self.keys = [c.name for c in commands] # sorted keys
		self.weights = dict([(self.keys[i], weights[i]) for i in xrange(len(self.keys))])
		assert len(self.weights)==len(self.keys), ValueError("bad initializer")
	def get_next(self):
		tries = 0
		while tries<self.max_tries:
			choose_from = []
			for key in self.keys:
				args, kws = self.commands[key].get_args()
				if self.commands[key].check_preconditions(args, kws):
					choose_from.append((key, args, kws))
			if not choose_from:
				tries+=1
			else:
				lw = [self.weights[c[0]] for c in choose_from ]
				s = sum(lw)
				r = random.uniform(0, s)
				acc = 0
				for i, w in enumerate(lw):
					acc+=w
					if r<acc:
						name, args, kws = choose_from[i]
						return self.commands[name], args, kws
		raise AssertionError("Could not generate a valid call within %d tries." % (self.max_tries,))

class WeightedCmds2(UniformCmds):
	""" this generator first generates <weight> amount of calls for each function, filters them with the preconditions and then selects one uniformly
	"""
	def __init__(self, commands, weights):
		super(WeightedCmds2, self).__init__(commands)
		self.keys = [c.name for c in commands] # sorted keys
		self.weights = dict([(self.keys[i], int(weights[i])) for i in xrange(len(self.keys))])
		assert len(self.weights)==len(self.keys), ValueError("bad initializer")
	def get_next(self):
		tries = 0
		while tries<self.max_tries:
			choose_from = []
			for key in self.keys:
				for i in xrange(self.weights[key]):
					args, kws = self.commands[key].get_args()
					if self.commands[key].check_preconditions(args, kws):
						choose_from.append((key, args, kws))
			if not choose_from:
				tries+=1
			else:
				name, args, kws = random.choice(choose_from)
				return self.commands[name], args, kws
		raise AssertionError("Could not generate a valid call within %d tries." % (self.max_tries,))


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
		possible = []
		for f in self.functions:
			args, kws = f.get_args()
			if f.check_preconditions(args, kws):
				possible.append((f, args, kws))
		return possible

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
		self.state = starting_state
	def get_next(self):
		transitions = self.states[self.state]
		collected = {}
		for transition in transitions:
			calls = transition.get_calls()
			for call, args, kws in calls:
				assert not call in collected, KeyError("too many targets")
				collected[call] = (args, kws, transition)
		selected = random.choice(collected.keys())
		args, kws, transition = collected[selected]
		self.state = transition.to_state
		return selected, args, kws
