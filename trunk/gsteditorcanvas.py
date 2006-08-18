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
        
        #stuff to handle link drag state
        self.currentLink = None

        
    def setPopup(self, popup):
        self.popup = popup
    
    def _onButtonPress(self, view, event):
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                # pop up menu
                self.popup.popup(None, None, None, event.button, event.time)
                return True
            
    def _onLinkClick(self, view, target, event):
        "handler for link clicks"
        self.pointer_ungrab(view, 0)
        print "clicked on a link"
            
    def _startDrag(self, view, target, event):
        "start a new link drag"
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 1:
                print "starting drag"
                                
                #find the src pad
                item = target.get_item()
                src = item.get_data("pad")
                x = item.get_property("center_x")
                y = item.get_property("center_y")
                src_coords = self.convert_from_item_space(view, x, y)
                to_coords = self.convert_from_item_space(view, event.x, event.y)
                
                #make the new link
                points = goocanvas.Points([src_coords, to_coords])
                self.currentLink = goocanvas.Polyline()
                self.currentLink.props.points = points

                #make sure the link has refs to the pad for
                # moves and updates
                self.currentLink.set_data("src", src)

                self.currentLink.set_data("src_coords", src_coords)
                self.currentLink.set_data("item_type", "link")
                
                self.root.add_child(self.currentLink)

                self.currentLink.raise_(None)
                
                #now watch for these events so we can catch 
                self.linkHandlers = list()
                handler = self.connect("motion_notify_event", self._doDrag)
                self.linkHandlers.append(handler)
                handler = self.connect("button_release_event", self._stopDrag, view)
                self.linkHandlers.append(handler)

        
        #ungrab so we can mouse over the other pads
        self.pointer_ungrab(view, 0)

        return True
        
        
    def _doDrag(self, view, event):
        "update link end point"
        
        if self.currentLink:
            src_coords = self.currentLink.get_data("src_coords")

            #TODO: remove this when goocanvas is fixed
            #      this is a hack to keep the link PolyLine from stealing
            #      the pointer focus
            (srcx, srcy) = src_coords
            if srcx < event.x :
                newx = event.x - 1
            else:
                newx = event.x + 1
            
            if srcy < event.y:
                newy = event.y - 1
            else:
                newy = event.y + 1
            
            sink_coords = (newx, newy)
            
            newpoints = goocanvas.Points([src_coords, sink_coords])
            self.currentLink.props.points = newpoints
            self.currentLink.raise_(None)
            self.currentLink.set_data("sink_coords", sink_coords)
            print "dragging"

        return False
            
    def _stopDrag(self, view, event, srcview):
        "attaches or destroys a link when user lets go of mouse"
        
        #if it's over a pad, try to connect
        #otherwise, destroy the link
        if self.hover:
            sinkpad = self.hover.get_data("pad")
            print "connecting to ", sinkpad.get_name()
            srcpad = self.currentLink.get_data("src")
            if srcpad.can_link(sinkpad):
                srcpad.link(sinkpad)
                srcpad.set_data("link", self.currentLink)
                sinkpad.set_data("link", self.currentLink)
                self.currentLink.set_data("sink", sinkpad)
                #TODO: tidy up the link drawing so that the endpoint is
                #      orthogonal and ends at the radius
            else:
                #TODO: indicate graphically that these pads can't link
                self._destroyLink()
        else:
            print "done dragging"
            self._destroyLink()


        while len(self.linkHandlers):
            link = self.linkHandlers.pop()
            view.disconnect(link)
            print "removed link" + str(link)
        
        return True
    
    def _destroyLink(self):
        "deletes a link"
        child = self.root.find_child(self.currentLink)
        self.root.remove_child(child)
        del(self.currentLink)
        self.currentLink = None
    
    def _setHover(self, view, target, event, item):
        "sets the pad currently under the mouse"
        self.hover = item
        print "hovering"
        return False

    def _unsetHover(self, view, target, event, item):
        "unsets the hover pad on leaving"
        self.hover = None
        print "hover unset"
        return False
    
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
        print "element deleted"
        return True
            
    def setPlayMode(self, mode):
        "sets the main pipeline to be playing or paused"
        if mode:
            self.pipeline.setPlaying()
        else:
            self.pipeline.setPaused()

    def getPlayMode(self):
        "returns the current pipeline state"
        return self.pipeline.getPlayMode()
    
    def onItemViewCreated(self, view, itemview, item):
        "Callback connects all other signals and events for new items"

        #set up a ref to the ItemView
        item.set_data("view", itemview)
        
        if item.get_data("item_type") == "pad":
            
            sig = itemview.connect("enter_notify_event", self.newelement.onPadEnter)
            self.newelement.signals.append((itemview,sig))
            
            #sets current hover pad so we can set up links
            sig = itemview.connect("enter_notify_event", self._setHover, item)
            self.newelement.signals.append((itemview, sig))

            sig = itemview.connect("leave_notify_event", self.newelement.onPadLeave)
            self.newelement.signals.append((itemview,sig))

            #unsets the hover pad
            sig = itemview.connect("leave_notify_event", self._unsetHover, item)
            self.newelement.signals.append((itemview, sig))

            sig = itemview.connect("button_press_event", self._startDrag)
            self.newelement.signals.append((itemview, sig))
            
        if item.get_data("item_type") == "element":
            sig = itemview.connect("button_press_event", self.newelement.onButtonPress)
            self.newelement.signals.append((itemview, sig))
            
            sig = itemview.connect("button_release_event", self.newelement.onButtonRelease)
            self.newelement.signals.append((itemview, sig))
            
        if item.get_data("item_type") == "link":
            sig = itemview.connect("button_press_event", self._onLinkClick)
            self.newelement.signals.append((itemview, sig))
            
        return True
