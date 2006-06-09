import gnomecanvas

import gsteditorelement

class GstEditorCanvas(gnomecanvas.Canvas):
    """
    This class visually describes the state of the main GST pipeline of a
    GstEditor object.  
    """
    
    def __init__(self):
        "Create a new GstEditorCanvas."
        gnomecanvas.Canvas.__init__(self)
        
        # create a main pipeline to contain all elements
        self.pipeline = gsteditorelement.PipelineModel()
     
    def makeNewElement(self, name, factory):
        "Creates a new Gst element and draws it on the canvas"
        element = factory.make(name)
        #need some kind of workaround for bins and pipelines here
        self.pipeline.addElement(element)
        raise NotImplementedError
    
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
    
    def testMe(self):
        "just a simple set of tests"
        
        #test1 initialize a window with a canvas
        
        #test2 draw a new element
        
        #test3 reposition the element
        
        #test4 delete the element
        
        #test5 draw two elements and connect them
        
        #test6 delete the connector
        
        #test7 delete element with connector
        
        #test8 move element and update connectors