#!/usr/bin/env python

class TToeToken:
  IGNORE = 0 # TODO move to base class?
  INVALID = 1 # TODO move to base class?
  
  YIELD = 10
  RETURN = 11
  IF = 12
  CLASS = 13
  TYPE = 14
  WHILE = 15
  DO = 16
  FOR = 17
  NAMESPACE = 18
  ELSE = 19
  RAISE = 20
  EXCEPT = 21
  TRY = 22
  FINALLY = 23
  LABEL = 24
  GOTO = 25
  OUT = 26
  REF = 27
  ENSURES = 28
  REQUIRES = 29
  INVARIANTS = 30
  INHERITED = 31
  VIRTUAL = 32
  OVERRIDE = 33
  REINTRODUCE = 34
  TO = 35
  IN = 36
  SET = 37
  OPEN_BRACE = 38
  CLOSE_BRACE = 39
  #OPEN_BRACKET = 40
  #CLOSE_BRACKET = 41
  RECORD = 42
  PROPERTY = 43
  EVENT = 44
  CASE = 45
  OF = 46
  AT = 47
  PROTECTED = 48
  PUBLIC = 49
  COLON = 50
  SEMICOLON = 51
  LESS_THAN = 52
  LESS_OR_EQUAL = 53
  GREATER_THAN = 54
  GREATER_OR_EQUAL = 55
  COMPARER = 56
  NOT_EQUAL = 57
  EQUAL = 58
  PLUS = 59
  MINUS = 60
  POWER = 61
  STAR = 62
  SLASH = 63
  SHL = 64
  SHR = 65
  ROL = 66
  ROR = 67
  AND = 68
  OR = 69
  XOR = 70
  NOT = 71
  DIV = 72
  MOD = 73
  OTHERWISE = 74
  ASSIGNMENT = 75
  DOT = 76
  QUOTED_STRING = 77
  NUMBER = 78
  ID = 79
  NEWLINE = 80
  DISTINCT = 81
  LINE_COMMENT = 82
  AND_SO_ON = 83
  COMMA = 84

  def to_name(klass, value):
    for name_1 in dir(klass):
      x_value = getattr(klass, name_1)
      
      if x_value == value:
        return name_1
        
    return value
    
  to_name = classmethod(to_name)        
  