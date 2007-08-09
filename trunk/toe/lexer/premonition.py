#!/usr/bin/env python

# TODO: actually use this

class stream(object):
	"""
	>>> from cStringIO import StringIO
	>>> io = StringIO()
	>>> io.write("foobar")
	>>> io.seek(0)
	>>> stream_1 = stream(io)
	>>> stream_1.peek()
	'f'
	"""
	def __init__(self, stream):
		self.stream = stream
		self.pending = None

	def _fetch(self):
		if self.pending is None:
			self.pending = self.stream.read(1)
			if self.pending == "":
				self.pending = None

	def peek(self):
		self._fetch()
		return self.pending

	def consume(self):
		self.pending = None

	# for debugging and error messages:
	def consume_rest(self):
		rest = StringIO()
		if self.pending is not None:
			rest.write(self.pending)

		rest.write(self.stream.read())

		return rest.getvalue()

	def __iter__(self):
		while True:
			input = self.peek()
			if input is None:
				break

			yield input
			self.consume()

if __name__ == "__main__":
	import doctest
	doctest.testmod()
