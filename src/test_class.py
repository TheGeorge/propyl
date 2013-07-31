class A(object):
	_watch_ = []
	def print_watch(self):
		print type(self)._watch_

class B(A):
	_watch_ = [1,2,3]

B().print_watch()
