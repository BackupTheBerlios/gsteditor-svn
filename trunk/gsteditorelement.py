import gst
import gtk
import gobject
import goocanvas

class ElementModel(gobject.GObject):
    "GstElement Model"
    
    def __init__(self, name=None, element=None, description=None):
        if not element:
            self.element = gst.element_factory_make("fakesrc")
        else: 
            self.element = element
        gobject.GObject.__init__(self)
        
        self.name = name
        self.description = description

        #element.connect("element-added", self._elementAddedCb)
        #element.connect("element-removed", self._elementRemovedCb)
        
        #create widget 
        self.widget = goocanvas.Group()
        
        self.box = goocanvas.Rect(x=100, y=100, width=100, height=66,
                                    line_width=3, stroke_color="black",
                                    fill_color="grey", radius_y=5, radius_x=5)
        text = goocanvas.Text(x=150, y=133, width=80, text=description, 
                            anchor=gtk.ANCHOR_CENTER, font="Sans 9")
        self.widget.add_child(self.box)
        self.widget.add_child(text)
        #draw pads
        self.pads = self._makePads()
        self.hidePads()
        self.widget.add_child(self.pads)
        #TODO: attach pad signals and events here
        #self.connect("button_press_event", self._onButtonPress)

    def _makePads(self):
        "Creates a Group containing individual pad widgets"
        #TODO: color code based on caps
        pgroup = goocanvas.Group()
        lefty = 109
        righty = 109
        leftx = 109
        rightx = 191
        factory = self.element.get_factory()
        padlist = factory.get_static_pad_templates()
        count = 0
        for pad in padlist:
            count += 1
            if (pad.direction == gst.PAD_SINK):
                plug = goocanvas.Ellipse(center_x = leftx, center_y = lefty,
                                        radius_x = 4, radius_y = 4,
                                        fill_color = "yellow", line_width = 2,
                                        stroke_color = "black")
                pgroup.add_child(plug)
                lefty += 12
            elif (pad.direction == gst.PAD_SRC):
                plug = goocanvas.Ellipse(center_x = rightx, center_y = righty,
                                        radius_x = 4, radius_y = 4,
                                        fill_color = "blue", line_width = 2,
                                        stroke_color = "black")
                pgroup.add_child(plug)
                righty += 12
        print "total pads: " + str(count)
        
        # resize the Rect if there are more than 5 sinks or src pads
        if (righty > lefty):
            biggerside = righty
        else: 
            biggerside = lefty
        if biggerside > 157:
            self.box.set_property("height", biggerside - 103)
            
        return pgroup
        
    def hidePads(self):
        pass
        
    def showPads(self):
        pass

    def onButtonPress(self, view, target, event):
        "handle button clicks"
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 1:
                # Remember starting position for drag moves.
                self.drag_x = event.x
                self.drag_y = event.y
                return True

            elif event.button == 2:
                #TODO: pop up menu
                return True
            
            #TODO: double click to pop up element parameters window
        
    def onMotion(self, view, target, event):
        #drag move
        if event.state & gtk.gdk.BUTTON1_MASK:
            # Get the new position and move by the difference
            new_x = event.x
            new_y = event.y

            self.widget.translate(new_x - self.drag_x, new_y - self.drag_y)

            return True
        
    def onEnter(self, view, target, event):
        "display the pads when mousing over"
        self.showPads()
        
    def onLeave(self, view, target, event): 
        "hide the pads when mousing out"
        self.hidePads()
    
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
