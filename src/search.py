import elements

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

