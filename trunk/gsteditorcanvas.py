import goocanvas
import gtk

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
        
    def setPopup(self, popup):
        self.popup = popup
    
    def _onButtonPress(self, view, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                # pop up menu
                print "popup menu"
                self.popup.popup(None, None, None, event.button, event.time)
                return True
    
    def makeNewElement(self, name, factory):
        "Creates a new Gst element and draws it on the canvas"
        element = factory.create(name)
        desc = factory.get_longname()
        #need some kind of workaround for bins and pipelines here
        self.pipeline.addElement(element)
        
        elementmodel = gsteditorelement.ElementModel(element.get_name(), 
                                        element, desc)
        self.newelement = elementmodel
        self.root.add_child(elementmodel.widget)
        
    
    def moveElement(self, element):
        "Repositions an element on the canvas and re-draws connectors"
        raise NotImplementedError
        
    def deleteElement(self, element):
        "Remove an element and any connecting lines from the canvas"
        raise NotImplementedError
    
    def deleteConnector(self, connector):
        "Deletes a connecting line between a src and a sink"
        raise NotImplementedError
    
    def drawNewConnector(self, src, sink):
        "Draws a new connector from a src to a sink"
        raise NotImplementedError
    
    def onItemViewCreated(self, view, itemview, item):
        "Callback connects all other signals and events for new items"
        #this assumes any Group is an element.  this may need to change...
        if item.get_data("item_type") == "pad":
            print "connecting pad signals"
            pad = item.get_data("pad")
            itemview.connect("enter_notify_event", self.newelement.onPadEnter, pad)
            itemview.connect("leave_notify_event", self.newelement.onPadLeave, pad)
            itemview.connect("button_press_event", self.newelement.onPadPress, pad)
        if isinstance(item, goocanvas.Group):
            print "connected signal"
            itemview.connect("button_press_event", self.newelement.onButtonPress)
            itemview.connect("motion_notify_event", self.newelement.onMotion)
            itemview.connect("enter_notify_event", self.newelement.onEnter)
            itemview.connect("leave_notify_event", self.newelement.onLeave)