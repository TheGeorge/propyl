from elements import * 

class Search(object):
	def __init__(self, properties, N=1000):
		super(Search,self).__init__()
		self.props = properties
		self.amount = N
	def test(self):
		for prop in self.props:
			print("Property %s" %(prop.name,))
			for i in xrange(amount):
				try:
					prop.test()
				except elements.TestException as testcase:
					print("oh my!")
					testcase.shrink
					testcase.output_commands
					break



class Test(object):
	def __init__(self, properties, N=1000):
		self.props = properties
		self.runs = N
	def run(self):
		for prop in self.props:
			RuntimeStates.reset_states()
			try:
				prop.test(N=self.runs)
			except AssertionError as e:
				print("Error: %s" % (e.message,))
				for l in prop.command_list:
					print(str(l))

test_props = {}

class test_property(object):
	def __init__(self, test_name, *args, **kws):
		super(test_property, self).__init__()
		self.name = test_name
		self.args = args
		self.kws = kws
	def __call__(self, prop):
		if not self.name in test_props:
			test_props[self.name] = []
		test_props[self.name].append(prop(*self.args, **self.kws))

def run_tests(argv):
	for key in test_props:
		print("Test '%s'" % (key,))
		t = Test(test_props[key])
		try:
			t.run()
		except Exception as e:
			print("The testing framework has crashed during a crash: %s" % (e.message,))
			raw_input("press [Enter] for debug information and [Ctrl+C] to exit.")
			import traceback, sys
			traceback.print_exc(file=sys.stdout)

