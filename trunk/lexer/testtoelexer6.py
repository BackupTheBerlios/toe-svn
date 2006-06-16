#!/usr/bin/env python

from toelexer import TLexer, ELexerEofError
from toelexergenerator import TLexerGenerator, ELexerLoadError
from toetokens import TToeToken
import cStringIO

def test_lexer():
  """
Has a typo in the generator stream on purpose.

>>> generator = test_lexer()
>>> generator.next()
Traceback (most recent call last):
ELexerLoadError: in line(3): ' ' NO -->  <-- ' ' IGNORE
syntax error (3), char is " "

  """
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
'NAMESPACE'
' ' IGNORE
""")
  generator_stream.seek(0)

  generator = TLexerGenerator(TToeToken)

  lexer = TLexer()
  lexer.states = generator.load(generator_stream, False)
  assert(len(lexer.states) > 2) # initial, invalid

  test_stream = cStringIO.StringIO()
  test_stream.write("namespacenamespace")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof:
    yield (lexer.token, TToeToken.to_name(lexer.token))
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


