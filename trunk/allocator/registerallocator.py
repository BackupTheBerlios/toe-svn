#!/usr/bin/env python

"""

This class emulates infinite registers by resorting to the stack, if neccessary.

Note that any given architecture has multiple sets of registers, like 
normal registers, floating-point registers, mmx registers, ...

Some, by using one set, really clobber another set in the process. I ignore that so far.

TODO: size to allocate in bits?

"""

import sys
import exceptions
import stackallocator
import cpuallocator
from cpuallocator import TRegisterId

class TStackRegister(cpuallocator.TRegister):
	def __init__(self, offset):
		cpuallocator.TRegister.__init__(self, TRegisterId(128 + offset))
		self._offset = offset

	def __str__(self):
		return "in stack frame at %d" % self._offset

	def __repr__(self):
		return str(self)

	offset = property(lambda self: self._offset)

class ERegisterUnavailable(exceptions.Exception):
	pass

class TCustomRegisterAllocator(object):
	stack_allocator_class = None

	def __init__(self, cpu):
		self._cpu = cpu
		self._stack_allocator = self.__class__.stack_allocator_class()
		self._stack_offsets = [] # [keep sorted.] index = offset // self._cpu.register_size, value = register

	# returns the allocated register or throws exception.
	def allocate(self, guest, preferred_id = TRegisterId.Any, is_stack_ok = True):
		register = self._cpu.allocate(guest, preferred_id)
		if register == None:
			if is_stack_ok and self._stack_allocator != None:
				offset = self._stack_allocator.push()
				index = offset // self._cpu.__class__.register_size

				while len(self._stack_offsets) <= index:
					self._stack_offsets.append(None)

				register = TStackRegister(offset)
				self._stack_offsets[index] = register

				return register
		else:
			return register

		raise ERegisterUnavailable("E2006062417: no register available")

	# also takes care of culling the stack, if possible (and only then).
	def _unstack(self, offset):
		index = offset // self._cpu.__class__.register_size
		assert(len(self._stack_offsets) > index)
		self._stack_offsets[index] = None
		#print >>sys.stderr, "unstacko", self._stack_offsets

		# find leftermost 'None' item (cull from there later)
		i = index
		while i >= 0:
			if self._stack_offsets[i] != None:
				break

			i = i - 1

		i = i + 1

		index = i

		# now check if all the tail is 'None'
		while i < len(self._stack_offsets):
			if self._stack_offsets[i] != None:
				# there are some other registers on top of the stack, can't compact.
				#print >>sys.stderr, "bam"
				return

			#print >>sys.stderr, "item...."
			i = i + 1

		# get rid
		count = len(self._stack_offsets) - index
		if count > 0:
			#print >>sys.stderr, "unstack", count
			self._stack_allocator.pop(count)
			self._stack_offsets = self._stack_offsets[:-count]

	def clobber(self, id):
		if id >= 128:
			self._unstack(id - 128)
		else:
			self._cpu.clobber(id)
		
	def free(self, id):
		if id >= 128:
			self._unstack(id - 128)
		else:
			self._cpu.free(id)

	def get_register(self, id):
		return self._cpu.get_register(id)

	def print_state(self):
		self._cpu.print_state()

	stack_allocator = property(lambda self: self._stack_allocator)

class TX86RegisterAllocator(TCustomRegisterAllocator):
	"""
	>>> cpu = cpuallocator.TX86CPU()
	>>> registers = TX86RegisterAllocator(cpu)
	>>> registers.print_state()
	eax: None
	ebx: None
	ecx: None
	edx: None
	esi: None
	edi: None
	esp: Illuminati
	ebp: Illuminati
	eip: Illuminati
	>>> registers.allocate(1)
	eax
	>>> registers.allocate(2)
	ebx
	>>> registers.allocate(7)
	ecx
	>>> registers.allocate(3)
	edx
	>>> registers.allocate(100)
	esi
	>>> registers.allocate(200)
	edi
	>>> registers.allocate(300)
	in stack frame at 0
	>>> registers.allocate(400)
	in stack frame at 4
	>>> registers.allocate(4)
	in stack frame at 8
	"""
	stack_allocator_class = stackallocator.TX86StackAllocator

	def __init__(self, cpu):
		TCustomRegisterAllocator.__init__(self, cpu)

"""
this class has a kind of funny design. It has 0 (yes, zero) registers and resorts 
to the stack for everything.
"""
class TX87RegisterAllocator(TCustomRegisterAllocator):
	stack_allocator_class = stackallocator.TX87StackAllocator

	def __init__(self, cpu):
		TCustomRegisterAllocator.__init__(self, cpu)

class TARMRegisterAllocator(TCustomRegisterAllocator):
	"""
	>>> cpu = cpuallocator.TARMCPU()
	>>> registers = TARMRegisterAllocator(cpu)
	>>> registers.print_state()
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
	>>> registers.allocate(1)
	r0
	>>> registers.allocate(2)
	r1
	>>> registers.allocate(7)
	r2
	>>> registers.allocate(3)
	r3
	>>> registers.allocate(100)
	r4
	>>> registers.allocate(200)
	r5
	>>> registers.allocate(201)
	r6
	>>> registers.allocate(202)
	r7
	>>> registers.allocate(203)
	r8
	>>> registers.allocate(204)
	r9
	>>> print registers.stack_allocator.position
	0
	>>> r128 = registers.allocate(300)
	>>> print r128
	in stack frame at 0
	>>> r129 = registers.allocate(400)
	>>> print r129
	in stack frame at 4
	>>> print registers.stack_allocator.position
	8
	>>> r130 = registers.allocate(4)
	>>> print r130
	in stack frame at 8
	>>> registers.free(r130.id)
	>>> print registers.stack_allocator.position
	8
	>>> r131 = registers.allocate(400)
	>>> print r131
	in stack frame at 8
	>>> registers.free(r129.id)
	>>> registers.free(r131.id)
	>>> print registers.stack_allocator.position
	4
	"""
	stack_allocator_class = stackallocator.TX86StackAllocator

	def __init__(self, cpu):
		TCustomRegisterAllocator.__init__(self, cpu)

TRegisterAllocator = TX86RegisterAllocator

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()
