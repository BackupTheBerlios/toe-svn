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
from tsigh import TEditViewColumn

class TEditModel(gtk.TreeModel):
  pass
  
class TEditStore(gtk.TreeStore):
  pass

INT_MAX = 2**31 - 1

# class TCellRendererBreakpoint
# class TCellRendererFlag
# diff?
### class TCellRendererLineNumber = gtk.CellRendererText
# profiler info

# syntax highlighting!!!

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

class TCellRendererEditLineClass(getattr(gobject, "GObjectMeta", type)):
  def __new__(cls, name, bases, dct):
    ret = type.__new__(cls, name, bases, dct)
    
    gtk.widget_class_install_style_property(ret, (
      "search-result-selection-color", gtk.gdk.Color, "search result selection color",
      "the color to draw the search result marker in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "error-hint-selection-color", gtk.gdk.Color, "error hint selection color",
      "the color to draw the error hint marker in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "clipboard-selection-color", gtk.gdk.Color, "clipboard selection color",
      "the color to draw the selected text marker in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "reference-selection-color", gtk.gdk.Color, "reference selection color",
      "the color to draw the reference marker (brace finder, find references) in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "current-instruction-color", gtk.gdk.Color, "current instruction color",
      "the color to draw the current instruction marker in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "breakpoint-color", gtk.gdk.Color, "breakpoint color",
      "the color to draw the breakpoint marker in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "disabled-breakpoint-color", gtk.gdk.Color, "disabled breakpoint color",
      "the color to draw disabled breakpoint marker in",
      gobject.PARAM_READABLE))

    gtk.widget_class_install_style_property(ret, (
      "unresolved-breakpoint-color", gtk.gdk.Color, "unresolved breakpoint color",
      "the color to draw unresolved breakpoint marker in",
      gobject.PARAM_READABLE))

    gtk.widget_class_install_style_property(ret, (
      "careted-line-color", gtk.gdk.Color, "careted line color",
      "the color to draw the line that has the caret in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "diff-old-color", gtk.gdk.Color, "diff old color",
      "the color to draw the old version diff lines in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "diff-new-color", gtk.gdk.Color, "diff new color",
      "the color to draw the new version diff lines in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "diff-modification-color", gtk.gdk.Color, "diff modification color",
      "the color to draw the modified version diff lines in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "diff-context-color", gtk.gdk.Color, "diff modification color",
      "the color to draw the context lines in",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "keyword-color", gtk.gdk.Color, "keyword color",
      "the color to use for words that are keywords",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "directive-color", gtk.gdk.Color, "directive color (keywords only reserved in some contexts)",
      "the color to use for words that are directives",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "literal-color", gtk.gdk.Color, "color for literals",
      "the color to use for literals",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "comment-color", gtk.gdk.Color, "color for comments",
      "the color to use for comments",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "type-color", gtk.gdk.Color, "color for types",
      "the color to use for types",
      gobject.PARAM_READABLE))
    
    gtk.widget_class_install_style_property(ret, (
      "bad-color", gtk.gdk.Color, "color for bad syntax",
      "the foreground color to use for bad syntax",
      gobject.PARAM_READABLE))
    
    gobject.type_register(ret)
    return ret

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
    "search-result-selection-start": (gobject.TYPE_INT,
      "selection start",
      "the selection start, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "search-result-selection-end": (gobject.TYPE_INT,
      "selection end",
      "the selection end, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "error-hint-selection-start": (gobject.TYPE_INT,
      "selection start",
      "the selection start, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "error-hint-selection-end": (gobject.TYPE_INT,
      "selection end",
      "the selection end, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "clipboard-selection-start": (gobject.TYPE_INT,
      "selection start",
      "the selection start, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "clipboard-selection-end": (gobject.TYPE_INT,
      "selection end",
      "the selection end, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),

    "reference-selection-start": (gobject.TYPE_INT,
      "selection start",
      "the selection start, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
    
    "reference-selection-end": (gobject.TYPE_INT,
      "selection end",
      "the selection end, or 0",
      0, INT_MAX, 0,
      gobject.PARAM_READWRITE),
      
    "is-current-instruction": (gobject.TYPE_BOOLEAN,
      "current instruction?",
      "whether this line is the current instruction",
      False,
      gobject.PARAM_READWRITE),

    "is-breakpoint": (gobject.TYPE_BOOLEAN,
      "breakpoint?",
      "whether this line is a breakpoint",
      False,
      gobject.PARAM_READWRITE),
      
    "is-unresolved-breakpoint": (gobject.TYPE_BOOLEAN,
      "unresolved breakpoint?",
      "whether this line is a unresolved breakpoint",
      False,
      gobject.PARAM_READWRITE),

    "is-disabled-breakpoint": (gobject.TYPE_BOOLEAN,
      "disabled breakpoint?",
      "whether this line is a disabled breakpoint",
      False,
      gobject.PARAM_READWRITE),
      
    "is-diff-old": (gobject.TYPE_BOOLEAN,
      "diff old version",
      "whether this line is part of the old version of a diff",
      False,
      gobject.PARAM_READWRITE),

    "is-diff-new": (gobject.TYPE_BOOLEAN,
      "diff new version",
      "whether this line is part of the new version of a diff",
      False,
      gobject.PARAM_READWRITE),
    
    "is-diff-modification": (gobject.TYPE_BOOLEAN,
      "diff modification version",
      "whether this line is part of a common line of a diff with modifications",
      False,
      gobject.PARAM_READWRITE),
      
    "is-diff-context": (gobject.TYPE_BOOLEAN,
      "diff context",
      "whether this line is one of the context lines of a diff",
      False,
      gobject.PARAM_READWRITE),
      
    "has-caret-currently": (gobject.TYPE_BOOLEAN,
      "caret here?",
      "whether the caret is currently in this line", # current line is highlighted, so.....
      False,
      gobject.PARAM_READWRITE),
      
    "initial-highlighter-state": (gobject.TYPE_INT,
      "initial highlighter state",
      "the state of the formatter before entering this row",
      0, INT_MAX, 0,
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
    self.__is_diff_context = False
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
    self.__search_result_selection_color = self.style_get_property("search-result-selection-color")
    self.__error_hint_selection_color = self.style_get_property("error-hint-selection-color")
    self.__clipboard_selection_color = self.style_get_property("clipboard-selection-color")
    self.__reference_selection_color = self.style_get_property("reference-selection-color")
    self.__current_instruction_color = self.style_get_property("current-instruction-color")
    self.__breakpoint_color = self.style_get_property("breakpoint-color")
    self.__disabled_breakpoint_color = self.style_get_property("disabled-breakpoint-color")
    self.__unresolved_breakpoint_color = self.style_get_property("unresolved-breakpoint-color")
    self.__careted_line_color = self.style_get_property("careted-line-color")
    self.__diff_old_color = self.style_get_property("diff-old-color")
    self.__diff_new_color = self.style_get_property("diff-new-color")
    self.__diff_modification_color = self.style_get_property("diff-modification-color")
    self.__diff_context_color = self.style_get_property("diff-context-color")
    self.__keyword_color = self.style_get_property("keyword-color")
    self.__directive_color = self.style_get_property("directive-color")
    self.__literal_color = self.style_get_property("literal-color")
    self.__comment_color = self.style_get_property("comment-color")
    self.__bad_color = self.style_get_property("bad-color")
    self.__escape_color = self.style_get_property("escape-color")
    self.__type_color = self.style_get_property("type-color")
    self.__preprocessor_color = self.style_get_property("preprocessor-color")
    self.__block_delimiter_color = self.style_get_property("block-delimiter-color")
    self.__font = style.font_desc
    self.queue_resize()
    #print "STYLE"
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
    elif property1.name == "search-result-selection-start":
      return self._search_result_selection.start
    elif property1.name == "search-result-selection-end":
      return self._search_result_selection.end_exclusive
    elif property1.name == "error-hint-selection-start":
      return self._error_hint_selection.start
    elif property1.name == "error-hint-selection-end":
      return self._error_hint_selection.end_exclusive
    elif property1.name == "clipboard-selection-start":
      return self._clipboard_selection.start
    elif property1.name == "clipboard-selection-end":
      return self._clipboard_selection.end_exclusive
    elif property1.name == "reference-selection-start":
      return self._reference_selection.start
    elif property1.name == "reference-selection-end":
      return self._reference_selection.end_exclusive
    elif property1.name == "is-current-instruction":
      return self.__is_current_instruction
    elif property1.name == "is-breakpoint":
      return self.__is_breakpoint
    elif property1.name == "is-unresolved-breakpoint":
      return self.__is_unresolved_breakpoint
    elif property1.name == "is-disabled-breakpoint":
      return self.__is_disabled_breakpoint
    elif property1.name == "is-diff-old":
      return self.__is_diff_old
    elif property1.name == "is-diff-new":
      return self.__is_diff_new
    elif property1.name == "is-diff-modification":
      return self.__is_diff_modification
    elif property1.name == "is-diff-context":
      return self.__is_diff_context
    elif property1.name == "has-caret-currently":
      return self.__has_caret_currently
    elif property1.name == "initial-highlighter-state":
      return self.__initial_highlighter_state
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
    elif property1.name == "search-result-selection-start":
      self._search_result_selection.start = value
    elif property1.name == "search-result-selection-end":
      self._search_result_selection.end_exclusive = value
    elif property1.name == "error-hint-selection-start":
      self._error_hint__selection.start = value
    elif property1.name == "error-hint-selection-end":
      self._error_hint__selection.end_exclusive = value
    elif property1.name == "clipboard-selection-start":
      self._clipboard_selection.start = value
    elif property1.name == "clipboard-selection-end":
      self._clipboard_selection.end_exclusive = value
    elif property1.name == "reference-selection-start":
      self._reference_selection.start = value
    elif property1.name == "reference-selection-end":
      self._reference_selection.end_exclusive = value
    elif property1.name == "is-current-instruction":
      self.__is_current_instruction = value
    elif property1.name == "is-breakpoint":
      self.__is_breakpoint = value
    elif property1.name == "is-unresolved-breakpoint":
      self.__is_unresolved_breakpoint = value
    elif property1.name == "is-disabled-breakpoint":
      self.__is_disabled_breakpoint = value
    elif property1.name == "is-diff-old":
      self.__is_diff_old = value
    elif property1.name == "is-diff-new":
      self.__is_diff_new = value
    elif property1.name == "is-diff-modification":
      self.__is_diff_modification = value
    elif property1.name == "is-diff-context":
      self.__is_diff_context = value
    elif property1.name == "has-caret-currently":
      self.__has_caret_currently = value
    elif property1.name == "initial-highlighter-state":
      self.__initial_highlighter_state = value
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
    
    if False:
      pass
      #if self.__has_caret_currently == True:
      #  "careted-line-color"
      #if self.__is_current_instruction == True:
      #  background_color_name = "current-instruction-color"
    elif self.__is_disabled_breakpoint == True:
      background_color_name = "disabled-breakpoint-color"
    elif self.__is_unresolved_breakpoint == True:
      background_color_name = "unresolved-breakpoint-color"
    elif self.__is_breakpoint == True:
      background_color_name = "breakpoint-color"
    elif self.__is_diff_new == True:
      background_color_name = "diff-new-color"
    elif self.__is_diff_modification == True:
      background_color_name = "diff-modification-color"
    elif self.__is_diff_context == True:
      background_color_name = "diff-context-color"
    elif self.__is_diff_old == True:
      background_color_name = "diff-old-color"
    
    # self.__selections
    # take note of treeview's hover selection!!
    # self.__text
    
    #window.draw_pixbuf(draw_rect.x - r.x, draw_rect.y - r.y, draw_rect.x, draw_rect.y, draw_rect.width, draw_rect.height, ...)
    
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

# add header line? no, app does (mtime, file name, path, .....)

class TEditView(gtk.VBox):
  __gtype_name__ = "TEditView"
  
  def __init__(self, *args):
    gtk.Widget.__init__(self, *args)
    self.__columns = []
    self.__model = None
    self._expander_column = None  # None=first_visible
    self._cursor_path = None
    self._cursor_column = None
    self._cursor_cell = None
    # ? self._cursor_line_number = None

    self.__search_result_selection_color = None
    self.__error_hint_selection_color = None
    self.__clipboard_selection_color = None
    self.__reference_selection_color = None
    self.__current_instruction_color = None
    self.__breakpoint_color = None
    self.__disabled_breakpoint_color = None
    self.__unresolved_breakpoint_color = None
    self.__careted_line_color = None
    self.__diff_old_color = None
    self.__diff_new_color = None
    self.__diff_modification_color = None
    self.__diff_context_color = None
    self.__keyword_color = None
    self.__directive_color = None
    self.__literal_color = None
    self.__comment_color = None
    self.__bad_color = None
    self.__escape_color = None
    self.__preprocessor_color = None
    self.__block_delimiter_color = None
    self.__type_color = None

    self.__rows_reordered_handler_id = None
    self.__row_inserted_handler_id = None
    self.__row_has_child_toggled_handler_id = None
    self.__row_deleted_handler_id = None
    self.__row_changed_handler_id = None
    
    self._headers = gtk.HButtonBox()
    self._headers.show()
    
    self.__cursor_path = None

    self._drawing_area = gtk.DrawingArea()
    self._drawing_area.connect("expose-event", self.content_expose_event_cb)
    self._drawing_area.show()
    
    self.pack_start(self._headers, False, False)
    self.pack_start(self._drawing_area, True, True)
    
    # show/hide columns

  def set_headers_visible(self, value):
    if value == True:
      self._headers.show()
    else:
      self._headers.hide()
      
  def get_headers_visible(self):
    return self._headers.props.visible
      
  def column_notify_visible_cb(self, paramspec1):
    print "TODO"
    pass
    
  def __added_column(self, column1):
    column1.connect("notify::visible", self.column_notify_visible_cb, self)
    
  def __removed_column(self, column1):
    # TODO
    column1.disconnect_by_user_data("notify::visible", self)
    
  def append_column(self, column1):
    assert(column1 not in self.__columns)
    self.__columns.append(column1)
    self.__added_column(column1)
    self._rescale()
    
    return len(self.__columns)
    
  def get_column(self, index):
    try:
      return self.__columns[index]
    except:
      return None
      
  def get_columns(self):
    return self.__columns[:]

  def move_column_after(self, column1, base_column):
    self.remove_column(column1)
    position = self.__columns.index(base_column)
    position = position + 1
    self.insert_column(column1, position)
    self._rescale()
    
  def set_expander_column(self, column):
    self._expander_column = column
    self._rescale()
    
  def get_expander_column(self, column):
    return self._expander_column
    
  def insert_column(self, column1, position):
    assert(column1 not in self.__columns)
    if position == -1:
      self.append_column(column1, position)
      self.__added_column(column1)
    else:
      self.__columns.insert(position, column1)
      self._rescale()
      
    return len(self.__columns)
      
  # gtk_tree_view_insert_column_with_data_func
  # gtk_tree_view_insert_column_with_attributes
    
  def remove_column(self, column1):
    if column1 in self.__columns:
      self.__columns.remove(column1)
      if self._expander_column == column1:
        self._expander_column = None
      self.__removed_column(column1)
      self._rescale()
    
    return len(self.__columns)

  def scroll_to_point(self, tree_x, tree_y):
    # widget must be realized
    
    # TODO
    if tree_x != -1:
      # scroll
      pass
      
    pass

  def scroll_to_cell(self, path, column, use_align, row_align, col_align, offset = 0):
    # does not need to be realized yet
    
    # path == None: no vertical scrolling
    # column == None: no horizontal scrolling
    # row_align 0..1
    # col_align 0..1
    # use_align == False: do the least amount of work
    # If the cell is currently visible on the screen, nothing is done.
    
    pass

  def set_cursor(self, path, focus_column, start_editing):
    #self._cursor_path = 
    #self._cursor_column = 
    #self._cursor_cell = 
    pass
    # This function is often followed by gtk_widget_grab_focus (tree_view) in order to give keyboard focus to the widget.
    # Please note that editing can only happen when the widget is realized.
  
  def set_cursor_on_cell(self, path, focus_column, focus_cell, start_editing):
    #self._cursor_path = 
    #self._cursor_column = 
    #self._cursor_cell = 
    pass
    
  def get_cursor(self):
    return self._cursor_path, self._cursor_column
    #self._cursor_cell = 
    
  def set_model(self, value):
    if self.__model != None:
      self.__model.disconnect(self.__rows_reordered_handler_id)
      self.__model.disconnect(self.__row_inserted_handler_id)
      self.__model.disconnect(self.__row_has_child_toggled_handler_id)
      self.__model.disconnect(self.__row_deleted_handler_id)
      self.__model.disconnect(self.__row_changed_handler_id)
      
      self.__rows_reordered_handler_id = None
      self.__row_inserted_handler_id = None
      self.__row_has_child_toggled_handler_id = None
      self.__row_deleted_handler_id = None
      self.__row_changed_handler_id = None

    if value != None:
      self.__rows_reordered_handler_id = None
      self.__row_inserted_handler_id = None
      self.__row_has_child_toggled_handler_id = None
      self.__row_deleted_handler_id = None
      self.__row_changed_handler_id = None
  
    self.__model = value
    self._rescale()
    
  def _rescale(self):
    pass
    
  #def row_activated(self, path, column)
  
  def expand_all(self):
    pass
    
  def collapse_all(self):
    pass
    
  def expand_to_path(self, path):
    pass
    
  def expand_row(self, path, open_all):
    pass
    
  def collapse_row(self, path):
    pass
    # return True if row was collapsed

  def map_expanded_rows(self, function1):
    # calls a function on all expanded rows
    pass
  
  def row_expanded(self, path):
    # TODO
    return True
    
  # set_reorderable
  
  def get_path_at_pos(self, tree, x, y):
    path = None
    column = None
    cell_x = 0
    cell_y = 0
    return path, column, cell_x, cell_y
    
  def get_cell_area(self, path, column):
    #return x,y,w,h
    pass
    # if path is NULL, or points to a path not currently displayed, 
    # the y and height fields of the rectangle will be filled with 0.

  def get_background_area(self, path, column):
    # return x,y,w,h
    pass

  def get_visible_rect(self):
    # return x,y,w,h
    pass
    # Caller converts to widget coordinates with gtk_tree_view_tree_to_widget_coords()

  def get_visible_range(self):
    start_path = None
    end_path = None
    return start_path, end_path # True
    
  def get_bin_window(self):
    pass
    # gdkwindow
    
  def widget_to_tree_coords(self, wx, wy):
    tx = wx # unscroll
    ty = wy # unscroll
    return tx, ty

  def tree_to_widget_coords(self, tx, ty):
    wx = tx # scroll
    wy = ty # scroll
    return wx, wy

  # enable_model_drag_dest
  # enable_model_drag_source
  # unset_rows_drag_source
  # unset_rows_drag_dest
  # set_drag_dest_row/get
  # get_dest_row_at_pos
  # create_row_drag_icon
  
  def set_enable_search(self, enable_search):
    # typeahead, by typing
    pass

  def set_search_column(self, column_index):
    # MODEL column index
    pass
    
  # connect model's "rows-reordered"
  # connect model's "row-inserted"
  # connect model's "row-has-child-toggled"
  # connect model's "row-deleted"
  # connect model's "row-changed"
  
  def model_row_changed_cb(self, model, path, iter):
    pass
    
  def model_row_deleted_cb(self, model, path):
    pass
    
  def model_row_has_child_toggled_cb(self, model, path, iter):
    pass
    
  def model_row_inserted_cb(self, model, path, iter):
    pass
    
  def model_rows_reordered_cb(self, model, path, iter, new_order):
    """
    new_order : an array of integers mapping the current position 
                of each child to its old position before the re-ordering, 
                i.e. new_order[newpos] = oldpos.
    """
    pass
  
  def each_row_and_renderer(self, real_render = True):
    if self.model != None:
      y = 0
      for row in self.model:
        # TODO child nodes?

        y_max_height = 0
        for i_column in range(len(self.__columns)):
          column = self.__columns[i_column]
          # TODO invisible columns!
          if column.get_visible() == False:
            continue
          
          for renderer in column.get_cell_renderers(): 
            #renderer
            expose_area = gtk.gdk.Rectangle()
            background_area = gtk.gdk.Rectangle()
            cell_area = gtk.gdk.Rectangle() # TODO
            flags = 0
            
            info = column.get_cell_info(renderer)
            
            # column._gtk_tree_view_column_cell_render
            #info.attributes
            # renderer.
            
            for key, column in info.items():
              value = row[column]
              
              renderer.set_property(key, value)
              
            # TODO call cell data func, if any
            
            t_x, t_y, t_width, t_height = renderer.on_get_size(self._drawing_area, cell_area)

            cell_area.x = 0
            cell_area.y = y
            cell_area.width = t_width
            cell_area.height = t_height
            
            background_area = cell_area.copy() # TODO!
            
            if background_area.height > y_max_height:
              y_max_height = background_area.height
            
            if real_render == True:
              renderer.on_render(self._drawing_area.window, self, background_area, cell_area, expose_area, flags)
          
          #data = row[i_column]
          #print column, data
          
          # area output clipping
          # self.__cursor_path != None
          # gtk.draw_insertion_cursor(self._drawing_area, self._drawing_area.window, None, location, True, gtk.TEXT_DIR_LTR, False)
          
        y = y + y_max_height
  
  def content_expose_event_cb(self, widget, event):
    area = event.area
      
    print "expose", area.x, area.y, area.width, area.height
    
    self.each_row_and_renderer(True)
      
    return False

  # "hover selection"
  # "hover expand"
  # GtkTreeViewRowSeparatorFunc
  
  model = property(lambda self: self.__model, set_model)
  expander_column = property(lambda self: self._expander_column, set_expander_column)
  headers_visible = property(lambda self: self.get_headers_visible, set_headers_visible)

edit_view_1 = TEditView()

# tree columns that I can think of right now:
#   text
#   line number
#   blame annotation
#   mtime
#   breakpoint/current instruction icon
#   (expander)
# invisible:
#   lexer state at beginning of line

edit_view_1.model = gtk.TreeStore(int, str, str)

cell1 = TCellRendererEditLine()
# cell1 = gtk.CellRendererText()

column1 = TEditViewColumn("text", cell1, text = 1)
#column1 = gtk.TreeViewColumn("text", cell1, text = 1)

edit_view_1.append_column(column1)

edit_view_1.show()

# cell1_1 = gtk.CellRendererText() 
cell1_1 = TCellRendererEditLine()

tree_view_1 = gtk.TreeView()
tree_view_1.set_model(edit_view_1.model)
tree_view_1.append_column(gtk.TreeViewColumn("text", cell1_1, text = 1))

tree_view_1.show()

hbox_1 = gtk.HBox()
hbox_1.pack_start(edit_view_1, True, True)
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
  iter = edit_view_1.model.append(None)
  edit_view_1.model.set_value(iter, 0, lineno)
  edit_view_1.model.set_value(iter, 1, line)

f.close()


gtk.main()
