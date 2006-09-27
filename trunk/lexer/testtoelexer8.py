#!/usr/bin/env python

from toelexer import TLexer, ELexerEofError
from toelexergenerator import TLexerGenerator, ELexerLoadError
from toetokens import TToeToken
import cStringIO

def test_lexer():
  """

>>> generator = test_lexer()
>>> generator.next()
(18, 'NAMESPACE')
>>> generator.next()
(79, 'ID')
>>> generator.next()
(76, 'DOT')
>>> generator.next()
(79, 'ID')
>>> generator.next()
(76, 'DOT')
>>> generator.next()
(79, 'ID')
>>> generator.next()
Traceback (most recent call last):
  File "<stdin>", line 1, in ?
StopIteration
  """
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
[[:whitespace:]]                                IGNORE
'NAMESPACE'[[:whitespace:]][[:whitespace:]]*    NAMESPACE
[a-zA-Z_][a-zA-Z0-9_]*[?!]*[[:whitespace:]]*    ID
'.'	DOT
""")
  generator_stream.seek(0)

  generator = TLexerGenerator(TToeToken)

  lexer = TLexer()
  lexer.states = generator.load(generator_stream, False)
  assert(len(lexer.states) > 2) # initial, invalid
  #print "len(lexer.states)", len(lexer.states)

  test_stream = cStringIO.StringIO()
  test_stream.write("NAMESPACE f.b.b ")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof:
    yield (lexer.token, TToeToken.to_name(lexer.token))
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


