import gst
import gtk
import gobject
import goocanvas

class ElementModel(gobject.GObject):
    "GstElement Model"
    
    def __init__(self, name=None, element=None, description=None):
        if not element:
            element = gst.Element(name)
        gobject.GObject.__init__(self)
        
        self.name = name
        self.description = description

        #element.connect("element-added", self._elementAddedCb)
        #element.connect("element-removed", self._elementRemovedCb)
        
        #create widget 
        #TODO: draw pads
        self.widget = goocanvas.GroupView()
        
        box = goocanvas.Rect(x=100, y=100, width=100, height=66,
                                    line_width=3, stroke_color="black",
                                    fill_color="grey", radius_y=5, radius_x=5)
        text = goocanvas.Text(x=150, y=133, width=80, text=description, 
                            anchor=gtk.ANCHOR_CENTER, font="Sans 9")
        self.widget.add_child(box)
        self.widget.add_child(text)
        #draw pads
        #need to attach signals and events here
        self.connect("button_press_event", self._onButtonPress)

    def onButtonPress(self, view, event):
        "update widget for drag move"
#        self.widget.translate(newx-dragx, newy-dragy)
        print "clikced!"

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
        self.bin = bin
        
    # actions possible, DON'T update UI here
    # CONTROLLER

    def addElement(self, element):
        self.bin.add(element)
    
    def removeElement(self, element):
        self.bin.remove(element)
        

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
