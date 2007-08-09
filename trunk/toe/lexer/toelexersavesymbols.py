#!/usr/bin/env python

from toelexer import TLexer, ELexerEofError
from compiler import TLexerGenerator, ELexerLoadError
from toetokens import TToeToken

import cStringIO
import pickle

generator_stream = file("toe-lexer-symbols.source", "r")

generator = TLexerGenerator(TToeToken)
states = generator.load(generator_stream, False)

f = file("toe-lexer-symbols.compiled", "w")
pickle.dump(states, f)
f.close()

