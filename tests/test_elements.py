from propyl import *

# the function to test:
def d(x,y):
	if x==0:
		return -1
	if x<y:
		return y-x
	else:
		return x-y

func_a = Call("func_d", FuncCall(d), (Integer(), Integer()))

@next_state(func_a)
def record_results(result, *args, **kws):
	get_state("general")["summed"] += result

@precondition(func_a)
def only_even_numbers(*args, **kws):
	if (args[0] % 2):
		return False
	return True

@postcondition(func_a, "always positive")
def define_property_as_condition(result, *args, **kws):
	if result >= 0:
		return True
	else:
		return False

@test_property("my_test")
class Prop_Positive(Property):
	#_commands_ = WeightedCmds2([func_a], [1])
	_commands_ = [func_a]
	def setup(self):
		get_state("general")["summed"] = 0

# init the states
RuntimeStates.init_states(["general"])

# run the tests
run_tests(None)
