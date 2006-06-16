#!/usr/bin/env python

# TODO support "holes" in the text? (diff support)
# TODO intellisense signal
# TODO horizontal scrolling
# ("virtual" word wrapping?)

import pygtk
pygtk.require("2.0")
import gtk
import exceptions
import gobject
import cStringIO
import pango

class TEditModel(gtk.TreeModel):
  pass
  
class TEditStore(gtk.TreeStore):
  pass

INT_MAX = 2**31 - 1

class TCellRendererEditLineClass(getattr(gobject, "GObjectMeta", type)):
  def __new__(cls, name, bases, dct):
    ret = type.__new__(cls, name, bases, dct)
    
    gobject.type_register(ret)
    return ret

class TCellRendererEditLineSelection(gobject.GObject):
  __gtype_name__ = "TCellRendererEditLineSelection"
  def __init__(self):
    gobject.GObject.__init__(self)
    self._start = 0
    self._end_exclusive = 0
    self._style = "block" # weird-underline, underline, rectangle
    #self._color = 0 # palette index
    
  def set_start(self, value):
    self._start = value
    self._changed()
    
  def set_end_exclusive(self, value):
    self._end_exclusive = value
    self._changed()
    
  #def set_color(self, value):
  #  self._color = value
  #  self._changed()
    
  def _changed(self):
    # TODO emit signal on self
    pass
    
  start = property(lambda self: self._start, set_start)
  end_exclusive = property(lambda self: self._end_exclusive, set_end_exclusive)
  #color = property(lambda self: self._color, set_color)

# possibility of blending out line parts?
# don't use the same cell renderer in _multiple_ editviews!
class TCellRendererEditLine(gtk.GenericCellRenderer):
  __gtype_name__ = "TCellRendererEditLine"
  __gproperties__ = {
    "text": (gobject.TYPE_STRING,
       "text", 
       "the line of text",
       "", # default
       gobject.PARAM_READWRITE),
      
    # font
    # font-desc
    # scale
  }
  __gsignals__ = {
    "edited": (gobject.SIGNAL_RUN_LAST,
      gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_STRING)),
  }
  
  # TODO tabstops?
       
  def __init__(self):
    gtk.GenericCellRenderer.__init__(self)
    
    self.__text = ""
    self.__path = None
    self.__new_text = ""
    self.__width = 5
    self.__height = 5
    self.__selections = [] # index = id
    self.__initial_highlighter_state = 0 # INVALID
    self.__is_current_instruction = False
    self.__is_breakpoint = False
    self.__is_diff_old = False
    self.__is_diff_new = False
    self.__is_diff_modification = False
    self.__has_caret_currently = False
    self.__is_unresolved_breakpoint = False
    self.__is_disabled_breakpoint = False
    self.__formatter = None
    self.props.xalign = 0.0
    self.props.yalign = 0.5
    self.props.xpad = 2
    self.props.ypad = 2
    # width_chars
    # wrap_width
    
    # fixed_size
    
    self.add_selection(TCellRendererEditLineSelection())
    self.add_selection(TCellRendererEditLineSelection())
    self.add_selection(TCellRendererEditLineSelection())
    self.add_selection(TCellRendererEditLineSelection())

    self._clipboard_selection = self.get_selection(0) # bottom-most because it's a block
    self._error_hint_selection = self.get_selection(1)
    self._search_result_selection = self.get_selection(2)
    
    # brace-finding, ctrl+click:
    self._reference_selection = self.get_selection(3)
    
    # "block" # weird-underline, underline, rectangle
    self._search_result_selection.style = "rectangle"
    self._clipboard_selection.style = "block"
    self._error_hint_selection.style = "weird-underline"
    self._reference_selection.style = "underline"
    
    self.__font = pango.FontDescription()
    self.__layout = None

    # self.do_style_set(self.get_style())
  
  def _ensure_layout(self, widget):
    if self.__layout != None:
      return self.__layout
      
    # self.__layout = self.create_pango_layout("XYZ!/\\#[]()%\"'`|&{}²")
    # SIGH
    self.__layout = widget.create_pango_layout(self.__text)
    self.__layout.set_single_paragraph_mode(True)
    # pango_layout_set_ellipsize
    # pango_layout_set_wrap (layout, PANGO_WRAP_CHAR)
    
    return self.__layout

    # TODO pixmap buffer?
    
  # TODO on style set: get font + font size: calc width height
  # TODO use
  def do_style_set(self, what):
    style = what # self.get_style()
    self.__font = style.font_desc
    self.queue_resize()
    print "TCellRendererEditLine.style-set"
    #self.chain(what)
    
  def add_selection(self, selection1): 
    assert(selection1 not in self.__selections)
    self.__selections.append(selection1)
    
  def get_selection(self, index):
    return self.__selections[index]
    
  def get_selections(self):
    return self.__selections[:]
    
  #def remove_selection(self): useful? no.
    
  def do_get_property(self, property1):
    if property1.name == "text":
      return self.__text
    elif property1.name == "font-desc":
      return self.__font
    elif property1.name == "font":
      return self.__font.to_string()
    else:
      raise exceptions.AttributeError, "unknown property %s" % property1.name
      
  def do_set_property(self, property1, value):
    if property1.name == "text":
      # note that this currently also disallows tab (bad)
      self.__text = "".join([x for x in value if ord(x) >= 32])
      if self.__formatter != None:
        self.__formatter.source_stream.reset()
        self.__formatter.source_stream.write(self.__text)
        self.__formatter.source_stream.seek(0)
        
      # "self.queue_draw()"
    elif property1.name == "font-desc":
      self.__font = value
    elif property1.name == "font":
      self.__font = pango.FontDescription(value)
    else:
      raise exceptions.AttributeError, "unknown property %s" % property1.name
      
    # changed.
    
  def on_get_size(self, widget, cell_area):
    self.__layout = None
    self._ensure_layout(widget)

    size = self.__layout.get_pixel_size() # extents?
    
    self.__width = self.props.xpad * 2 + size[0]
    self.__height = self.props.ypad * 2 + size[1]
    
    return 0, 0, self.__width, self.__height
    
    # Please note that the values set in width and height, as well as those in x_offset and y_offset are inclusive of the xpad and ypad properties.
    # If cell_area is not NULL, fills in the x and y offsets (if set) of the cell relative to this location.
    
    # pango_context_get_metrics
    # pango_font_metrics_get_approximate_char_width
    
  def on_text_editing_done(self, widget):
    # self.__new_text = ""
    # self.stop_editing(False) # cancelled?
    # path = g_object_get_data (G_OBJECT (entry), GTK_CELL_RENDERER_TEXT_PATH);
    # self.emit("edited", 0, path, self.__new_text)
    pass
    
  def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
    self.__path = path
    self.__new_text = self.__text
    pass
    
  def on_render(self, window, widget, background_area, cell_area, expose_area, flags):
    x_offset, y_offset, item_width, item_height = self.on_get_size(widget, cell_area)
    
    # pango_layout_set_width (layout,
    #             (cell_area->width - x_offset - 2 * cell->xpad) * PANGO_SCALE)
                                

    self.__layout = None
    self._ensure_layout(widget)
    
    r = gtk.gdk.Rectangle(0, 0, self.__width - self.props.xpad, self.__height - self.props.ypad)
    gc = window.new_gc()
    r.x = r.x + cell_area.x
    r.y = r.y + cell_area.y
    r.width = r.width - self.props.xpad
    r.height = r.height - self.props.ypad
    
    draw_rect = cell_area.intersect(r)
    draw_rect = expose_area.intersect(draw_rect)

    background_color_name = None
    
    style = widget.get_style()
    if background_color_name != None:
      gc.set_rgb_fg_color(widget.style_get_property(background_color_name))
      window.draw_rectangle(gc, True, r.x, r.y, r.width, r.height)
    
    #   pango_layout_get_pixel_extents (layout, NULL, &rect);
    # gtk_widget_create_pango_layout
    # pango_attr_list_new
    # pango_layout_set_single_paragraph_mode    
    # pango_attr_font_desc_new
    # pango_layout_set_attributes
    
    # paint_layout
    # TODO -> formatter
    
    style.paint_layout(window, gtk.STATE_NORMAL, True, None, widget, "cellrenderereditline", r.x, r.y, self.__layout)
    
    if self.__formatter != None:
      self.__formatter.state = self.__initial_highlighter_state
      prev_i = 0
      
      while not self.__formatter.eof:
        i = self.__formatter.source_stream.tell()
        token = self.__formatter.token

        is_keyword = False        
        if token == self.__formatter.NONE: # reached EOF before finding something useful
          is_keyword = False
        elif token == self.__formatter.INVALID: # unknown token
          is_keyword = False
        else:
          is_keyword = True

        # prev_i..i : highlight

        try:
          self.__formatter.consume()
          # TODO import ELexerEofError
        except ELexerEofError, e:
          break

  def on_activate(self, event, widget, path, background_area, cell_area, flags):
    pass
    
  def on_start_editing(self, event, widget, path, background_area, cell_area, flags):
    pass
    
  def set_formatter(self, value):
    self.__formatter = value
    if value != None:
      self.__formatter.source_stream = cStringIO.StringIO()
      
    # ?
    
  # for formatting
  formatter = property(lambda self: self.__formatter, set_formatter)

# cell1_1 = gtk.CellRendererText()  # doesn't use my font either
cell1_1 = TCellRendererEditLine()

model_1 = gtk.TreeStore(int, str, str)


tree_view_1 = gtk.TreeView()
tree_view_1.set_model(model_1)
tree_view_1.append_column(gtk.TreeViewColumn("text", cell1_1, text = 1))

tree_view_1.show()

hbox_1 = gtk.HBox()
hbox_1.pack_start(tree_view_1, True, True)
hbox_1.show()

window_1 = gtk.Window()
window_1.add(hbox_1)
window_1.connect("destroy", lambda x: gtk.main_quit())
window_1.show()

f = file("verne.txt", "r")
lineno = 0
for line in f.readlines():
  lineno = lineno + 1
  line = line[:-1]
  iter = model_1.append(None)
  model_1.set_value(iter, 0, lineno)
  model_1.set_value(iter, 1, line)

f.close()


gtk.main()
