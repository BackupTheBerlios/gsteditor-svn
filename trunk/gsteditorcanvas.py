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
        self.connect("button_press_event", self.doEvent)
    
    def doEvent(self, widget, event=None):
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 1:
                # Remember starting position.
                self.remember_x = event.x
                self.remember_y = event.y
                print "clicked on" + event.__dict__
                return gtk.TRUE
            
        if event.type == gtk.gdk.MOTION_NOTIFY:
            if event.state & gtk.gdk.BUTTON1_MASK:
                # Get the new position and move by the difference
                new_x = event.x
                new_y = event.y

                widget.move(new_x - self.remember_x, new_y - self.remember_y)

                self.remember_x = new_x
                self.remember_y = new_y

                return gtk.TRUE
    
    def makeNewElement(self, name, factory):
        "Creates a new Gst element and draws it on the canvas"
        element = factory.create(name)
        desc = factory.get_longname()
        #need some kind of workaround for bins and pipelines here
        self.pipeline.addElement(element)
        
        elementmodel = gsteditorelement.ElementModel(element.get_name(), 
                                        element, desc)
        self.root.add_child(elementmodel.widget)
        
    def onItemViewCreated(self, itemview, item, event):
        print "element created"
    
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
    