# Copyright (C) 2006 Brendan Howell
#
#   gstparamwin.py: gtk+ widget for GSTreamer elements.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import gtk
import gst
import gobject

class GstParamWin(gtk.Window):
    """this class provides a convenient Gtk+ widget that will pop open a
    non-modal window with widgets to control and adjust the parameters for
    any Gstreamer Element.  The module was designed as part of the Gstreamer
    Graphical Pipeline Editor."""
    
    def __init__(self, element=None):
        gtk.Window.__init__(self)
        
        if element:
            title = element.props.name + " - Parameters"
            self.set_title(title)
            self.element = element
            
        self.set_position(gtk.WIN_POS_MOUSE)
        self.set_default_size(380, 500)

        self.connect("delete-event", self.onDelete)
        
        self.vbox = gtk.VBox()
        self.vbox.set_border_width(15)
        self.scrollwin = gtk.ScrolledWindow()
        self.scrollwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scrollwin.add_with_viewport(self.vbox)
        self.add(self.scrollwin)
        
        #TODO: make this prettier
        self.vbox.pack_start(gtk.Label('Set Element Parameters'), expand=False,
                                        padding=10)
        
        proplist = gobject.list_properties(self.element)
        self.table = gtk.Table(len(proplist), 2)
        self.table.props.row_spacing = 5
        self.table.props.column_spacing = 5
        self.vbox.pack_start(self.table, expand=False, padding=10)
        
        count = 0
        for property in proplist:
            #skip any non readable params
            if not(property.flags & gobject.PARAM_READABLE):
                continue
            
            label = gtk.Label(property.name)
            label.set_alignment(1,0.5)
            self.table.attach(label, 0, 1, count, count+1)
            #TODO: tooltips using property.blurb
            
            if hasattr(property, "minimum") and hasattr(property, "maximum"):
                #guess that it's numeric - we can use an HScale
                value = self.element.get_property(property.name)
                adj = gtk.Adjustment(value, property.minimum, property.maximum)
                
                adj.connect("value_changed", self.onValueChanged, property)
                hscale = gtk.HScale(adj)
                hscale.set_value_pos(gtk.POS_RIGHT)
                
                #check for ints and change digits
                if not((property.value_type == gobject.TYPE_FLOAT) or
                        (property.value_type == gobject.TYPE_DOUBLE)):
                    hscale.set_digits(0)
                    
                self.table.attach(hscale, 1, 2, count, count+1)
                
            elif gobject.type_is_a(property.value_type, gobject.TYPE_BOOLEAN):
                #booleans get a toggle button
                tstate = self.element.get_property(property.name)
                if tstate:
                    button = gtk.ToggleButton("On")
                else:
                    button = gtk.ToggleButton("Off")
                button.set_active(tstate)
                button.set_size_request(40,30)
                button.connect("toggled", self.onToggled, property)
                self.table.attach(button, 1, 2, count, count+1)

            elif hasattr(property, "enum_class"):
                #for enumerated types, use a combobox
                choices = _getChoices(property)
                enum = self.element.get_property(property.name)
                
                combo = gtk.ComboBox(choices)
                cell = gtk.CellRendererText()
                combo.pack_start(cell, True)
                combo.add_attribute(cell, 'text', 0)
                combo.set_active(enum)

                combo.connect("changed", self.onComboBoxChanged, property)
                self.table.attach(combo, 1, 2, count, count+1)

            elif gobject.type_is_a(property.value_type, gobject.TYPE_STRING):
                #strings get a gtk.Entry widget
                entry = gtk.Entry()
                text = self.element.get_property(property.name)
                # ignore empty strings
                if text:
                    entry.set_text(text)
                
                entry.connect("changed", self.onEntryChanged, property)
                self.table.attach(entry, 1, 2, count, count+1)

            count += 1

    def onValueChanged(self, adj, property):
        "Update element parameter when slider is moved"
        #cast non float types as int
        if not((property.value_type == gobject.TYPE_FLOAT) or
                (property.value_type == gobject.TYPE_DOUBLE)):
            value = int(adj.get_value())
        else:
            value = adj.get_value()

        self.element.set_property(property.name, value)
        return True
    
    def onToggled(self, button, property):
        "Update element boolean parameter when button is toggled"
        tstate = button.get_active()
        self.element.set_property(property.name, tstate)
        if tstate:
            button.set_label("On")
        else:
            button.set_label("Off")
        return True

    def onComboBoxChanged(self, widget, property):
        "Change element parameter when the ComboBox value is adjusted"
        model = widget.get_model()
        iter = widget.get_active_iter()
        
        #we need to grab the actual enum value for non-serial values
        enum = model.get_value(iter, 1)
        self.element.set_property(property.name, enum)
                
    def onEntryChanged(self, widget, property):
        "update text parameter"
        self.element.set_property(property.name, widget.get_text())
        
    def onDelete(self, window, event):
        "Hide the window when the user closes it"
        self.hide()
        return True
    
def _getChoices(cls):
    """This method is a slightly modified version of the EnumType handler 
    from Gazpacho (http://gazpacho.sicem.biz/) as written by Johan Dahlin 
    (jdahlin@async.com.br).  It returns a sorted gtk.ListStore of columns with 
    the form: (name string, enum int value)"""
    
    choices = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT)
    if not hasattr(cls.enum_class, '__enum_values__'):
        raise UnsupportedProperty

    for enum in cls.enum_class.__enum_values__.values():
        choices.append((enum.value_name, enum))
    choices.set_sort_column_id(1, gtk.SORT_ASCENDING)
    return choices
