#!/usr/bin env

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

#class TStackRegister(TRegister):
#	pass

class TCustomCPU(object):
	def __init__(self):
		self._registers = {}

	# returns the allocated register or returns None
	def allocate(self, guest, preferred_id = TRegisterId.Any):
		if preferred_id != TRegisterId.Any and self._registers[preferred_id].guest == None:
			self._registers[preferred_id] = guest
			return self._registers[preferred_id]

		for register_id, register in self._registers.items():
			if register.guest == None:
				register.guest = guest
				return register

		return None

	def clobber(self, id):
		self._registers[id].guest = None
		
	def free(self, id):
		self._registers[id].guest = None

	def get_register(self, id):
		return self._registers[id]

	def print_state(self):
		for register_id, register in self._registers.items():
			print "%d: %s" % (register_id, register.guest)

	def _create_register(self, register):
		id = register.id
		assert(TRegisterId(id) not in self._registers)
		self._registers[TRegisterId(id)] = register

class TX86CPU(TCustomCPU):
	"""
	>>> cpu = TX86CPU()
	>>> cpu.print_state()
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
	def __init__(self):
		TCustomCPU.__init__(self)

		for name in dir(TX86RegisterId):
			if not name.startswith("_") and name != "Any":
				self._create_register(TMachineRegister(getattr(TX86RegisterId, name)))

class TX87CPU(TCustomCPU):
	def __init__(self):
		TCustomCPU.__init__(self)

TCPU = TX86CPU

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
