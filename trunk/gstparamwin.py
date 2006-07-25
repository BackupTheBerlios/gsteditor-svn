import gtk
import gst

class GstParamWin(gtk.Window):
    """this class provides a convenient Gtk+ widget that will pop open a
    non-modal window with widgets to control and adjust the parameters for
    any Gstreamer Element."""
    
    def __init__(self, element=None):
        gtk.Window.__init__(self)
        
        if element:
            self.set_title(element.name)
            self.set_position(gtk.WIN_POS_MOUSE)