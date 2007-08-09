#!/usr/bin/env python

from data import TLexerStates, TLexerStateTransition
import sys
import exceptions
import toe.symbol

STATE_INVALID = 0 # dupe
STATE_INITIAL = 1 # dupe
INVALID = toe.symbol.intern("invalid") # invalid token

def phony_upper_case(c):
  return c.upper()
  
def phony_lower_case(c):
  return c.lower()

# debugging only
def phonychr(c):
  if c >= 32 and c < 128:
    return chr(c)
    
  return "#%d" % c
  

class TLexerStateMatches(object):
  def __init__(self):
    self._states = [] # of TLexerState

  def __len__(self):
    return len(self._states)
    
  def __getitem__(self, index):
    return self._states[index]
    
  def __iter__(self):
    for item in self._states: 
      yield item
      
  def __str__(self):
    return str(self._states)
      
  def copy(self):
    result = TLexerStateMatches()
    result._states = self._states[:]
    return result
    
  def add(self, state):
    for xstate in self._states:
      if xstate == state:
        return
        
    self._states.append(state)

  def clear(self):
    self._states = []
  
  # debug
  def print1(self, prefix = "states: ", suffix = "\n\r"):
    sys.stdout.write(prefix)
    for state in self._states:
      sys.stdout.write(state)
      sys.stdout.write(" ")
      
    sys.stdout.write(suffix)

# basically just a set()
# TODO use set()
class TLexerMatchset(object):
  # TODO make that a real set (if the order actually doesn't matter)
  def __init__(self):
    self._matchset = [] # of bool
    
  def clear(self):
    self._matchset = []
    
  def __len__(self):
    return len(self._matchset)
  
  # debug
  def __str__(self):
    list_1 = []
    for index, value in enumerate(self._matchset):
      if value == True:
        list_1.append(chr(index))
        
    return "".join(list_1)
    
  def __getitem__(self, index):
    return self._matchset[index]
    
  def add(self, c, case_sensitive):
    if case_sensitive == False:
      self._add(phony_upper_case(c))
    else:
      self._add(c)
    
  def _add(self, c):
    cix = ord(c)
    while cix >= len(self._matchset):
      self._matchset.append(False)
      
    self._matchset[cix] = True

  def invert(self):
    for cix in range(len(self._matchset)):
      self._matchset[cix] = not self._matchset[cix]
      
    count = len(self._matchset)
    icount = 1 << (8 * 1) # 1 == sizeof(TLexerChar)
    
    if icount > count:
      for cix in range(icount - count):
        self._matchset.append(not False)
        
  def print1(self, prefix = "", suffix = "\n\r"):
    sys.stdout.write(prefix)
    for c in self._matchset:
      sys.stdout.write(chr(c))
    sys.stdout.write(suffix)
    
  def is_empty(self):
    return len(self._matchset) == 0

class ELexerLoadError(exceptions.Exception):
  pass

class TLexerGenerator(object):
  def __init__(self, token_table): # token_table: symbol_table
    self._lexer_states = TLexerStates()
    self._line_number = 0
    self._line = None # for error messages
    
    self._token_table = token_table

    
    self._token_name = None
    self._matchset1 = TLexerMatchset()
    self._need_set_token_states = TLexerStateMatches() # set of states the token must be set for
    self._case_sensitive = False
    self._wildcard_fixups = {} # onset_state -> non-wildcard grammar part string, e.g. 5: "abc"

  def new_state(self):
    # TLexerState
    #print ".",
    
    new_state = len(self._lexer_states.states)
    self._lexer_states.states.append(TLexerStateTransition())
    assert(new_state > STATE_INVALID) # state invalid
    return new_state

  # returns: <toe.symbol.symbol> # TODO: get rid of 'self._token_name', it's ugly
  def declare_symbol(self):
    try:
      return self._token_table.set(toe.symbol.intern(self._token_name), None)
    except exceptions.Exception, e:
      print >>sys.stderr, "toe.compiler: exception: ", e
      raise ELexerLoadError("syntax error (11): unknown token \"%s\"" % self._token_name) # SIGH near ' + Copy(line, ci - 1, Length(line)));

  def format_loader_error(self, error_message):
    line = self._line
    ci = 0 # TODO use actual position in line?
    
    location_1 = "in line(%d): %s" % (self._line_number, line)
    #" --> %s <-- %s" % (
    #  self._line_number, line[:ci - 2],
    #  line[ci - 1: ci], line[ci:])
      
    return "%s\n%s" % (location_1, error_message)

  # needs: state, statematches, matchset1
  # state: TLexerState
  def add_wildcard(self, statematches, state, setout_state):
    # see careful1.txt for why it _needs_ an extra state just for the wildcard, and cannot just "fix up" the previous state

    # remember the nodes to fix up the case
    # grammar "a[0]*" input "a" only must match!

    # however, the self-transitions are not in yet.
   
    
    transitions = self._lexer_states.states[state]
     
    for cix in range(len(self._matchset1)):
      if not self._matchset1[cix]:
        continue
        
      transitions.is_wildcard_tainted = True
      transitions.transitions[cix] = state # .newstate  # repeater rule
      # transitions.modified = True
      
      # nextstate = prevtrans[cix];
              
      # this state is in the need_set_token_states list, so it's token will be set later

    # make sure the state ends up in the list too, since they still need to have their token set.

    statematches.add(state)

  def string_transitions_internal(self, statenr, trans2, force_detail):
    global STATE_INVALID
    # i: Integer;
    # newstateToCount: TStringList;
    # newstate: TLexerState;
    # cnt: Integer;
    # majority: Boolean;
    # hasmajority: TLexerState;
    # res: string;
    
    res = ""

    if (not trans2.is_modified) and (not force_detail):
      res = res + "S%d: (unchanged); " % (statenr)
      return res
          
    # trans2.is_modified = False

    res = res + "\r\nS%d:\r\n" % (statenr)
          
    majority = False
    new_state_to_count = {}
    for i in range(len(self._lexer_states.states)):
      new_state_to_count[i] = 0
          
    for i in range(len(trans2.transitions)):
      newstate = trans2.transitions[i] # .newstate
      if newstate <> STATE_INVALID:
        cnt = new_state_to_count[newstate] + 1
        if cnt > 50:
          majority = True
          hasmajority = newstate

        new_state_to_count[newstate] = cnt

    if majority:
      for i in range(len(trans2.transitions)):
        newstate = trans2.transitions[i] # .newstate;
              
        if (newstate <> STATE_INVALID) and (newstate <> hasmajority):
          res = res + '  %s -> S%d\r\n' % (phonychr(i), trans2.transitions[i])
          
      for i in range(len(trans2.transitions)):
        newstate = trans2.transitions[i] # .newstate;
              
        if (newstate <> STATE_INVALID) and (newstate == hasmajority):
          res = res + '  majority -> S%d\r\n' % (hasmajority)
          break

    else: # not majority
      for i in range(len(trans2.transitions)):
        # newstate
        if (trans2.transitions[i] <> STATE_INVALID):
          res = res + "  %s -> S%d\r\n" % (phonychr(i), trans2.transitions[i])

    if trans2.fallback_token <> INVALID:
      res = res + "  DONE -> found %s\r\n" % repr(trans2.fallback_token)

    if trans2.is_wildcard_tainted: # ?
      res = res + "  (wildcard tainted)\r\n"

    res = res + "\r\n"
    return res

  def string_transitions(self, x_state):
    trans2 = self._lexer_states.states[x_state]
    return self.string_transitions_internal(x_state, trans2, False)
  
  #        
  def apply_matchset1_part_reuse(
    self,
    x_state, # TLexerState
    statematches, # i/o TLexerStateMatches
    cix, # integer
    is_wildcard, # Boolean;
    recursestates, # i/o TLexerStateMatches
  ):
    global STATE_INVALID
    global STATE_INITIAL
    
    trans2 = self._lexer_states.states[x_state]
    okuseagain = (trans2.is_wildcard_tainted == False) # TODO maybe nothing in the path to here can be wildcard tainted.
    if is_wildcard and not okuseagain:
      # TODO check if all the states are the same
      # okuseagain = True
      return
      
    if not okuseagain:
      sys.stderr.write(self.format_loader_error("transition already used"))
      # trans2.is_modified = True
      
      s = self.string_transitions_internal(x_state, trans2, True)
      sys.stderr.write(s)
      sys.stderr.write("\n")
      sys.stderr.write("I mean the transition to " + phonychr(cix) + "\n")
      
      # if it is  already set, this means another regex is overriding this one. example:
              
      # hello         EX1
      # [a-z][a-z]*   EX2
                  
      # this would match both, and since the latter comes later, it shall not overwrite the detailed one. XXX
                  
      # however, there is yet another case, if the input string is 
      #   heli
      # then is needs to 'copy' from EX2

      if trans2.fallback_token == INVALID: # needs to be unset, still
        # trans2.FallbackToken = self.declare_symbol()
        pass

    else: # ok to use state again
      anextstate = trans2.transitions[cix] #.newstate;
      assert((anextstate <> STATE_INITIAL) and (anextstate <> STATE_INVALID)) # not back to initial! (at least not when not matched a token)
      statematches.add(anextstate)
      
      if is_wildcard == True: # ok to use state again, and wildcard
        # comment2
        
        recursestates.add(anextstate)

  #
  def apply_matchset1_part(
    self,
    statematches, # i/o TLexerStateMatches
    recursestates, # i/o TLexerStateMatches
    x_state, # TLexerState;
    cix, # Integer; 
    anewstate, # i[/o]: TLexerState;
    is_wildcard #: Boolean
  ):
    global STATE_INVALID
    global STATE_INITIAL
    
    trans2 = self._lexer_states.states[x_state]
    
    if len(trans2.transitions) <= cix:
      while len(trans2.transitions) <= cix:
        trans2.transitions.append(STATE_INVALID)
        
      trans2.transitions[cix] = STATE_INVALID 
      #trans2.is_modified = True
      
    
    # .newstate
    if trans2.transitions[cix] == STATE_INVALID: # still invalid, i.e. unset
      if anewstate == STATE_INVALID: # just one for the set is enough. or zero.
        anewstate = self.new_state()
            
        if (anewstate <> STATE_INVALID) and is_wildcard:
          # this means a new state was created for the wildcard and needs to be made self-referencing and included in the
          # to-be-token-set list
              
          self.add_wildcard(statematches, anewstate, x_state)

        trans2 = self._lexer_states.states[x_state] # refresh # not really needed in python
                
        # Writeln('new state ii: ' + inttostr(anewstate));
                
      # PrintStates;
      # PrintTransitionsInternal(x_state, trans2^);
                        
      # .newstate
      trans2.transitions[cix] = anewstate
      #trans2.is_modified = True
      # Writeln('new state1: ' + inttostr(trans2.transitions[cix]));
      anextstate = trans2.transitions[cix] # .newstate
      assert((anextstate <> STATE_INITIAL) and (anextstate <> STATE_INVALID)) # not back to initial! (at least not when not matched a token)
      statematches.add(anextstate)
    else: # trans2.transitions[cix] != STATE_INVALID
      self.apply_matchset1_part_reuse(x_state, statematches, cix, is_wildcard, recursestates)

  #        
  def apply_matchset1(
    self,
    statematches, # i/o TLexerStateMatches; 
    is_wildcard, # boolean
    wildcard_clean_new_state = 0, # : TLexerState = 0
  ):
    # this will, taking into accout the current states, 
    # add transitions to them as mentioned in the matchset1

    #{$IFDEF DEBUG_LEXER_LOAD}
    #Writeln('  ... applying');
    #{$ENDIF DEBUG_LEXER_LOAD}

    assert(self._matchset1.is_empty() == False)
          
    curstates = statematches.copy()
    statematches.clear()
    
    #print "curstates", curstates

    for csi in range(len(curstates)):
      # this iterates through all the previous states 
      # which need their "next pointer" adjusted
            
      x_state = curstates[csi]
      anewstate = STATE_INVALID
      
      recursestates = TLexerStateMatches()
            
      for cix in range(len(self._matchset1)): # this iterates through every possible char here, i.e. abcdef... *)
        if not self._matchset1[cix]:
          continue

        self.apply_matchset1_part(statematches, recursestates, x_state, cix, anewstate, is_wildcard)
            
      # recursestates now contains the states that were already present and thus need to be hijacked in order to do the wildcard thing correctly
            
      if len(recursestates) > 0:
        #{$IFDEF DEBUG_LEXER_LOAD}
        #Writeln('recursing... ');
        #PrintStateList(recursestates, 'recursing...');
        #{$ENDIF DEBUG_LEXER_LOAD}
        self.apply_matchset1(recursestates, is_wildcard) # wildcardCleanNewState: TLexerState
        # recursestates inout
        for rix in range(len(recursestates)):
          #print "recursestates", rix, recursestates[rix]
          if recursestates[rix] != STATE_INVALID:
            statematches.add(recursestates[rix])
            
          #{$IFDEF DEBUG_LEXER_LOAD}
          #Writeln(' ... done adding to statematches: ' + inttostr(recursestates[rix]));
          #{$ENDIF DEBUG_LEXER_LOAD}
  #

  def process_line_part(
    self,
    line, # string
    ci # integer
  ):
    if True:
      startrange = -1
      
      assert(ci < len(line))
      
      c = line[ci]
      ci = ci + 1
        
      if True:
        if c == '[':
          # note that this can also contain double single quotes, but they have no impact as far as I see.
          
          self._matchset1.clear()
          do_invert = False
          #{$IFDEF DEBUG_LEXER_LOAD}
          #Write('REGEXP: ');
          #{$ENDIF DEBUG_LEXER_LOAD}
          if not (ci < len(line)):
            raise ELexerLoadError(self.format_loader_error('syntax error (5)'))

          c = line[ci]
          if c == '^':
            #{$IFDEF DEBUG_LEXER_LOAD}
            #Write('REVERSE ');
            #{$ENDIF DEBUG_LEXER_LOAD}
            
            do_invert = True
            ci = ci + 1
            if not (ci < len(line)):
              raise ELexerLoadError(self.format_loader_error('syntax error (1)'))

            c = line[ci]
          
          while True:
            if (startrange == -1) and (c == '-') and (ci + 1 < len(line)): # range
              assert(ci > 1)
              startrange = ord(line[ci - 1]) 
              # note that this doesnt support the notation [1-], i.e. without end
              #   and not the notation [-1], i.e. without beginning
              
              # and it doesnt support ranges over special forms like "[:whitespace:]", 
              # which would be stupid anyway.
            else: # end of range, normal char to add to range
              if startrange <> -1: # actually end of range
                # endrange very very local
                endrange = ord(c)
                c = chr(startrange)
                while c <= chr(endrange):
                  self._matchset1.add(c, self._case_sensitive)
                  c = chr(ord(c) + 1)

                startrange = -1
              else: # normal char to add to range
                if c == ']':
                  raise ELexerLoadError(self.format_loader_error('probably invalid "]"'))
                  
                if c == "[":
                  if line[ci:ci + 14] == "[:whitespace:]":
                    ci = ci + 14 - 1
                    #print "LI", line[ci:]
                    
                    self._matchset1.add(" ", False)
                    self._matchset1.add("\t", False)
                    
                    # TODO make configurable:
                    #self._matchset1.add("\n", False)
                    
                    self._matchset1.add("\r", False)
                    
                    # TODO UTF-8 space thingies?
                    #self._matchset1.add(" ", False)
                  elif line[ci:ci + 11] == "[:newline:]":
                    ci = ci + 11 - 1
                    
                    self._matchset1.add("\n", False)
                  elif line[ci:ci + 8] == "[:utf8:]":
                    ci = ci + 8 - 1

                    for aai in range(128, 256):
                      self._matchset1.add(chr(aai), False)
                  else:
                    raise ELexerLoadError(self.format_loader_error('invalid special form, expected "[:whitespace:]", "[:newline:]" or "[:utf8:]"'))
                else:
                  self._matchset1.add(c, self._case_sensitive)
            
            ci = ci + 1
            if not (ci < len(line)):
              raise ELexerLoadError(self.format_loader_error('syntax error (1)'));

            c = line[ci]
            
            if c == "]":
              break

          ci = ci + 1
          
          # assert that at least one char was matched by rule
          #{$IFDEF DEBUG_LEXER_LOAD}
          #PrintMatchset1('matchset1: ');
          #{$ENDIF DEBUG_LEXER_LOAD}
          
          assert(not self._matchset1.is_empty())
          
          if do_invert == True:
            self._matchset1.invert()
            assert(not self._matchset1.is_empty())
          
          # prevStates = need_set_token_states
                    
          if ci < len(line):
            nextc = line[ci]
          else:
            nextc = "\0"
          
          if nextc == '*': # wildcard
            ci = ci + 1
            
            # first make sure that grammar "a[0]*b" yields grammar "ab" as well:
            
            rest = line[ci:]
            for setout_state in self._need_set_token_states:
              if setout_state not in self._wildcard_fixups:
                self._wildcard_fixups[setout_state] = rest
          
          self.apply_matchset1(self._need_set_token_states, nextc == '*')
          # needSetTokenStates.clear()
          
          if nextc == '*':
            if self._matchset1.is_empty():
              raise ELexerLoadError(self.format_loader_error('syntax error (5): wildcard after empty set'))
  
            if ci == 1: # (* FIXME or prevchar is '*' too *)
              raise ELexerLoadError(self.format_loader_error('syntax error (4)'))
            
            # AddWildcard(); done by apply_matchset1
            self._matchset1.clear()
            
        elif c == '*':
          # also done in the regexp part above.
          # not: self._matchset1.clear() in order to keep old one around to be able to match now (in AddWildcard)
          pass
        elif c == '\\': # \n, \r
          if ci >= len(line):
            raise ELexerLoadError(self.format_loader_error('syntax error: expected n or r, not nothing'))
          
          nextc = line[ci]
          if nextc in ['n', 'r']:
            self._matchset1.clear()
            
            if nextc == 'n':
              c = BackslashN
            elif nextc == 'r':
              c = BackslashR
            
            self._matchset1.add(c, self._case_sensitive)
            self.apply_matchset1(self._need_set_token_states, False) # this means that 'a'* doesnt work. use [a]* or add feature :)
            
          else:
            raise ELexerLoadError(self.format_loader_error('syntax error: expected n or r, not ' + PhonyChr(ord(nextc))))

          ci = ci + 1
        elif c == "\'":
          tmp_token_name = ""
          
          self._matchset1.clear()
          assert(ci < len(line))
          c = line[ci]
          numquotes = 0
          while (c <> "\'") or ((c == "\'") and ((ci + 1 < len(line)) and (line[ci + 1] == "\'"))):
            if ((c == "\'") and ((ci + 1 < len(line)) and (line[ci + 1] == "\'"))):
              # Writeln('  skip escaped quote...');
              ci = ci + 1
              c = line[ci]
              # continue; # next quote will be fetched
              # fall through
            
            if (c == "\'"): # some real quote, not a dupe
              numquotes = numquotes + 1
              
            #{$IFDEF DEBUG_LEXER_LOAD}
            #Writeln(' CHAR: ' + c);
            #{$ENDIF DEBUG_LEXER_LOAD}
            #//transitions.transitions[c]
            
            if self._token_name == '':
              tmp_token_name = tmp_token_name + c

            self._matchset1.clear()
            self._matchset1.add(c, self._case_sensitive)
            # self._need_set_token_states.clear()
              
            self.apply_matchset1(self._need_set_token_states, False) # this means that 'a'* doesnt work. use [a]* or add feature :)
            # self._need_set_token_states was changed now
            
            # TODO check a max length here to avoid all-too-obvious infinite loops on garbage data ? guess not.
            
            # TODO assert that at least one char was matched by rule
          
            ci = ci + 1
            if ci >= len(line):
              raise ELexerLoadError(self.format_loader_error('syntax error (2)'));
              
            c = line[ci]

          ci = ci + 1
          #{$IFDEF DEBUG_LEXER_LOAD}
          #Writeln('DONE CHARS');
          #{$ENDIF DEBUG_LEXER_LOAD}
          
          if self._token_name == '': # default token name is the beginning of the match
            self._token_name = tmp_token_name

          # debug: PrintStateList(self._need_set_token_states, '... switched state to ');
        else:
          raise ELexerLoadError(self.format_loader_error("syntax error (3), char is \"" + c + "\""))
        
    return ci
    
  def process_line(self, line):
    #  ci: Integer; (* char index *)
    #  trans2: PLexerStateTrans;
    #  csi: Integer; // state index
    #  state: TLexerState;
    
    self._line = line # for error messages
    
    global STATE_INITIAL
    global STATE_INVALID
    
    self._wildcard_fixups = {}

    state = STATE_INITIAL # start state, line by line
    self.process_line_1(line, state)

    # now fix up the states that were the set-out for a wildcard
    # those need to end in the token

    while len(self._wildcard_fixups) > 0:
      fixups = self._wildcard_fixups.copy()
      self._wildcard_fixups = {}

      for state, non_wildcard_line_parts in fixups.items():
        assert(state not in (STATE_INITIAL, STATE_INVALID))
        trans2 = self._lexer_states.states[state]
      
        if non_wildcard_line_parts != "": # still something left
          self.process_line_1(non_wildcard_line_parts, state)
        else: # nothing left: nice, but still need to set token
          trans2 = self._lexer_states.states[state]
        
          if trans2.fallback_token == INVALID:
            trans2.fallback_token = self.declare_symbol()
    
  def process_line_1(self, line, state):
    global STATE_INITIAL
    global STATE_INVALID

    ci = 0

    self._need_set_token_states.clear()
    self._need_set_token_states.add(state)
      
    self._matchset1.clear()
      
    while ci < len(line):
      ci = self.process_line_part(line, ci)
      
    # in the new state, match the token.

    assert(len(self._need_set_token_states) > 0)
    for csi in range(len(self._need_set_token_states)):
      state = self._need_set_token_states[csi]

      if state == STATE_INITIAL:
        raise ELexerLoadError('syntax error: needs to match at least something: ' + line);

      if state == STATE_INVALID:
        raise ELexerLoadError('syntax error: returned invalid: ' + line);
        
      trans2 = self._lexer_states.states[state]
        
      if trans2.fallback_token == INVALID:
        trans2.fallback_token = self.declare_symbol()
        #print "token", trans2.fallback_token, self._token_definitions
        # trans2.is_modified = True
      else:
        # do not overwrite FallbackToken since its matching something else already
        pass
    
        
        
    # debug: PrintStates(False);
    
  def load(self, stream, case_sensitive = False):
    xi = -1
    
    self._case_sensitive = case_sensitive

    self._lexer_states = TLexerStates()
    self._lexer_states.is_case_sensitive = case_sensitive
    self._lexer_states.states.append(TLexerStateTransition()) # invalid
    self._lexer_states.states.append(TLexerStateTransition()) # initial
    
    #self.print_states(False)
  
    lines = stream.readlines()
    
    # token_definitions
    
    self._line_number = 0
    for line in lines:
      line = line.strip()
      
      self._line_number = self._line_number + 1
      self._line = line
      
      if line == "": # empty line
        continue
      
      if line.startswith("#"): # commented out
        continue
      
      self._token_name = ""

      line = line.strip()

      xi = -1

      # reverse-find whitespace
      for i in range(len(line) - 1, -1, -1):
        if line[i] in [" ", "\t"]:
          xi = i
          break

      if xi > -1:
        self._token_name = line[xi + 1:]
        line = line[: xi]
        line = line.strip()
      
      # line now is only the regexp
      line = line.strip()
      # ClearTransitions(transitions);
      
      #print 'line:', line # debug
      
      self.process_line(line)
      
    return self._lexer_states
      
if __name__ == "__main__":
  import cStringIO
  import toe.symbol
  
  generator_stream = cStringIO.StringIO()
  generator_stream.write("""
  'NAMESPACE'
  
  """)
  generator_stream.seek(0)
  
  table_1 = toe.symbol.table()
  generator = TLexerGenerator(table_1)
  
  lexer_states = generator.load(generator_stream, False)
  assert(len(lexer_states) > 2) # initial, invalid
  
  print len(lexer_states)
  assert(set(table_1.keys()) == set([toe.symbol.intern("NAMESPACE")]))
