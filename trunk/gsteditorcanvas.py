import goocanvas

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
    
    def makeNewElement(self, name, factory):
        "Creates a new Gst element and draws it on the canvas"
        element = factory.create(name)
        desc = factory.get_description()
        #need some kind of workaround for bins and pipelines here
        self.pipeline.addElement(element)
        
        elementmodel = gsteditorelement.ElementModel(element.get_name(), 
                                        element, desc)
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
    