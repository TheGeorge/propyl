from elements import *
from lib import * 
from search import *

# the function to test:
def a(x,y):
	if x==0:
		return -1
	if x<y:
		return y-x
	else:
		return x-y

func_a = Call("func_a", FuncCall(a), (Integer(), Integer()))

@next_state(func_a)
def record_results(result, *args, **kws):
	get_state("general")["summed"] += result

@precondition(func_a)
def only_even_numbers(*args, **kws):
	if (args[0] % 2):
		return False
	return True

#@postcondition(func_a)
#def define_property_as_condition(result, *args, **kws):
	#if result >= 0:
		#return True
	#else:
		#return False



@test_property("my_test")
class Prop_Positive(Property):
	_commands_ = WeightedCmds([func_a], [1])
	def setup(self):
		get_state("general")["summed"] = 0
	def check(self):
		ok, ret = self.command()
		if ok:
			assert ret >= 0, AssertionError("not positive")

# init the states
RuntimeStates.init_states(["general"])

# run the tests
run_tests(None)
