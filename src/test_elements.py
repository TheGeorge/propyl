from elements import *
from lib import * 

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

@postcondition(func_a)
def define_property_as_condition(result, *args, **kws):
	if result >= 0:
		return True
	else:
		return False

class Prop_Positive(Property):
	_commands_ = [func_a]
	def setup(self):
		get_state("general")["summed"] = 0
	def check(self):
		ok, ret = self.func_a()
		if ok:
			assert ret >= 0, AssertionError("not positive")

# glue code to run the test
RuntimeStates.init_states(["general"])
p = Prop_Positive()

try:
	p.test()
except AssertionError as e:
	print "Error: ", e.message
finally:
	for l in p.command_list:
		print l

print RuntimeStates.states
