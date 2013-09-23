from propyl import *
import sys
#test functions
def ping():
	sys.stdout.write(".")
def pong():
	sys.stdout.write("#")

#states
Sping = State("ping")
Spong = State("pong")

#calls
func_ping = Call(FuncCall(ping))
func_pong = Call(FuncCall(pong))

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
import sys
run_tests(sys.argv)
print