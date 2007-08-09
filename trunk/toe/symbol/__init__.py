#!/usr/bin/env python


"""
TODO:
- mutex to make it thread safe
- thread-local storage to speed it up
- case-sensitiveness option
- multiple symbol tables
- deletion of symbol tables
"""

class symbol(object):
	def __init__(self, text):
		self.text = text

	def __repr__(self):
		return "#\"%s\"" % self.text
		#return "\\%s" % self.text

# TODO do this properly

class symbol_table(dict):
	def intern(self, text):
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
		"""
	        result = self.get(text)
	        if result is None:
                	result = symbol(text)
        	        self[text] = result

		return result

global_table = symbol_table()
def intern(name):
	global global_table
	return global_table.intern(name)

if __name__ == "__main__":
	import doctest
	doctest.testmod()

