#!/usr/bin/env python


"""
TODO:
- mutex to make it thread safe
- thread-local storage to speed it up
- case-sensitiveness option
- multiple symbol tables
- deletion of symbol tables
- support read-only operation
"""

class symbol(object):
	""" don't instantiate this directly! """
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return "toe.symbol.intern(\"%s\")" % self.text # TODO escape
		#return "\\%s" % self.text

	def __str__(self):
		return "#\"%s\"" % self.text
		#return "\\%s" % self.text

# TODO do this properly

class table(dict): # key :: <symbol>
	def set(self, symbol_1, value):
		""" @takes(symbol, object) """
		assert(isinstance(symbol_1, symbol))
		self[symbol_1] = value

		return self

interned_strings = {} # name -> symbol

def intern(text):
	"""
	>>> a = intern("a")
	>>> b = intern("b")
	>>> id(a) == id(b)
	False
	>>> id(a) == id(intern("a"))
	True
	>>> id(b) == id(intern("b"))
	True
	>>> id(b) == id(intern("a"))
	False
	>>> id(a) == id(intern("b"))
	False
	>>> id(a) == symbol("a")
	False
	"""
	global interned_strings
	result = interned_strings.get(text)
	if result is None:
		result = symbol(text)
		interned_strings[text] = result

	return result

if __name__ == "__main__":
	import doctest
	doctest.testmod()

