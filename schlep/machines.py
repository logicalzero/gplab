"""
Different types of basic SCHLEP virtual machines.
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .environment import Environment

from .stack import Stack
from .program import Program



class Machine:
    """
    A simple virtual machine for running an instance of a Program. It has a
    single, integer data stack.
    """
    
    def __init__(self,
                 environment: "Environment",
                 program: Program,
                 runForever: bool = True,
                 clearData: bool = False,
                 trackCoverage: bool = True):
        """ Create a new Machine running the provided Program. Multiple 
            machines can refer to the same program.
            
            Note: Machines should typically be created via the environment
                with the method `Environment.createMachine()`

            :param environment: The container holding this Machine (and
                possibly others).
            :type environment: `Environment`
            :param program: The program that this machine will run.
            :type program: `Program`
            :param runForever: If `True` (default), the program starts over 
                when it reaches the end.
            :param clearData: If `True`, the stack is emptied when the 
                program restarts. `False` is the default.
        """
        self.program = program
        self.parent = environment
        self.runForever = runForever
        self.clearData = clearData
        self.dataStack = Stack()
        self.pointerStack = Stack()
        self.trackCoverage = trackCoverage
        if trackCoverage:
            self._codeCoverage = [False] * len(self.program)
        else:
            self._codeCoverage = []

        self.currentPointer = 0
        self.running = True
        self.stackEmpty = False
        self.missingTerminator = False
        self.fitness = 0

        self.reset()


    def reset(self):
        """ Sets the virtual machine back to its initial state.
        """
        self.dataStack.clear()
        self.pointerStack.clear()
        self.currentPointer = 0
        self.running = True
        self.stackEmpty = False
        self.missingTerminator = False
        if self._codeCoverage:
            self._codeCoverage = [False] * len(self.program)
        self.fitness = 0

                
    def pushFP(self):
        """ Store the current position in the machine's SCHLEP program.
        """
        self.pointerStack.push(self.currentPointer)


    def popFP(self):
        """ Restore the previous position in the machine's SCHLEP program.
            The program will either end or restart if the pointer stack is
            empty, depending on the runForever variable.
        """
        self.currentPointer = self.pointerStack.pop()
        if self.pointerStack.poppedEmpty():
            if not self.runForever:
                self.running = False
            elif self.clearData:
                self.dataStack.clear()
        
        
    def step(self):
        """ Execute one instruction (if the program has not stopped). 
        """
        if self.running or self.runForever:
            if self._codeCoverage:
                self._codeCoverage[self.currentPointer] = True
            result = self.program[self.currentPointer](self)
            # Functions or 'true' conditionals return True; advance one
            # token. 'false' conditionals return False; go to Else branch.
            # Terminators return None.
            if result is True:
                self.currentPointer += 1
            elif result is False:
                self.currentPointer = self.program.getElse(self.currentPointer)
            
            # Has program reached the end, but was unterminated?
            # This is very likely in a randomly generated and/or mutated
            # program.    
            if self.currentPointer < 0 or self.currentPointer > len(self.program):
                self.missingTerminator = True
                self.currentPointer = 0
                

#############################################################################

class TuringMachine(Machine):
    """
    A variant of SCHLEP machines containing two data stacks, essentially 
    creating the 'tape' of a Turing machine. One stack is active at a time 
    and accessed via the standard 'dataStack' property.
    """
    
    def __init__(self,
                 environment: "Environment",
                 program: Program,
                 runForever: bool = True,
                 clearData: bool = False,
                 trackCoverage: bool = True):
        Machine.__init__(self, environment, program, runForever, clearData, trackCoverage)
        self.activeStackNum = 0
        self.stacks = (Stack(), Stack())
        self.dataStack = self.stacks[0]


    def stackToggle(self):
        """ Changes which data stack is active.
        """
        self.changeStack((self.activeStackNum & 1) ^ 1)


    def changeStack(self, stackNum: int):
        """ Explicitly changes the active stack. Since there are only two, any 
            even number enables stack 0; any odd number enables stack 1.
            
            :param stackNum: The stack number (0-1) to make 'active'.
                Only the last bit is used, so any range of numbers is valid.
        """
        self.activeStackNum = stackNum & 1
        self.dataStack = self.stacks[self.activeStackNum]
    
    
#############################################################################
        
class RegisterMachine(Machine):
    """
    A variant of SCHLEP machine that has several data 'registers' that can be 
    called explicitly by a program. Specialized instructions load data from 
    the stack into registers, and other instructions push that data back onto 
    the stack. 
    """
    
    def __init__(self,
                 environment: "Environment",
                 program: Program,
                 runForever: bool = True,
                 clearData: bool = False,
                 numRegisters: int = 8,
                 trackCoverage: bool = True):
        Machine.__init__(self, environment, program, runForever, clearData, trackCoverage)
        self.registers = [0] * numRegisters


#############################################################################
