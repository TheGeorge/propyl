from ctypes import * 
import random
import propyl
from propyl.error import * 
import operator, platform

class CTypesError(Error): pass

# types
class CBool(propyl.Generator):
	def generate(self):
		return c_bool(random.choice([True, False]))

class CChar(propyl.Generator):
	def __init__(self, chars=None):
		super(CChar, self).__init__()
		self.chars = chars
	def generate(self):
		if not self.chars:
			return c_char(chr(random.randint(0,255)))
		else:
			return c_char(random.choice(self.chars))

class CInteger(propyl.Integer):
	conversion = {
		'byte'                  : c_byte,
		'unsigned byte'         : c_ubyte,
		'short'                 : c_short,
		'unsigned short'        : c_ushort,
		'int'                   : c_int,
		'unsigned int'          : c_uint,
		'long'                  : c_long,
		'unsigned long'         : c_ulong,
		'long long'             : c_longlong,
		'unsigned long long'    : c_ulonglong
		}
	def __init__(self, lb=-1000, ub=1000, ctype="int"):
		super(CInteger, self).__init__(lb=lb, ub=ub)
		if isinstance(ctype, str):
			self.ctype = CInteger.conversion[ctype]
		else:
			self.ctype = ctype
	def generate(self):
		return self.ctype(super(CInteger, self).generate())

class CFloat(propyl.Float):
	conversion = {
		'double'      : c_double,
		'long double' : c_longdouble,
		'float'       : c_float
		}
	def __init__(self, lb=-1000.0, ub=1000.0, ctype="float"):
		super(CFloat, self).__init__(lb=lb, ub=ub)
		if isinstance(ctype, str):
			self.ctype = CFloat.conversion[ctype]
		else:
			self.ctype = ctype
	def generate(self):
		return self.ctype(super(CFloat, self).generate())

class CStr(propyl.Generator):
	conversion = {
		'c_char_p' : c_char_p
		}
	def __init__(self, characters=None, maxlength=128, ctype="c_char_p"):
		super(CStr, self).__init__()
		self.characters = characters
		if isinstance(ctype, str):
			self.ctype = CStr.conversion[ctype]
		else:
			self.ctype = ctype
		self.maxlength = 128
		self.check_always = [""]*3
	def generate(self):
		if self.check_always and random.uniform(0,1)<0.2:
			return self.ctype(self.check_always.pop())
		l = random.randint(0,self.maxlength)
		return self.ctype(reduce(operator.add, [chr(random.randint(0,255)) for i in xrange(l)]))

# unimplemented base types:
"""
c_wchar	wchar_t	1-character unicode string

c_wchar_p	wchar_t * (NUL terminated)	unicode or None
c_void_p	void *	int/long or None
"""

_used_libs = []

# storrage
_loaders = {}
_unloaders = {}

# decorators
class loader(object):
	def __init__(self, name):
		self.name = name
	def __call__(self, func):
		_loaders[self.name] = func
		return func
class unloader(object):
	def __init__(self, name):
		self.name = name
	def __call__(self, func):
		_unloaders[self.name] = func
		return func

# loaders
@loader("linux")
def linux_loader(path):
	return cdll.LoadLibrary(path)

__libdl = None
@unloader("linux")
def linux_unloader(lib):
	handle = lib._handle
	if not __libdl:
		__libdl = cdll.LoadLibrary("libdl.so")
	del lib
	__libdl.dlclose(handle)

__win_handles = {}
@loader("win32")
def win_loader(path):
	handle = ctypes.windll.kernel32.LoadLibraryA(path)
	lib = ctypes.WinDLL(None, handle=handle)
	__win_handles[lib] = handle
	return lib

@unloader("win32")
def win_unloader(lib):
	handle = __win_handles.pop(lib)
	del lib
	ctypes.windll.kernel32.FreeLibrary(handle)

# wrappers
def _save_load_lib(path):
	# determine loader to use
	if platform.system()=='Linux':
		return _loaders['linux'](path)
	if platform.system()=='Windows':
		return _loaders['win32'](path)
	else:
		return CTypesError("no loader for the current architecture implemented")

def _save_unload_lib(lib):
	# determine loader to use
	if platform.system()=='Linux':
		return _unloaders['linux'](lib)
	if platform.system()=='Windows':
		return _unloaders['win32'](lib)
	else:
		return CTypesError("no loader for the current architecture implemented")

# encapsuled C-lib
class CLib(object):
	def __init__(self, path_to_lib, unload=True):
		super(CLib, self).__init__()
		self.path = path_to_lib
		self.lib = None
		self.unload = unload
		_used_libs.append(self)
	def __getattr__(self, name):
		"""get symbolic c-function"""
		return CFunction(self, name)
	def init(self):
		if not self.lib:
			self.lib = _save_load_lib(self.path)
	def teardown(self):
		if self.unload:
			_save_unload_lib(self.lib)
			self.lib = None

# util
def setup_ctypes():
	for lib in _used_libs:
		lib.init()
def teardown_ctypes():
	for lib in _used_libs:
		lib.teardown()

class CFunction(object):
	""" symbolic c function """
	def __init__(self, lib, name):
		super(CFunction, self).__init__()
		self.lib = lib
		self.name = name
		self.argtypes = None
		self.restype = None
	def __call__(self, *args):
		# retrieve library and function at call time
		if not self.lib.lib:
			raise CTypesError("library not loaded, forget to initialize?")
		f = getattr(self.lib.lib, self.name)
		if self.argtypes:
			f.argtypes = self.argtypes
		if self.restype:
			f.restype = self.restype
		return f(*args)

# call object
class CCall(propyl.FuncCall):
	""" same as function call, just checks that no kws arguments are used and emphthizes the fact that you are calling a c function
	"""
	def __init__(self, func, restype=None):
		super(CCall, self).__init__(func)
		self.func.restype = restype
	def get_args(self, args, kws):
		assert not kws, CTypesError("c functions take no keyword arguments")
		try:
			self.func.argtypes = [arg.ctype for arg in args]
		except AttributeError as e:
			raise CTypesError("error: all ctypes generators must define a ctype attribute")
		return super(CCall, self).get_args(args, kws)
	def check_preconditions(self, call_args, call_kws):
		assert not call_kws, CTypesError("c functions take no keyword arguments")
		return super(CCall, self).check_preconditions(call_args, call_kws)
	def check_postconditions(self, retval, call_args, call_kws):
		assert not call_kws, CTypesError("c functions take no keyword arguments")
		return super(CCall, self).check_postconditions(retval, call_args, call_kws)
	def call_with_args(self, call_args, call_kws):
		assert not call_kws, CTypesError("c functions take no keyword arguments")
		return super(CCall, self).call_with_args(call_args, call_kws)

# util property
class CProperty(propyl.Property):
	def setup(self):
		setup_ctypes()
	def teardown(self):
		teardown_ctypes()
