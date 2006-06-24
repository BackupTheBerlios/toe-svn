#!/usr/bin env

import exceptions
import sys

class TCustomRegisterId(int):
	Any = -1

	def __str__(self):
		for name in dir(self.__class__):
			if int(self) == getattr(self.__class__, name):
				return name

		return str(int(self))

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
		self._id = id # TRegisterId(id)
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

	def __repr__(self):
		return str(self._id)

	machine_register_id = property(_get_machine_register_id)

#class TStackRegister(TRegister):
#	pass

class TEstablishment:
	def __str__(self):
		return "Illuminati"

establishment = TEstablishment()

class TCustomCPU(object):
	id_class = None

	def __init__(self):
		self._registers = {}

		id_class = self.__class__.id_class
		for name in dir(id_class):
			if not name.startswith("_") and name != "Any":
				id_value = id_class(getattr(id_class, name))
				self._create_register(TMachineRegister(id_value))

	# returns the allocated register or returns None
	def allocate(self, guest, preferred_id = TCustomRegisterId.Any):
		if preferred_id != TRegisterId.Any and self._registers[preferred_id].guest == None:
			self._registers[preferred_id].guest = guest
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
			print "%s: %s" % (register_id, register.guest)

	def _create_register(self, register):
		id = register.id
		assert(id not in self._registers)
		self._registers[id] = register

class TX86CPU(TCustomCPU):
	"""
	>>> cpu = TX86CPU()
	>>> cpu.print_state()
	eax: None
	ebx: None
	ecx: None
	edx: None
	esi: None
	edi: None
	esp: Illuminati
	ebp: Illuminati
	eip: Illuminati
	"""

	id_class = TX86RegisterId

	def __init__(self):
		TCustomCPU.__init__(self)


		global establishment
		assert(self.allocate(establishment, TX86RegisterId.eip) != None)
		assert(self.allocate(establishment, TX86RegisterId.esp) != None)
		assert(self.allocate(establishment, TX86RegisterId.ebp) != None)

class TX87CPU(TCustomCPU):
	def __init__(self):
		TCustomCPU.__init__(self)

class TARMCPU(TCustomCPU):
	"""
	>>> cpu = TARMCPU()
	>>> cpu.print_state()
	r0: None
	r1: None
	r2: None
	r3: None
	r4: None
	r5: None
	r6: None
	r7: None
	r8: None
	r9: None
	Stack_Limit: Illuminati
	Frame_Pointer: Illuminati
	I_Pointer: Illuminati
	Stack_Pointer: Illuminati
	Link_Return: Illuminati
	Program_Counter: Illuminati
	"""

	id_class = TARMRegisterId

	def __init__(self):
		TCustomCPU.__init__(self)

		global establishment
		assert(self.allocate(establishment, TARMRegisterId.Program_Counter) != None)
		assert(self.allocate(establishment, TARMRegisterId.Link_Return) != None)
		assert(self.allocate(establishment, TARMRegisterId.Stack_Pointer) != None)
		assert(self.allocate(establishment, TARMRegisterId.I_Pointer) != None)
		assert(self.allocate(establishment, TARMRegisterId.Frame_Pointer) != None)
		assert(self.allocate(establishment, TARMRegisterId.Stack_Limit) != None)


TCPU = TX86CPU

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
