from property import *
from util import RuntimeStates
import operator
from calls import Call, FuncCall
from variable_generator import GenGenerator

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
		self.print_stats()
	def print_stats(self):
		counts = {}
		for prop in self.props:
			for call in prop.command_list:
				name = call[0]
				if name in counts:
					counts[name] +=1
				else:
					counts[name] = 1
		total = sum(counts.values())
		print("Statistics: %d calls in total" % (total,))
		for key in counts:
			print("\t%s = %.2f %% (%d)" % (key, float(counts[key])/total*100,counts[key]))

	def shrink(self, prop):
		r = []
		c = [i for i in enumerate(prop.command_list)]
		return self.dd3(prop, c, r, 2)

	def dd3(self, prop, c, r, n):
		if len(c)<=1:
			return c
		l = len(c)/n
		ci = [c[i-l:min(i, len(c))] for i in range(l, len(c)+l, l)]
		ti = [self._subtest(prop, e) for e in [_c for _c in ((ci+[r]) if r else ci)]]
		# found in ci
		for i, t_res in enumerate(ti):
			if t_res==FAIL:
				return self.dd3(prop, ci[i], r, 2)
		ici = [[e for e in c if not e in _c+r] for _c in ci]
		iti = [self._subtest(prop, _c) for _c in (ici+[r] if r else ici)]
		cut = lambda a,b: [e for e in a if e in b]
		# inference
		for i in range(len(ti)):
			if ti[i]==OK and iti[i]==OK:
				return self.dd3(prop, ci[i], ici[i]+r, 2) + self.dd3(prop, ici[i], ci[i]+r, 2)
		# preference
		for i in range(len(ti)):
			if ti[i]==UNDEF and iti==OK:
				return self.dd3(prop, ci[i], ici[i]+r, 2)
		if n<len(c):
			cc = cut(c, reduce(cut, [ici[i] for i in range(len(ici)) if iti[i]==FAIL]))
			rr = r + reduce(operator.add, [ci[i] for i in range(len(ci)) if ti[i]==OK])
			nn = min(len(cc), 2*n)
			return self.dd3(prop, cc, rr, nn)
		else:
			return cut(c, reduce(cut, [ici[i] for i in range(len(ici)) if iti[i]==FAIL]))

	def _subtest(self, prop, commands):
		commands.sort(lambda x,y: int.__cmp__(x[0], y[0]))
		c = [packed[1] for packed in commands]
		return prop.run_list(c)

test_props = {}

class test_property(object):
	def __init__(self, test_name, *args, **kws):
		super(test_property, self).__init__()
		self.name = test_name
		self.args = args
		self.kws = kws
	def __call__(self, prop):
		if type(prop)==type and issubclass(prop, Property):
			if not self.name in test_props:
				test_props[self.name] = []
			test_props[self.name].append(prop(*self.args, **self.kws))
		elif callable(prop):
			# func
			assert isinstance(self.args[0], list), Error("list of calls required")
			assert not self.kws
			prop_call = Call(FuncCall(prop), tuple([GenGenerator(g) for g in prop.__defaults__]))
			if not self.name in test_props:
				test_props[self.name] = []
			test_props[self.name].append(SimpleProperty(prop_call, self.args[0]))
		else:
			raise Error(repr(prop)+" is not a valid property")
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
