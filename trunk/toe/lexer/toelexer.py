#!/usr/bin/env python

import exceptions
from data import TLexerStates
import time

TToken = int
IGNORE = 0
INVALID = 1

def paranoid_char(i):
  if i == chr(32):
    return "<SPACE>"
    
  if i == chr(9):
    return "<TAB>";
    
  if i == chr(13):
    return "<CR>"
    
  if i == chr(10):
    return "<LR>"
    
  if i > chr(127):
    return "<#%d>" % ord(i)

class ELexerEofError(exceptions.Exception):
  pass
    
class TLexer(object):
  def __init__(self, **kwargs):
    global INVALID
    self._token = INVALID
    self._eof = False
    self._eof_pending = False
    self._state = 0 # state invalid
    self._previous_state = 0 # state invalid  # for continue_token
    self._source_file_path = None
    self._source_line_number = 1
    self._source_column_number = 0
    self._source_stream = None
    self._matched_text = ""
    self._input_char = chr(0)
    self._input_char_valid = False
    self._matched_text_clear_next = True
    self._last_state_change = time.time()
    self._states = TLexerStates()

    for key, value in kwargs.items():
      assert(hasattr(self, "set_" + key))
      getattr(self, "set_" + key)(value)
    
  def set_states(self, value):
    assert(isinstance(value, TLexerStates))
    self._states = value
    
  def set_source_stream(self, value):
    self._source_stream = value
    self._state = 1 # state initial
    self._last_state_change = time.time()
    self._previous_state = 0 # state invalid
    self._eof = False
    self._eof_pending = False
    self._matched_text_clear_next = True
    self.consume()
    
  def consume(self):
    global IGNORE
    self._token = IGNORE
    self._matched_text = ""
    self._matched_text_clear_next = True
    
    # token IGNORE: 0
    while (not self._eof) and (self._token == IGNORE):
      self.consume_one()
      
    return self._token

  # overload that
  def want_to_continue_token(self):
    #self.token
    #self.matched_text
    # note that "state" is still "old"
    return False
  
  # returns: TToken
  def consume_one(self):
    global INVALID
    global IGNORE
    
    if self._eof_pending == True:
      self._eof = True
      return INVALID
    
    if self._source_stream == None:
      self._eof = True
      # fall
      
    if self._eof == True:
      raise ELexerEofError("Unexpected end of file")
      
    transitions = self._states.states[self._state]
    
    reached_end = False # ?
    if self._input_char_valid == False:
      self._input_char = self._source_stream.read(1) # fixme?
      if self._input_char != "":
        self._input_char_valid = True
      else:
        reached_end = True
    else:
      reached_end = False
      
    if reached_end == True:
      # with that the lexer needs one last wish, and that is to consume a char not matching whatever
      # was the last rule. This will cause the last token to complete even though there is no violation character.
      # i.e. [a-z][a-z]*   ID  matches "abc" at the end of the file too, and returns the token ID, before finishing
      
      self._token = transitions.fallback_token
      if self._token != INVALID:
        self._eof_pending = True
        return self._token

      self._eof = True
      raise ELexerEofError("Unexpected end of file")
      
    # not end
    
    if self._input_char == "\n":
      self._source_column_number = 0
      self._source_line_number = self._source_line_number + 1
    else:
      self._source_column_number = self._source_column_number + 1
    
    if self._states.is_case_sensitive == True:
      input_code = ord(self._input_char)
    else:
      input_code = ord(self._input_char.upper())
    
    next_state = transitions.transitions[input_code]
        
    if next_state == 0: # state invalid
      if transitions.fallback_token <> INVALID:
        self._token = transitions.fallback_token

        if self.want_to_continue_token() == True:
          # wants to continue in token, so
          #   frobnicate the state and hope no one notices.
        
          self._token = IGNORE
          self._state = self._previous_state
          return IGNORE
      else:
        self._token = transitions.fallback_token # XX
        self._input_char_valid = False
        
      self._matched_text_clear_next = True
      self._previous_state = self._state
      self._state = 1 # state initial
      self._last_state_change = time.time()
    else: # next state, next char
      self._input_char_valid = False
      if self._matched_text_clear_next == True:
        self._matched_text_clear_next = False
        self._matched_text = ""
        
      self._matched_text = self._matched_text + self._input_char # slow
      self._previous_state = self._state
      self._state = next_state
      self._last_state_change = time.time()
      
    return self._token # 0: no token

  def set_source_line_number(self, value):
    self._source_line_number = value
    
  def set_source_column_number(self, value):
    self._source_column_number = value
    
  def set_source_file_path(self, value):
    self._source_file_path = value
    
  def set_state(self, value):
    self._state = value
    self._last_state_change = time.time()
    
  def set_matched_text(self, value):
    self._matched_text = value
    
  token = property(lambda self: self._token)
  source_file_path = property(lambda self: self._source_file_path, set_source_file_path)
  source_line_number = property(lambda self: self._source_line_number, set_source_line_number)
  source_column_number = property(lambda self: self._source_column_number, set_source_column_number)
  source_stream = property(lambda self: self.source_stream, set_source_stream)
  eof = property(lambda self: self._eof)
  input_char = property(lambda self: self._input_char)
  matched_text = property(lambda self: self._matched_text, set_matched_text)
  states = property(lambda self: self._states, set_states) # *possible* states (TLexerStates)
  state = property(lambda self: self._state, set_state)  
  last_state_change = property(lambda self: self._last_state_change)

  