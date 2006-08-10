import pygtk
pygtk.require("2.0")

import pygst
pygst.require("0.10")

import gst
import gobject
import gtk
import gtk.glade
import gnome.ui

import gsteditorelement
import gsteditorcanvas


APPNAME="GstEditor"
APPVERSION="0.0.1"

MAINICON="arrow-icon.png"

class GstEditor:
  "GStreamer Graphical Pipeline Editor class" 
 
  def __init__(self,name=None):
    "Initialize a new GSTEditor"

    print gst.version_string()
    
    gnome.init(APPNAME, APPVERSION)
    self.name = name
    self.gladefile = "glade-sources/gsteditor.glade"
    self.widgets = gtk.glade.XML(self.gladefile, "gstEditorMainWin")
    self.mainwin = self.widgets.get_widget("gstEditorMainWin")
    
    #set default icon
    gtk.window_set_default_icon_from_file(MAINICON)
    
    #start up the canvas
    self.canvas = gsteditorcanvas.GstEditorCanvas()
    canvasSW = self.widgets.get_widget("canvasSW")
    canvasSW.add(self.canvas)

    #grab the status bar
    self.statusbar = self.widgets.get_widget("statusbar")

    #grab the play button
    self.playbutton = self.widgets.get_widget("togglebutton1")
    self.buttonHandler = self.playbutton.connect("toggled", self._setPlayMode)
    
    #connect buttons
    dict = { "destroyWindow": self._destroyWindow,
            "addElement": self._addElement,
            "loadFromFile": self._loadFromFile }
    self.widgets.signal_autoconnect(dict)
    
    #pass the popup menu to the canvas
    self.popwidgets = gtk.glade.XML(self.gladefile, "popupMenu")
    popup = self.popwidgets.get_widget("popupMenu")
    self.popwidgets.signal_autoconnect(self)
    self.canvas.setPopup(popup)
    
    #initialize status bar
    self._updatePlayModeDisplay() 
    
    #TODO: this is easy but ugly.  maybe move this to a gsteditorcanvas.py
    bus = self.canvas.pipeline.pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", self._busMessage)
    
    #self.updating keeps track of play button state to avoid looping
    self.updating = False
    
  def _loadFromFile(self, widget, event):
    "Load GST Editor pipeline setup from a file and initialize"
    raise NotImplementedError

  def _destroyWindow(self, widget):
    "Kills the app and cleans up"
    
    gtk.main_quit()
  
  def _addElementPopup(self, event):
    "Calls add element from a popup menu selection"
    self._addElement(None, event)

  def _delElementPopup(self, event):
    "Calls _delElement from a popup menu selection"
    self._delElement(None, event)

  def _addElement(self, widget, event):
    "Pops open a dialog and adds a GST element to the editor pipeline"
    
    diawidget = gtk.glade.XML(self.gladefile, "addElementDialog")
    dialog = diawidget.get_widget("addElementDialog")
    
    #build a list of all usable gst elements
    registry = gst.registry_get_default()
    registrylist = registry.get_feature_list(gst.ElementFactory)
    registrylist.sort(lambda x, y: cmp(x.get_name(), y.get_name()))    
    
    #TODO: it would be nice to have tooltips with full descriptions here

    #populate the tree
    treemodel = gtk.TreeStore(gobject.TYPE_PYOBJECT, gobject.TYPE_STRING)
    for item in registrylist:
        treemodel.append(None, [item, item.get_name()])

    #display view
    treeview = diawidget.get_widget("elementListView")
    treeview.set_model(treemodel)
    renderer = gtk.CellRendererText()
    column = gtk.TreeViewColumn("Element", renderer, text=1)
    treeview.append_column(column)
    treeview.show()
    
    rtn = dialog.run()
    
    if (rtn != gtk.RESPONSE_OK):
        print "no element selected"
    else:
        #find out which element was selected
        selected = treeview.get_selection()
        model, select = selected.get_selected()
        newfactory = model.get_value(select, 0)
        #give it to the canvas to instantiate and draw
        self.canvas.makeNewElement(None, newfactory)
    #clean up
    dialog.destroy()
  
  def _busMessage(self, bus, message):
    "handles special case where pipeline changes state without a button press"
    if not self.updating:
        self._updatePlayModeDisplay()
        
        mode = self.canvas.getPlayMode()

        #TODO: sort out wierdness and delays that causes this to be triggered
        # while state is propagating through the pipeline
        # maybe there is a way to filter messages
        
        #block emission of signal before updating the button
        self.playbutton.handler_block(self.buttonHandler)
        if mode == gst.STATE_PAUSED:
            self.playbutton.set_active(False)
        elif mode == gst.STATE_PLAYING:
            self.playbutton.set_active(True)
        self.playbutton.handler_unblock(self.buttonHandler)
    
  def _updatePlayModeDisplay(self):
    "updates the status bar with current pipeline state"
    cid = self.statusbar.get_context_id("current")

    self.statusbar.pop(cid)
    
    mode = self.canvas.getPlayMode()
    if mode == gst.STATE_NULL:
        self.statusbar.push(cid, "Pipeline Initialized")
    elif mode == gst.STATE_PAUSED:
        self.statusbar.push(cid, "Pipeline Paused")
    elif mode == gst.STATE_PLAYING:
        self.statusbar.push(cid, "Pipeline Playing")
    elif mode == gst.STATE_READY:
        self.statusbar.push(cid, "Pipeline Ready")
    elif mode == gst.STATE_VOID_PENDING:
        self.statusbar.push(cid, "Pipeline Void Pending")

  def _setPlayMode(self, widget):
    "Toggles the Play/Pause button."
    self.updating = True
    print "started setting play mode"
    playmode = widget.get_active()
    self.canvas.setPlayMode(playmode)
    self._updatePlayModeDisplay()
    print "done setting play mode"
    self.updating = False
    #TODO: change the widget to make the play mode more visually obvious
    #TODO: attach a signal to update the widget when the element changes state
    #      without a user clicking the button
        
  def __main__(self):
    gtk.main()
