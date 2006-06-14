import goocanvas

class ElementView(goocanvas.GroupView):
    "View component for a GstEditor element."
    
    def __init__(self, model=None):
        goocanvas.GroupView.__init__(self)
        
    