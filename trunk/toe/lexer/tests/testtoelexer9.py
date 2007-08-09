#!/usr/bin/env python

from toe.lexer import TLexer, ELexerEofError
from toe.lexer.compiler import TLexerGenerator, ELexerLoadError
import toe.symbol
import cStringIO

def test_lexer():
  """

>>> generator = test_lexer()
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
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
StopIteration
  """
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
[[:whitespace:]]                                      IGNORE
'NAMESPACE'[[:whitespace:]][[:whitespace:]]*          NAMESPACE
[a-zA-Z_[:utf8:]][a-zA-Z0-9_]*[?!]*[[:whitespace:]]*  ID
'.'	DOT
""")
  generator_stream.seek(0)

  table_1 = toe.symbol.table()
  generator = TLexerGenerator(table_1)

  lexer = TLexer()
  lexer.states = generator.load(generator_stream, False)
  assert(len(lexer.states) > 2) # initial, invalid
  #print "len(lexer.states)", len(lexer.states)

  test_stream = cStringIO.StringIO()
  test_stream.write("NAMESPACE f.b.b ")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof:
    yield lexer.token
    lexer.consume()

"""
expected:
len(lexer.states) 2070
18 NAMESPACE
? ID
76 DOT
? ID
76 DOT
? ID
#dannym@pyramid# toe-py # 
"""

__test__ = {
  "test_lexer": test_lexer,
}


def _test():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  _test()


