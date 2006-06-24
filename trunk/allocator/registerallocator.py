#!/usr/bin/env python

"""

This class emulates infinite registers by resorting to the stack, if neccessary.

Note that any given architecture has multiple sets of registers, like 
normal registers, floating-point registers, mmx registers, ...

Some, by using one set, really clobber another set in the process. I ignore that so far.

TODO: size to allocate in bits?

"""

import exceptions
import stackallocator
import cpuallocator
from cpuallocator import TRegisterId

class TStackRegister(cpuallocator.TRegister):
	pass

class ERegisterUnavailable(exceptions.Exception):
	pass

class TCustomRegisterAllocator(object):
	stack_allocator_class = None

	def __init__(self, cpu):
		self._cpu = cpu
		self._stack_allocator = self.__class__.stack_allocator_class()

	# returns the allocated register or throws exception.
	def allocate(self, guest, preferred_id = TRegisterId.Any, is_stack_ok = True):
		register = self._cpu.allocate(guest, preferred_id)
		if register == None:
			if is_stack_ok and self._stack_allocator != None:
				address = self._stack_allocator.push()
				# TODO
			
		raise ERegisterUnavailable("E2006062417: no register available")

	def clobber(self, id):
		self._cpu.clobber(id)
		
	def free(self, id):
		self._cpu.free(id)

	def get_register(self, id):
		return self._cpu.get_register(id)

	def print_state(self):
		self._cpu.print_state()

class TX86RegisterAllocator(TCustomRegisterAllocator):
	"""
	>>> cpu = cpuallocator.TX86CPU()
	>>> registers = TX86RegisterAllocator(cpu)
	>>> registers.print_state()
	0: None
	1: None
	2: None
	3: None
	4: None
	5: None
	6: None
	7: None
	8: None
	"""
	stack_allocator_class = stackallocator.TX86StackAllocator

	def __init__(self, cpu):
		TCustomRegisterAllocator.__init__(self, cpu)

class TX87RegisterAllocator(TCustomRegisterAllocator):
	stack_allocator_class = stackallocator.TX87StackAllocator

	def __init__(self, cpu):
		TCustomRegisterAllocator.__init__(self, cpu)

TRegisterAllocator = TX86RegisterAllocator

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
