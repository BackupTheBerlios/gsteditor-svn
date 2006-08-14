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
                        
        #custom signal for pipeline state changes
        
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
                self.currentLink.raise_(None)
                self.currentLink.props.points = points
                self.root.add_child(self.currentLink)

                #make sure the link and the pad have refs to each other for
                # moves and updates
                self.currentLink.set_data("src", src)
                src.set_data("link", self.currentLink)

                self.currentLink.set_data("src_coords", src_coords)
                
                #now watch for these events so we can catch 
                self.linkHandlers = list()
                handler = view.connect("motion_notify_event", self._doDrag)
                self.linkHandlers.append(handler)
                
        print "handled drag"
        return True
        
        
    def _doDrag(self, view, target, event):
        "update link end point" 
        if self.currentLink:
            
            print "item coords: ", event.x, event.y
            newx,newy = self.convert_from_item_space(view, event.x, event.y)
            print "global coords: ", newx, newy

            src_coords = self.currentLink.get_data("src_coords")
            print "src coords: ", src_coords
            newpoints = goocanvas.Points([src_coords, (newx, newy)])
            self.currentLink.props.points = newpoints
            self.currentLink.raise_(None)
            return True
            
    def _stopDrag(self, view, target, event):
        "attaches or destroys a link when user lets go of mouse"
##        if self.currentLink:
##            #if it's over a pad, try to connect
##            #otherwise, destroy the link
        print "done dragging"
        child = self.root.find_child(self.currentLink)
        self.root.remove_child(child)
        del(self.currentLink)
        self.currentLink = None

        while len(self.linkHandlers):
            link = self.linkHandlers.pop()
            view.disconnect(link)
            print "removed link" + str(link)
        
        return True
    
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
        
        if item.get_data("item_type") == "pad":
            
            sig = itemview.connect("enter_notify_event", self.newelement.onPadEnter)
            self.newelement.signals.append((itemview,sig))

            sig = itemview.connect("leave_notify_event", self.newelement.onPadLeave)
            self.newelement.signals.append((itemview,sig))

            sig = itemview.connect("button_press_event", self._startDrag)
            self.newelement.signals.append((itemview, sig))

            # you don't do release events very often, we can put it from the start
            sig = itemview.connect("button_release_event", self._stopDrag)
            self.newelement.signals.append((itemview, sig))
            
        if item.get_data("item_type") == "element":
            sig = itemview.connect("button_press_event", self.newelement.onButtonPress)
            self.newelement.signals.append((itemview, sig))
            
            #TODO: move this so it's only set up after a click, saves cpu
            sig = itemview.connect("motion_notify_event", self.newelement.onMotion)
            self.newelement.signals.append((itemview, sig))
            
            sig = itemview.connect("button_release_event", self.newelement.onButtonRelease)
            self.newelement.signals.append((itemview, sig))
