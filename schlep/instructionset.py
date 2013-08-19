"""
"""
from collections import OrderedDict, Sequence
from importlib import import_module
from numbers import Number
from xml.dom import minidom

import xmlhelpers

#===============================================================================
# Decorators for simplifying the definition of instruction set items.
#===============================================================================

def operator(instructionSet, name=None, cost=None):
    def decorator(target):
        opname = name if name is not None else target.__name__
        setattr(target, 'cost', cost)
        setattr(target, 'isConditional', False)
        setattr(target, 'isOperator', True)
        setattr(target, 'isTerminator', False)
        setattr(target, 'isLiteral', False)
        setattr(target, 'opname', opname)
        instructionSet[opname] = target
        return target
    return decorator


def conditional(instructionSet, name=None, cost=None):
    def decorator(target):
        opname = name if name is not None else target.__name__
        setattr(target, 'cost', cost)
        setattr(target, 'isConditional', True)
        setattr(target, 'isOperator', False)
        setattr(target, 'isTerminator', False)
        setattr(target, 'isLiteral', False)
        setattr(target, 'opname', opname)
        instructionSet[opname] = target
        return target
    return decorator


def terminator(instructionSet, name=None, cost=None):
    def decorator(target):
        opname = name if name is not None else target.__name__
        setattr(target, 'cost', cost)
        setattr(target, 'isConditional', False)
        setattr(target, 'isOperator', False)
        setattr(target, 'isTerminator', True)
        setattr(target, 'isLiteral', False)
        setattr(target, 'opname', opname)
        instructionSet[opname] = target
        return target
    return decorator



#===============================================================================
# 
#===============================================================================

class InstructionSet(OrderedDict):
    """ A set of SCHLEP Operators, Conditionals, and/or Terminators. Its
        contents can be accessed by name or by index. Out-of-bounds indices
        are put back in range by modulus.
    """
    
    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop("name", None)
        super(InstructionSet, self).__init__(*args, **kwargs)
        self.__clearCache__()


    def __clearCache__(self):
        """
        """
        self._functions = self.values()
        self._operators = None
        self._conditionals = None
        self._terminators = None

        
    def __reindex__(self):
        """
        """
        self.__clearCache__()
        for k,v in self.iteritems():
            if v.isConditional:
                self._conditionals[k] = v
            elif v.isTerminator:
                self._terminators[k] = v
            else:
                self._operators[k] = v
                
        
    def __delitem__(self, k):
        """od.__delitem__(y) <==> del od[y]"""
        super(InstructionSet, self).__delitem__(k)
        self.__clearCache__()


    def __getitem__(self, k):
        """x.__getitem__(y) <==> x[y]"""
        if isinstance(k, Number):
            return self.getByIndex(k)
        return super(InstructionSet, self).__getitem__(k)


    def __setitem__(self, k, v):
        """od.__setitem__(i, y) <==> od[i]=y"""
        super(InstructionSet, self).__setitem__(k, v)
        self.__clearCache__()


    def __str__(self):
        """x.__str__() <==> str(x)"""
        return " ".join(self.keys())

    def __repr__(self):
        """ """
        if self.name is not None:
            return "<InstructionSet %s: %s>" % (self.name, self.keys())
        return "<InstructionSet: %s>" % self.keys()


    def __eq__(self, other):
        return str(self) == str(other)
    

    def clear(self):
        """od.clear() -> None.  Remove all items from od."""
        super(InstructionSet, self).clear()
        self.__clearCache__()


    def copy(self):
        """od.copy() -> a shallow copy of od"""
        result = super(InstructionSet, self).copy()
        return result


    @classmethod
    def fromkeys(cls, *args, **kwargs):
        """OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S.
        If not specified, the value defaults to None.
        """
        raise NotImplementedError("InstructionSet has no fromkeys()")


    def get(self, k, d=None):
        """D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."""
        if isinstance(k, Number):
            return self.getByIndex(k)
                
        return super(InstructionSet, self).get(k, d)


    def pop(self, *args):
        """od.pop(k[,d]) -> v, remove specified key and return the corresponding
        value.  If key is not found, d is returned if given, otherwise KeyError
        is raised.

        """
        result = super(InstructionSet, self).pop(*args)
        self.__clearCache__()
        return result


    def popitem(self):
        """od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        """
        result = super(InstructionSet, self).popitem()
        self.__clearCache__()
        return result


    def setdefault(self, *args):
        """od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d if k not in od"""
        result = super(InstructionSet, self).setdefault(*args)
        self.__clearCache__()
        return result


    def update(self, *args, **kwargs):
        """ Combine another InstructionSet with this one, changing any
            identically-named instructions.
        """
        super(InstructionSet, self).update(*args, **kwargs)
        self.__clearCache__()


#===============================================================================
# 
#===============================================================================
    
    def operators(self):
        """ Retrieve all Operators in the InstructionSet.
        """
        if self._operators is None:
            self.__reindex__()
        return self._operators
        
        
    def conditionals(self):
        """ Retrieve all Conditionals in the InstructionSet.
        """
        if self._conditionals is None:
            self.__reindex__()
        return self._conditionals
    
    
    def terminators(self):
        """ Retrieve all Terminators in the InstructionSet.
        """
        if self._terminators is None:
            self.__reindex__()
        return self._terminators
    
    
    def getByIndex(self, idx):
        """ Returns the instruction corresponding to an index. If the index
            is larger than the number of instructions, it wraps around.
        """
        return self._functions[idx % len(self)]

     
    def extend(self, d):
        """ Append a set of instructions onto the InstructionSet. Unlike
            `update()`, this does not replace existing keys, only adds new
            ones.
        """
        if isinstance(d, dict):
            for k, v in d.iteritems():
                if k not in self:
                    self[k] = v
        elif isinstance(d, Sequence):
            for v in d:
                self[v.name] = v
        else:
            raise TypeError("Incompatible type for extend(): %s" % type(d))


    def mget(self, *args):
        """ Get multiple instructions from the InstructionSet.
        """
        return [self[name] for name in args]
            
    
    def index(self, k):
        """ Returns the index of an Instruction.
        """
        return self.keys().index(k)

    
    def __add__(self, other):
        """
        """
        result = self.copy()
        result.extend(other)
        return result
        
    #===========================================================================
    # 
    #===========================================================================

    def toXml(self):
        """ Create an XML element representing the instruction set.
            
            @rtype: `xml.dom.minidom.Element`
        """
        parentEl = minidom.Element("InstructionSet")
        xmlhelpers.copyAttributes(parentEl, self, "name")
        xmlhelpers.copyAttributes(parentEl, self, ("defaultOperatorCost", 
                                                  "defaultConditionalCost", 
                                                  "defaultTerminatorCost"), 
                                 default=1.0)

        for name,instruction in self.iteritems():
            atts = {"name": name,
                    "module": instruction.__module__,
                    "cost": getattr(instruction, "cost", None)}
            if instruction.isConditional:
                xmlhelpers.addChildNode(parentEl, "conditional", atts)
            elif instruction.isTerminator:
                xmlhelpers.addChildNode(parentEl, "terminator", atts)
            else:
                xmlhelpers.addChildNode(parentEl, "operator", atts)
            
        return parentEl


    @classmethod
    def fromXml(self, el):
        """ Generate a new instruction set from a parsed XML 
            `<InstructionSet>` element. Each instruction must be in its
            module's `instructionSet`.
        
            @todo: Error handling. This version assumes well-formed XML and
                all instructions are available.
            @todo: Security. It is theoretically possible (albeit difficult
                and unlikely) to load malicious code.
        
            @param el: The XML element containing the instruction set.
            @type el: `xml.dom.minidom.Element`
            @rtype: `InstructionSet`
        """
        newSet = []
        for c in el.childNodes:
            nodeType = getattr(c, "nodeType", None)
            if nodeType == el.ELEMENT_NODE:
                opname = c.getAttribute("name")
                module = c.getAttribute("module")
                instruction = getattr(import_module(module), "instructionSet")[opname]
                newSet.append((opname, instruction))
        instructionSet = InstructionSet(newSet, name=el.getAttribute("name"))
        for att in ("defaultOperatorCost", "defaultConditionalCost", "defaultTerminatorCost"):
            if el.hasAttribute(att):
                setattr(instructionSet, att, float(el.getAttribute(att)))
            else:
                setattr(instructionSet, att, 1.0)
        return instructionSet



