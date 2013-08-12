from pyper import *

#test functions
def ping():
	print("ping")
def pong():
	print("pong")

#states
Sping = State("ping")
Spong = State("pong")

#calls
func_ping = Call("ping", FuncCall(ping), ())
func_pong = Call("pong", FuncCall(pong), ())

#fsm definition
fsm_trans = [
	(Sping > Spong)([func_ping]), 
	(Spong > Sping)([func_pong])
	]

#property (just run the commands)
@test_property("my_test")
class Prop_Positive(Property):
	_commands_ = FSMCmds(fsm_trans, Sping)

# run the tests
run_tests(None)
