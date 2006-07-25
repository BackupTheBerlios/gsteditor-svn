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
        self.widget.add_child(self.pads)

    def _makePads(self):
        "Creates a Group containing individual pad widgets"
        #TODO: color code based on caps
        pgroup = goocanvas.Group()
        
        pgroup
        lefty = 109
        righty = 109
        leftx = 109
        rightx = 191
        factory = self.element.get_factory()
        templist = factory.get_static_pad_templates()

        #TODO: clean and optimize this loop
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
                tipbg = goocanvas.Rect(x = leftx - (tipwidth + 18), y = lefty - 8, height = 16,
                                        width = tipwidth, line_width = 1,
                                        stroke_color = "red", fill_color = "pink")
                tooltip.add_child(tipbg)
                tooltip.add_child(tiptext)
                tooltip.set_property("visibility", goocanvas.ITEM_INVISIBLE)
                lefty += 12
            elif (pad.get_direction() == gst.PAD_SRC):
                plug = goocanvas.Ellipse(center_x = rightx, center_y = righty,
                                        radius_x = 4, radius_y = 4,
                                        fill_color = "blue", line_width = 2,
                                        stroke_color = "black")
                tooltip = goocanvas.Group()
                #TODO: prettify the string to remove underscores and such
                tiptext = goocanvas.Text(x= rightx + 20, y = righty, font = "Sans 9",
                                        text=pad.get_name(), anchor=gtk.ANCHOR_W)
                #TODO: get a better width calculation
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
        
        pads = self.element.pads()
        padcount = 0
        for pad in pads:
            padcount += 1
        print "total pads: " + str(padcount)
        # resize the Rect if there are more than 5 sinks or src pads
        if (righty > lefty):
            biggerside = righty
        else: 
            biggerside = lefty
        if biggerside > 157:
            self.box.set_property("height", biggerside - 103)
            
        return pgroup
    
    def onPadEnter(self, view, target, event):
        "mouse over callback for pads"
        #highlight stroke color
        item = target.get_item()
        item.set_property("stroke_color", "green")
        pad = item.get_data("pad")
        #show tooltip
        tooltip = item.get_data("tooltip")
        tooltip.set_property("visibility", goocanvas.ITEM_VISIBLE)
        #tooltip.raise_(None)
        #TODO: set tooltip to be top layer (sort out raise_ and lower)
        return True
        
    def onPadLeave(self, view, target, event):
        "mouse-out callback for pads"
        #reset the stroke color
        item = target.get_item()
        item.set_property("stroke_color", "black")
        pad = item.get_data("pad")
        tooltip = item.get_data("tooltip")
        tooltip.set_property("visibility", goocanvas.ITEM_INVISIBLE)
        return True
        
    def onPadPress(self, view, target, event):
        item = target.get_item()
        if event.button == 1:
            # Remember starting position for drag moves.
            self.pad_drag_x = event.x
            self.pad_drag_y = event.y
            x1 = item.get_property("center_x")
            y1 = item.get_property("center_y")
            parent = item.get_parent()
            link = goocanvas.polyline_new_line(parent, x1, y1, event.x, event.y)
            item.set_data("link", link)
            print "drawing link"
            return True
        elif event.button == 3:
            #TODO: delete connector
            pass
        return True
    
    def onPadMotion(self, view, target, event):
        if event.state & gtk.gdk.BUTTON1_MASK:
            item = target.get_item()
            link = item.get_data("link")
            if link:
                print "dragging link"
                endpoint = link.points[1]
                endpoint.set_property("x", event.x)
                endpoint.set_property("y", event.y)
        return True

    def onButtonPress(self, view, target, event):
        "handle button clicks"
        if event.type == gtk.gdk.BUTTON_PRESS:
            #TODO: sort out raise_ and lower to make this work
            #self.widget.raise_()
            if event.button == 1:
                # Remember starting position for drag moves.
                self.drag_x = event.x
                self.drag_y = event.y
                return True

            elif event.button == 3:
                #TODO: pop up menu
                print "element popup"
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
            #TODO: double click to pop up element parameters window
        
    def onMotion(self, view, target, event):
        #drag move
        if event.state & gtk.gdk.BUTTON1_MASK:
            # Get the new position and move by the difference
            new_x = event.x
            new_y = event.y

            self.widget.translate(new_x - self.drag_x, new_y - self.drag_y)

            return True
    
    def _elementRemovedCb(self):
        raise NotImplementedError
    
    def _delete(self, event):
        "un-draws the element and cleans up for deletion"
        parent = self.widget.get_parent().get_parent()
        dialog = gtk.Dialog('Delete Element',
                     parent,  # the window that spawned this dialog
                     gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,                       
                     (gtk.STOCK_DELETE, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CLOSE))
        dialog.vbox.pack_start(gtk.Label('Are you sure?'))
        dialog.show_all()
        
        rtn = dialog.run()
        if (rtn != gtk.RESPONSE_OK):
            print "canceled delete"
        else:
            self.emit("element_delete", self.widget, self)
        #clean up
        dialog.destroy()

        pass
        
    def _configure(self, event):
        "opens up the config dialog to set element parameters"
        #TODO: make this a floating modal dialog
        print "configure element\n total parameters:"
        proplist = gobject.list_properties(self.element)
        print len(proplist)
        for property in proplist:
            print property.name + " " + property.value_type.name
            print "\tvalue: " + str(self.element.get_property(property.name))
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
