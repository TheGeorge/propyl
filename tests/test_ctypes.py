from propyl import *
from propyl.lib.ctypes_elements import *
from ctypes import * 

mylib = CLib("./mylib.so")

func_add = Call(CCall(mylib.add, restype=c_int), (CInteger(), CInteger()))

@postcondition(func_add)
def high_level_add(result, a, b):
	return a.value+b.value==result

@test_property("ctypes_base_test")
class Prop_Ctypes_Base(CProperty):
	_commands_ = [func_add]

run_tests(None)
