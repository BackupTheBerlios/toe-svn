#!/usr/bin/env python

import toe.symbol

TLexerState = int

TLexerStateTransitionItem = TLexerState # or record with extra information

class TLexerStateTransition(object):
  def __init__(self):
    # 0 => state invalid
    self._transitions = 256 * [0] # char -> TLexerStateTransitionItem
    self._fallback_token = toe.symbol.intern("invalid") # token
    self._is_wildcard_tainted = False
    self.is_modified = True # dummy, unused
  
  def set_is_wildcard_tainted(self, value):
    self._is_wildcard_tainted = value

  def set_fallback_token(self, value):
    self._fallback_token = value
    
  def __str__(self):
    result = []
    
    if self._fallback_token != 0: # none
      result.append("  DONE -> %s" % str(self._fallback_token))
    
    for index, transition in enumerate(self._transitions):
      if index >= 32 and index < 128:
        c = chr(index)
      else:
        c = "#%d" % index
        
      if transition != 0: # invalid
        result.append("  %s -> %d" % (c, transition))

    result.append("")
    return "\n".join(result)
    
  fallback_token = property(lambda self: self._fallback_token, set_fallback_token)
  is_wildcard_tainted = property(lambda self: self._is_wildcard_tainted, set_is_wildcard_tainted)
  #modified
  transitions = property(lambda self: self._transitions)
    
class TLexerStates(object):
  def __init__(self):
    self._states = [] # of TLexerStateTransition
    self._is_case_sensitive = False

  def __len__(self):
    return len(self._states)
    
  def __iter__(self):
    for item in self._states:
      yield item
      
  def __repr__(self):
    result = []
    for index, item in enumerate(self._states):
      result.append("S%d:" % index)
      result.append(str(item))
    
    return "\n".join(result)
    
  def set_is_case_sensitive(self, value):
    self._is_case_sensitive = value
    
  states = property(lambda self: self._states)
  is_case_sensitive = property(lambda self: self._is_case_sensitive, set_is_case_sensitive)


