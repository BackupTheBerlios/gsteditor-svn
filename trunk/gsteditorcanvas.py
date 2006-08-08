import goocanvas
import gtk
import gobject

import gsteditorelement

class GstEditorCanvas(goocanvas.CanvasView):
    """
    This class visually describes the state of the main GST pipeline of a
    GstEditor object.  
    """
    
    def __init__(self):
        "Create a new GstEditorCanvas."
        goocanvas.CanvasView.__init__(self)
        self.set_size_request(600, 450)
        self.set_bounds(0, 0, 1000, 1000)
        self.show()
        
        #set up the model 
        self.model = goocanvas.CanvasModelSimple()
        self.root = self.model.get_root_item()
        self.set_model(self.model)

        # create a main pipeline to contain all child elements
        self.pipeline = gsteditorelement.PipelineModel()
        
        #set callback to catch new element creation so we can set events
        self.connect("item_view_created", self.onItemViewCreated)
        
        #set callbacks for background clicks
        self.connect_after("button_press_event", self._onButtonPress)
        
        #make our custom signal for deleting elements
        gobject.signal_new("element_delete", gsteditorelement.ElementModel, 
                        gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                        (gobject.TYPE_PYOBJECT, gobject.TYPE_PYOBJECT))
        
    def setPopup(self, popup):
        self.popup = popup
    
    def _onButtonPress(self, view, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                # pop up menu
                self.popup.popup(None, None, None, event.button, event.time)
                return True
    
    def makeNewElement(self, name, factory):
        "Creates a new Gst element and draws it on the canvas"
        element = factory.create(name)
        desc = factory.get_longname()
        #need some kind of workaround for bins and pipelines here
        self.pipeline.addElement(element)
        elementmodel = gsteditorelement.ElementModel(element.get_name(), 
                                        element, desc, self.get_toplevel())
        self.newelement = elementmodel
        self.root.add_child(elementmodel.widget)
        self.newelement.connect("element_delete", self.onDeleteElement)
        
    def onDeleteElement(self, event, widget, element):
        "un-draws and deletes the element"
        child = self.root.find_child(widget)
        self.root.remove_child(child)
        self.pipeline.removeElement(element.element)
        del(element)
        return True
            
    def setPlayMode(self, mode):
        "sets the main pipeline to be playing or paused"
        if mode:
            self.pipeline.setPlaying()
        else:
            self.pipeline.setPaused()
    
    def onItemViewCreated(self, view, itemview, item):
        "Callback connects all other signals and events for new items"
        #this assumes any Group is an element.  this may need to change...
        if item.get_data("item_type") == "pad":
            
            sig = itemview.connect("enter_notify_event", self.newelement.onPadEnter)
            self.newelement.signals.append((itemview,sig))

            sig = itemview.connect("leave_notify_event", self.newelement.onPadLeave)
            self.newelement.signals.append((itemview,sig))

            sig = itemview.connect("motion_notify_event", self.newelement.onPadMotion)
            self.newelement.signals.append((itemview,sig))
            
            sig = itemview.connect("button_press_event", self.newelement.onPadPress)
            self.newelement.signals.append((itemview,sig))
            
        if isinstance(item, goocanvas.Group):
            sig = itemview.connect("button_press_event", self.newelement.onButtonPress)
            self.newelement.signals.append((itemview,sig))
            
            sig = itemview.connect("motion_notify_event", self.newelement.onMotion)
            self.newelement.signals.append((itemview,sig))