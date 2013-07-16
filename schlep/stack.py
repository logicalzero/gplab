'''
Created on Oct 17, 2011

@author: stokes
'''

from collections import deque
import array

###############################################################################        
###############################################################################               


class Stack(object):
    """
    An abstracted representation of a stack of integers used by a SCHLEP 
    machine for either 'function pointers' (i.e. indices into its program) or
    data. This has been encapsulated in order for it to eventually be 
    replaced with native, C-based code, should performance require it.
    """
    
    def __init__(self):
        self.clear()

        
    def clear(self):
        """ Empties the stack. 
        """
        self.data = deque() # slightly faster than a normal list in this case
        self.stackEmpty = False
        self.overflow = False

    
    def __len__(self):
        return len(self.data)

        
    def __str__(self):
        return str(tuple(self.data))
    
    
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self))
    
        
    def push(self, val):
        """ Add a value to the top of the stack.
        """
        self.stackEmpty = False
        self.data.append(val)
        return True

        
    def pop(self):
        """ Remove and return the topmost value of the stack. The
            `stackEmpty` flag is set if an empty stack is popped.
        """
        if len(self) > 0:
            return self.data.pop()
        else:
            self.stackEmpty = True
            return 0

    
    def pop2(self):
        """ Remove and return the top two values from the stack."""
        if len(self.data) > 1:
            return (self.data.pop(), self.data.pop())
        elif len(self.data) > 0:
            self.stackEmpty = True
            return (self.data.pop(), 0)
        else:
            self.stackEmpty = True
            return (0,0)
        
        
    def peek(self):
        """ Returns the value of the topmost item in the data stack without 
            removing it.
        """
        if len(self.data) > 0:
            return self.data[-1]
        else:
            self.stackEmpty = True
            return 0

        
    def peek2(self):
        """ Returns the top two values of the data stack without removing them.
        """
        lenData = len(self.data)
        if lenData > 1:
            return self.data[-2:] #(self.data[-1], self.data[-2])
        elif lenData > 0:
            return (self.data[-1], 0)
        else:
            return (0,0)

        
    def poppedEmpty(self):
        """Returns True if an empty stack has been accessed (popped or peeked)."""
        return self.stackEmpty
        
        

###############################################################################        
###############################################################################               


class IntStack(Stack):
    """
    """
        
    def __init__(self, typecode='l'):
        self.typecode = typecode
        self.data = array.array(typecode)
        if typecode.islower():
            # lowercase type codes are signed
            self.maxVal = pow(2, self.data.itemsize * 8) / 2 - 1
            self.minVal = self.maxVal * -1 - 1
        else:
            self.minVal = 0
            self.maxVal = pow(2, self.data.itemsize * 8) - 1
    
    def clear(self):
        self.data = array.array(self.typecode)
        self.stackEmpty = False
        self.overflow = False


    def push(self, val):
        """ Add a value to the top of the stack.
        """
        self.stackEmpty = False
        try:
            self.data.append(val)
        except OverflowError:
            if val > self.maxVal:
                val = self.maxVal
            else:
                val = self.minVal
            self.data.append(val)

