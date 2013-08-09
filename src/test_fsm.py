from elements import *
from lib import * 
from search import *

def ping():
	print("ping")
def pong():
	print("pong")

Sping = State("ping")
Spong = State("pong")

func_ping = Call("ping", FuncCall(ping), ())
func_pong = Call("pong", FuncCall(pong), ())

fsm_trans = [
	(Sping > Spong)([func_ping]), 
	(Spong > Sping)([func_pong])
	]

@test_property("my_test")
class Prop_Positive(Property):
	_commands_ = FSMCmds(fsm_trans, Sping)

# run the tests
run_tests(None)
