from ctypes import * 
import random
import propyl

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
		self.ctype = CInteger.conversion[ctype]
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
		self.ctype = CFloat.conversion[ctype]
	def generate(self):
		return self.ctype(super(CFloat, self).generate())



"""
c_wchar	wchar_t	1-character unicode string

c_char_p	char * (NUL terminated)	string or None
c_wchar_p	wchar_t * (NUL terminated)	unicode or None
c_void_p	void *	int/long or None
"""
