"""
A handful of utility functions to make XML manipulation slightly tidier in
the rest of the code.
"""

import textwrap
import xml.dom.minidom

def getParentDocument(el):
    """
    """
    if el is None:
        return None
    if isinstance(el, xml.dom.minidom.Document):
        return el
    else:
        return getParentDocument(el.parentNode)
    

def addChildNode(parentEl, name, atts=None):
    """ Create a child node of the given 'parent' node.
    
        @param parentEl: The parent XML element
        @type parentEl: `xml.dom.minidom.Element`
        @param name: The name of the child element
        @keyword atts: A dict of attributes to apply to the new child 
            element. All values must be a type that can converted to
            a string.
    """
    el = xml.dom.minidom.Element(name)
    if atts is not None:
        for k,v in atts:
            if v is not None:
                el.setAttribute(k,str(v))
    parentEl.appendChild(el)
    return el


def copyAttributes(el, obj, atts, default=None):
    """ Create XML attributes on an XML element for a set of an object's 
        attributes. The object's attributes must be types that can be
        converted to strings.
        
        @param el: The XML element to which to add the attributes
        @type el: `xml.dom.minidom.Element`
        @param obj: A Python object
        @param atts: A list/tuple of attribute names
        @keyword default: A default value for attributes not present in the
            object. If `None`, the missing attribute is skipped.
    """
    for att in atts:
        val = getattr(obj, att, default)
        if val is not None:
            el.setAttribute(att, str(val))
            
            
def addTextNode(parentEl, text, width=70, indent="\t\t"):
    """
    """
    doc = getParentDocument(parentEl)
    t = doc.createTextNode(("\n%s" % indent).join(textwrap.wrap(text, width)))
    parentEl.appendChild(t)


def getText(parentEl):
    """
    """
    rc = []
    for node in parentEl.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ' '.join(rc)


    