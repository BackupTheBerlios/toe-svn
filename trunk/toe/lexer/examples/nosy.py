#!/usr/bin/env python

"""
this customizes the lexer a little bit so that it supports string escaping in string literals
"""

from toelexer import TLexer
import toe.symbol

class TNosyLexer(TLexer):
  def want_to_continue_token(self):
    token = self.token
    matched_text = self.matched_text

    if token == toe.symbol.intern("string-literal")
      # allows escaping the quotes
      # i.e. "he said \"foo\""
      
      assert(len(matched_text) > 0)
      quote = matched_text[0]
      if len(matched_text) >= 2:
        before_end_quote = matched_text[-2]
        if before_end_quote == "\\":
          self.matched_text = matched_text[:-2] + quote
          
          return True
    
    return False

def _test_nosy_lexer():
  """
  >>> generator = _test_nosy_lexer()
  >>> generator.next()
  (77, #"string-literal", '"he said "hello""')
  >>> generator.next()
  Traceback (most recent call last):
    File "<stdin>", line 1, in ?
  StopIteration
  """

  import cStringIO
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
'"'[^"]*'"'	QUOTED_STRING

""")
  generator_stream.seek(0)

  from compiler import TLexerGenerator
  
  table_1 = toe.symbol.table()
  generator = TLexerGenerator(table_1)

  lexer = TNosyLexer()
  lexer.states = generator.load(generator_stream, False)
  assert(len(lexer.states) > 2) # initial, invalid

  test_stream = cStringIO.StringIO()
  test_stream.write("\"he said \\\"hello\\\"\"")
  test_stream.seek(0)
  lexer.source_stream = test_stream

  while not lexer.eof:
    yield (lexer.token, repr(lexer.token), lexer.matched_text)
    lexer.consume()
  
def _test():
  import doctest
  doctest.testmod()
    
if __name__ == "__main__":
  _test()

  