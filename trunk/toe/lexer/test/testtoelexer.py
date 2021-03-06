#!/usr/bin/env python

from toe.lexer import TLexer, ELexerEofError
from toe.lexer.compiler import TLexerGenerator, ELexerLoadError
import toe.symbol
import cStringIO

def test_lexer():
  """
>>> generator = test_lexer()
>>> generator.next()
('len(lexer.states)', 1371)
>>> generator.next()
toe.symbol.intern("namespace")
>>> generator.next()
toe.symbol.intern("id")
>>> generator.next()
toe.symbol.intern("dot")
>>> generator.next()
toe.symbol.intern("id")
>>> generator.next()
toe.symbol.intern("dot")
>>> generator.next()
toe.symbol.intern("id")
>>> generator.next()
toe.symbol.intern("newline")
>>> generator.next()
toe.symbol.intern("newline")
>>> generator.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
StopIteration
  """
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
[[:newline:]]                 NEWLINE
[[:whitespace:]]              IGNORE
'namespace'[[:whitespace:]]*  NAMESPACE
[a-z][a-z0-9_?!]*             ID
':='[[:whitespace:]]*         ASSIGNMENT
'+'[[:whitespace:]]*          PLUS
'.'                           DOT
""")
  generator_stream.seek(0)

  table_1 = toe.symbol.table()
  generator = TLexerGenerator(table_1)

  lexer = TLexer()
  lexer.states = generator.load(generator_stream, False)

  #for i in range(len(lexer.states)):
  #  print generator.string_transitions(i)

  assert(len(lexer.states) > 2) # initial, invalid
  yield ("len(lexer.states)", len(lexer.states))

  test_stream = cStringIO.StringIO()
  test_stream.write("""namespace aaa.aaa.aaa

""")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof_p:
    yield lexer.token
    lexer.consume()

__test__ = {
  "test_lexer": test_lexer,
}


def _test():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  _test()


