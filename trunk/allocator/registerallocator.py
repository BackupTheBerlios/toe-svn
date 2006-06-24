#!/usr/bin/env python

"""

This class emulates infinite registers by resorting to the stack, if neccessary.

Note that any given architecture has multiple sets of registers, like 
normal registers, floating-point registers, mmx registers, ...

Some, by using one set, really clobber another set in the process. I ignore that so far.

TODO: size to allocate in bits?

"""

import exceptions

class TCustomRegisterId(int):
	Any = -1

class TX86RegisterId(TCustomRegisterId):
	eax = 0
	ebx = 1
	ecx = 2
	edx = 3
	esi = 4
	edi = 5
	ebp = 7
	esp = 6
	eip = 8

class TX87RegisterId(TCustomRegisterId):
	pass

class TARMRegisterId(TCustomRegisterId):
	r0 = 0
	r1 = 1
	r2 = 2
	r3 = 3
	r4 = 4
	r5 = 5
	r6 = 6
	r7 = 7
	r8 = 8
	r9 = 9
	Stack_Limit = 10
	Frame_Pointer = 11
	I_Pointer = 12
	Stack_Pointer = 13
	Link_Return = 14
	Program_Counter = 15

TRegisterId = TX86RegisterId

class TRegister(object):
	def __init__(self, id):
		self._id = TRegisterId(id)
		self._guest = None

	def _get_display_string(self):
		return "???"

	def _get_id(self):
		return self._id

	def _get_guest(self):
		return self._guest

	def _set_guest(self, value):
		self._guest = value

	guest = property(_get_guest, _set_guest)
	display_string = property(_get_display_string)
	id = property(_get_id)

class TMachineRegister(TRegister):
	def _get_machine_register_id(self):
		return self._id

	machine_register_id = property(_get_machine_register_id)

class TStackRegister(TRegister):
	pass

class ERegisterUnavailable(exceptions.Exception):
	pass

class TCustomRegisterAllocator(object):
	def __init__(self):
		self._registers = {}

	# returns the allocated register or throws exception.
	def allocate(self, preferred_id = TRegisterId.Any, guest):
		if preferred_id != TRegisterId.Any and self._registers[preferred_id].guest == None:
			self._registers[preferred_id] = guest
			return self._registers[preferred_id]

		for register_id, register in self._registers.items():
			if register.guest == None:
				return register

		raise ERegisterUnavailable("E2006062417: no register available")

	def clobber(self, id):
		self._registers[id].guest = None
		
	def free(self, id):
		self._registers[id].guest = None

	def get_register(self, id):
		return self._registers[id]

	def print_state(self):
		for register_id, register in self._registers.items():
			print "%d: %s" % (register_id, register.guest)

	def _create_register(self, id, register):
		assert(TRegisterId(id) not in self._registers)
		self._registers[TRegisterId(id)] = register

class TX86RegisterAllocator(TCustomRegisterAllocator):
	def __init__(self):
		TCustomRegisterAllocator.__init__(self)

		_create_register()

TRegisterAllocator = TX86RegisterAllocator

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
