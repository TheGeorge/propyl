from propyl import *
from propyl.lib.ctypes_elements import *

mylib = CLib("./mylib.so")

func_add = Call("add", CCall(mylib.add), (CInteger(), CInteger()))

@postcondition(func_add)
def high_level_add(result, a, b):
	return a.value+b.value==result

@test_property("ctypes_base_test")
class Prop_Ctypes_Base(Property):
	_commands_ = [func_add]
	def setup(self):
		setup_ctypes()
	def teardown(self):
		teardown_ctypes()

run_tests(None)