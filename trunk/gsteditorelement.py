import gst
import gtk
import gobject

class ElementModel(gobject.GObject):
    "GstElement Model"
    
    def __init__(self, name=None, element=None):
        if not element:
            element = gst.Element(name)
        gobject.GObject.__init__(self)

        element.connect("element-added", self._elementAddedCb)
        element.connect("element-removed", self._elementRemovedCb)


    def _elementAddedCb(self):
        raise NotImplementedError
    
    def _elementRemovedCb(self):
        raise NotImplementedError
    


class BinModel(ElementModel):
    """ GstBin Model """

    def __init__(self, name=None, bin=None):
        if not bin:
            bin = gst.Bin(name)
        ElementModel.__init__(self, name, bin)
        
    # actions possible, DON'T update UI here
    # CONTROLLER

    def addElement(self, element):
        self._object.add(element)
    
    def removeElement(self, element):
        self._object.remove(element)
        

    # Callbacks from gst.Bin, update UI here
    # VIEW
        
    def _elementAddedCb(self, bin, element):
        # create a ElementModel() to wrap the element added
        # display it
        raise NotImplementedError

    def _elementRemovedCb(self, bin, element):
        # find the widget associated with the element
        # remove it from UI
        raise NotImplementedError


class PipelineModel(BinModel):

    def __init__(self, name=None, pipeline=None):
        if not pipeline:
            pipeline = gst.Pipeline(name)
        BinModel.__init__(self, name, pipeline)
