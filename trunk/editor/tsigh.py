#!/usr/bin/env python

import pygtk
pygtk.require("2.0")
import gtk
import gobject

# sigh. this is needed only because of get_cell_info() being private in 
#   gtktreeviewcolumn

class TEditViewColumn(gobject.GObject):
  __gtype_name = "TEditViewColumn"
  def __init__(self, caption, cell_renderer, **kwargs):
    gobject.GObject.__init__(self)
    self.__parent = None
    self.__visible = True
    self.__caption = caption
    
    self.__cell_info = {}
    self.__cell_renderers = []
    if cell_renderer != None: 
      self.pack_start(cell_renderer)
      
      for key, value in kwargs.items():
        self.add_attribute(cell_renderer, key, value)
      
  def pack_start(self, cell_renderer, expand = True):
      self.__cell_renderers.append([cell_renderer, expand])
    
  # pack_end?
  
  def _notify_tree(self):
    #self.__parent.emit()
    # TODO
    pass
    
  def column_appended_to_edit(self, view):
    self.__parent = view
    self._notify_tree()
    
  def get_cell_renderers(self):
    for cell_renderer, expand in self.__cell_renderers:
      yield cell_renderer
    
  def get_cell_info(self, renderer):
    return self.__cell_info[renderer]
    
  def get_visible(self):
    return self.__visible
    
  def set_visible(self, value):
    self.__visible = value
    self._notify_tree()

  # attribute str
  # column int
  def add_attribute(self, cell_renderer, attribute, column):
    if cell_renderer not in self.__cell_info:
      self.__cell_info[cell_renderer] = {}
      
    self.__cell_info[cell_renderer][attribute] = column
    
  # set_attributes
  