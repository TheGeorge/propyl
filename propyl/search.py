from property import Property
from util import RuntimeStates

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
				length = len(prop.command_list)
				print("(name, caller, retval, args, kws)")
				for l in prop.command_list:
					print(str(l))
				print("Shrinking...")
				shrunk_case = self.shrink(prop)
				if len(shrunk_case)<length:
					print("shrunk testcase from %d to %d" % (length, len(shrunk_case)))
					for l in shrunk_case:
						print("\t%s" %(str(l[1]),))
				else:
					print("no smaller testcase found")
				break
	def shrink(self, prop):
		r = []
		c = [i for i in enumerate(prop.command_list)]
		return self.dd2(prop, c, r)

	def dd2(self, prop, c, r):
		c1 = c[:len(c)/2]
		c2 = c[len(c)/2:]
		if len(c)==1:
			return c
		if not self._subtest(prop, c1+r):
			return self.dd2(prop, c1,r)
		elif not self._subtest(prop, c2+r):
			return self.dd2(prop, c2, r)
		else:
			return self.dd2(prop, c1, c2+r)+self.dd2(prop, c2, c1+r)
	def _subtest(self, prop, commands):
		commands.sort(lambda x,y: int.__cmp__(x[0], y[0]))
		c = [packed[1] for packed in commands]
		try:
			prop.run_list(c)
		except:
			return False
		return True

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
		return prop

def run_tests(argv):
	for key in test_props:
		print("Test '%s'" % (key,))
		t = Test(test_props[key])
		try:
			t.run()
		except Exception as e:
			import traceback, sys
			print("The testing framework has crashed during a test: %s" % (e.message,))
			try:
				raw_input("press [Enter] for debug information and [Ctrl+C] to exit.")
			except KeyboardInterrupt:
				print
				sys.exit(0)
			traceback.print_exc(file=sys.stdout)
