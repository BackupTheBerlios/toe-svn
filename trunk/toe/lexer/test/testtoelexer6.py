#!/usr/bin/env python

from toe.lexer import TLexer, ELexerEofError
from toe.lexer.compiler import TLexerGenerator, ELexerLoadError
import toe.symbol
import cStringIO

def test_lexer():
  """
Has a typo in the generator stream on purpose.

>>> generator = test_lexer()
>>> generator.next()
toe.symbol.intern("invalid")
  """
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
'NAMESPACE'[[:whitespace:]][[:whitespace:]]*      NAMESPACE
' '              IGNORE
""")
  generator_stream.seek(0)

  table_1 = toe.symbol.table()
  generator = TLexerGenerator(table_1)

  lexer = TLexer()
  lexer.states = generator.load(generator_stream, False)
  assert(len(lexer.states) > 2) # initial, invalid

  test_stream = cStringIO.StringIO()
  test_stream.write("namespacenamespace")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof_p:
    yield lexer.token
    lexer.consume()

"""
1 INVALID
"""

__test__ = {
  "test_lexer": test_lexer,
}


def _test():
  import doctest
  doctest.testmod()

if __name__ == "__main__":
  _test()


