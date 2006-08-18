import gst
import gtk
import gtk.glade
import gobject
import goocanvas

import gstparamwin

class ElementModel(gobject.GObject):
    "GstElement Model"
    
    def __init__(self, name=None, element=None, description=None, window=None):
        if not element:
            self.element = gst.element_factory_make("fakesrc")
        else: 
            self.element = element
        gobject.GObject.__init__(self)
        
        self.name = name
        self.description = description
        
        #signals stores a list of attached signal handlers
        self.signals = list()

        #create widget 
        self.widget = goocanvas.Group()
        self.widget.set_data("item_type", "element")
        
        self.dragging = False
        
        self.mainwin = window
        
        self.box = goocanvas.Rect(x=100, y=100, width=100, height=66,
                                    line_width=3, stroke_color="black",
                                    fill_color="grey", radius_y=5, radius_x=5)
        text = goocanvas.Text(x=150, y=133, width=80, text=description, 
                            anchor=gtk.ANCHOR_CENTER, font="Sans 9")
        self.widget.add_child(self.box)
        self.widget.add_child(text)
        #draw pads
        self.pads = self._makePads()
        self.widget.add_child(self.pads)

    def setPlaying(self):
        "sets the element to playing"
        self.element.set_state(gst.STATE_PLAYING)

    def setPaused(self):
        "sets the element to paused"
        self.element.set_state(gst.STATE_PAUSED)

    def getPlayMode(self):
        "returns the current state of the element"
        (rtrn, current, pending) = self.element.get_state(gst.CLOCK_TIME_NONE)
        return current

    def _makePads(self):
        "Creates a Group containing individual pad widgets"
        #TODO: color code based on caps? 
        pgroup = goocanvas.Group()
        
        lefty = 109
        righty = 109
        leftx = 109
        rightx = 191
        factory = self.element.get_factory()
        templist = factory.get_static_pad_templates()

        for template in templist:
            #add any not yet existing pads using templates
            pad = self.element.get_pad(template.name_template)
            if not pad:
                pad = gst.pad_new_from_static_template(template, template.name_template)
                self.element.add_pad(pad)

            #draw the pads
            if (pad.get_direction() == gst.PAD_SINK):
                plug = goocanvas.Ellipse(center_x = leftx, center_y = lefty,
                                        radius_x = 4, radius_y = 4,
                                        fill_color = "yellow", line_width = 2,
                                        stroke_color = "black")
                tooltip = goocanvas.Group()
                tipwidth = 8 * len(pad.get_name())
                tiptext = goocanvas.Text(x= leftx - (tipwidth + 16), y = lefty, font = "Sans 9",
                                        text=pad.get_name(), anchor=gtk.ANCHOR_W)

                #TODO: get a better width calculation
                #width = tiptext.user_bounds_to_device()
                print "width = " + str(tiptext.get_property("width"))
                tipbg = goocanvas.Rect(x = leftx - (tipwidth + 18), y = lefty - 8, height = 16,
                                        width = tipwidth, line_width = 1,
                                        stroke_color = "red", fill_color = "pink")
                tooltip.add_child(tipbg)
                tooltip.add_child(tiptext)

                tooltip.props.visibility = goocanvas.ITEM_INVISIBLE
                lefty += 12
                
            elif (pad.get_direction() == gst.PAD_SRC):
                plug = goocanvas.Ellipse(center_x = rightx, center_y = righty,
                                        radius_x = 4, radius_y = 4,
                                        fill_color = "blue", line_width = 2,
                                        stroke_color = "black")
                tooltip = goocanvas.Group()

                text = pad.get_name()
                
                tiptext = goocanvas.Text(x= rightx + 20, y = righty, font = "Sans 9",
                                        text=pad.get_name(), anchor=gtk.ANCHOR_W)
                #TODO: get a better width calculation
                #print "tip width: " + str(tiptext.user_bounds_to_device())
                tipwidth = 8 * len(pad.get_name())
                tipbg = goocanvas.Rect(x = rightx + 16, y = righty - 8, height = 16,
                                        width = tipwidth, line_width = 1,
                                        stroke_color = "red", fill_color = "pink")
                tooltip.add_child(tipbg)
                tooltip.add_child(tiptext)
                tooltip.set_property("visibility", goocanvas.ITEM_INVISIBLE)
                righty += 12
                
            else:
                print "mystery pad:  " + pad.get_name()
            
            #add the pad widget to the group and set references
            plug.set_data("pad",pad)
            plug.set_data("item_type","pad")
            plug.set_data("tooltip", tooltip)
            pgroup.add_child(plug)
            pgroup.add_child(tooltip)
            pad.set_data("widget", plug)
        
        pads = self.element.pads()

        # resize the Rect if there are more than 5 sinks or src pads
        if (righty > lefty):
            biggerside = righty
        else: 
            biggerside = lefty
        if biggerside > 157:
            self.box.props.height = biggerside - 103
            
        return pgroup
    
    def onPadEnter(self, view, target, event):
        "mouse over callback for pads"
        #highlight stroke color
        item = target.get_item()
        item.set_property("stroke_color", "green")
        
        #show tooltip
        tooltip = item.get_data("tooltip")
        tooltip.set_property("visibility", goocanvas.ITEM_VISIBLE)

        #set tooltip to be top layer 
        #TODO: find out why this doesn't work right any more
        #      probably a goocanvas bug
        #tooltip.raise_(None)
        # for now just raise the whole widget
        self.widget.raise_(None)

        return True
        
    def onPadLeave(self, view, target, event):
        "mouse-out callback for pads"
        #reset the stroke color
        item = target.get_item()
        item.set_property("stroke_color", "black")

        tooltip = item.get_data("tooltip")
        tooltip.set_property("visibility", goocanvas.ITEM_INVISIBLE)
        return True

    def onButtonPress(self, view, target, event):
        "handle button clicks"
        if event.type == gtk.gdk.BUTTON_PRESS:
            # make this element pop to top
            self.widget.raise_(None)
            if event.button == 1:
                # Remember starting position for drag moves.
                self.drag_x = event.x
                self.drag_y = event.y
                self.dragging = True
                sig = view.connect("motion_notify_event", self.onMotion)
                self.dragsignal = (view, sig)
                return True

            elif event.button == 3:
                popup = gtk.Menu()

                configItem = gtk.ImageMenuItem("Configure Element")
                configimg = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
                configItem.set_image(configimg)
                configItem.connect("activate", self._configure)
                configItem.show()
                popup.attach(configItem, 0, 1, 0, 1)
                
                deleteItem = gtk.ImageMenuItem("Delete Element")
                deleteimg = gtk.image_new_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU)
                deleteItem.set_image(deleteimg)
                deleteItem.connect("activate", self._delete)
                deleteItem.show()
                popup.attach(deleteItem, 0, 1, 1, 2)
                
                popup.popup(None, None, None, event.button, event.time)
                return True

        #double clicks open the parameter editor window
        if event.type == gtk.gdk._2BUTTON_PRESS:
            self._configure(None)
        
    def onMotion(self, view, target, event):
        #drag move
        if self.dragging and (event.state & gtk.gdk.BUTTON1_MASK):
            # Get the new position and move by the difference
            new_x = int(event.x)
            new_y = int(event.y)

            self.widget.translate(new_x - self.drag_x, new_y - self.drag_y)
            
            #update the links
            for pad in self.element.pads():
                link = pad.get_data("link")
                if not link:
                    continue

                cview = view.get_canvas_view()

                widget = pad.get_data("widget")
                x = widget.props.center_x
                y = widget.props.center_y

                #if it's a src pad then the sink stays put, update src
                if (pad.get_direction() == gst.PAD_SRC):
                    sink_coords = link.get_data("sink_coords")
                    src_coords = cview.convert_from_item_space(view, x, y)
                    link.set_data("src_coords", src_coords)
                #otherwise the src stays put and we update the sink
                else:
                    src_coords = link.get_data("src_coords")
                    sink_coords = cview.convert_from_item_space(view, x, y)
                    link.set_data("sink_coords", sink_coords)
                
                newpoints = goocanvas.Points([src_coords, sink_coords])
                link.props.points = newpoints
                
        return True
    
    def onButtonRelease(self, view, target, event):
        "undo any dragging"
        self.dragging = False
        (sview, sig) = self.dragsignal
        sview.disconnect(sig)
    
    def _elementRemovedCb(self):
        raise NotImplementedError
    
    def _delete(self, event):
        "un-draws the element and cleans up for deletion"
        dialog = gtk.Dialog('Delete Element',
                     self.mainwin,  # the window that spawned this dialog
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,                       
                     (gtk.STOCK_DELETE, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_start(gtk.Label('Are you sure?'))
        dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        dialog.show_all()
        
        rtn = dialog.run()
        if (rtn != gtk.RESPONSE_OK):
            print "canceled delete"
        else:
            #delete the ItemView signals for the element and pad views
            for (view, signal) in self.signals:
                view.disconnect(signal)
                
            #TODO: check this to see if it's cleaning up signals etc.
            if hasattr(self, "paramWin"):
                del(self.paramWin)
            
            #tell the parent canvas to un-draw and clean up
            self.emit("element_delete", self.widget, self)
            
        dialog.destroy()

        pass
        
    def _configure(self, event):
        "opens up the config dialog to set element parameters"
        if not(hasattr(self,"paramWin")):
            self.paramWin = gstparamwin.GstParamWin(self.element)
        self.paramWin.show_all()
    
        return True
    

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

        self.pipeline = pipeline