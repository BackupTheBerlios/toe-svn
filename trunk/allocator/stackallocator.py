#!/usr/bin/env python

"""

there can be multiple stacks, like
  - one stack per thread
  - one stack for signal handlers
  - one stack for interrupts
  etcetc
"""

import exceptions

class EStackUnderflow(exceptions.Exception):
	pass

class TCustomStackAllocator(object):
	# size: total in byte
	# item size: one item size in byte
	def __init__(self, item_size):
		self._position = 0
		self._item_size = item_size # byte
		self._reserved_size = 0

	def push(self):
		#if self._position >= self._size:
		#	raise EStackOverflow()

		result = self._position
		self._position = self._position + self._item_size
		return result

	def pop(self, count = 1):
		relative = self._item_size * count
		if self._position < self._reserved_size + relative:
			raise EStackUnderflow("E20060624174: Stack frame underflow")

		self._position = self._position - relative

	position = property(lambda self: self._position)

class TX86StackAllocator(TCustomStackAllocator):
	"""
	>>> stack = TX86StackAllocator()
	>>> stack.push()
	0
	>>> stack.position
	4
	>>> stack.push()
	4
	>>> stack.position
	8
	>>> stack.pop()
	>>> stack.position
	4
	>>> stack.pop()
	>>> stack.position
	0
	>>> stack.push()
	0
	>>> stack.position
	4
	>>> stack.pop()
	>>> stack.position
	0
	>>> stack.pop()
	Traceback (most recent call last):
	EStackUnderflow: E20060624174: Stack frame underflow
	"""
	def __init__(self):
		TCustomStackAllocator.__init__(self, 4)
	pass

class TX87StackAllocator(TCustomStackAllocator):
	"""
	>>> stack = TX87StackAllocator()
	>>> stack.position
	56
	>>> address_1 = stack.push()
	>>> print address_1
	56
	>>> stack.position
	64
	>>> stack.register_number_of_address(address_1)
	0
	>>> address_2 = stack.push()
	>>> print address_2
	64
	>>> stack.position
	72
	>>> stack.register_number_of_address(address_2)
	0
	>>> stack.register_number_of_address(address_1)
	1
	>>> stack.pop()
	>>> print stack.register_number_of_address(address_1)
	0
	>>> print stack.register_number_of_address(address_2)
	None
	>>> stack.pop()
	>>> print stack.register_number_of_address(address_1)
	None
	>>> print stack.register_number_of_address(address_2)
	None
	>>> stack.pop()
	Traceback (most recent call last):
	EStackUnderflow: E20060624174: Stack frame underflow
	>>> address_1 = stack.push()
	>>> address_2 = stack.push()
	>>> address_3 = stack.push()
	>>> address_4 = stack.push()
	>>> address_5 = stack.push()
	>>> address_6 = stack.push()
	>>> address_7 = stack.push()
	>>> address_8 = stack.push()
	>>> address_9 = stack.push()
	>>> print stack.register_number_of_address(address_1)
	None
	>>> print stack.register_number_of_address(address_2)
	7
	>>> print stack.register_number_of_address(address_3)
	6
	>>> print stack.register_number_of_address(address_4)
	5
	>>> print stack.register_number_of_address(address_5)
	4
	>>> print stack.register_number_of_address(address_6)
	3
	>>> print stack.register_number_of_address(address_7)
	2
	>>> print stack.register_number_of_address(address_8)
	1
	>>> print stack.register_number_of_address(address_9)
	0
	>>> stack.pop()
	>>> print stack.register_number_of_address(address_1) # actually stupid, but I leave it at that for now
	7
	"""
	def __init__(self):
		TCustomStackAllocator.__init__(self, 8)
		for i in range(7):
			self.push()
		self._reserved_size = self._position

	def push_sized(self, item_size):
		#if self._position >= self._size:
		#	raise EStackOverflow()

		result = self._position
		self._position = self._position + item_size
		return result

	def pop_sized(self, item_size, count = 1):
		relative = item_size * count
		if self._position < relative:
			raise EStackUnderflow("E20060624174: Stack frame underflow")

		self._position = self._position - relative

	# returns register number or None (note that the register number changes with every push* or pop* !)
	def register_number_of_address(self, address):
		number = (self._position - self._item_size - address) // self._item_size
		if number < 0 or number > 7:
			return None

		return number

TStackAllocator = TX86StackAllocator

def _test():
	import doctest
	doctest.testmod()

if __name__ == "__main__":
	_test()

