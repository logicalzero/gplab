"""
Operators for RegisterMachine-derived SCHLEP machines.

With the exception of ``getRegister`` and ``setRegister``, the operators for
manipulating specific registers are dynamically generated. The total number
of registers can be changed by 
"""

from schlep.instructionset import operator, InstructionSet

NUM_REGISTERS = 8
COST = None

instructionSet = InstructionSet()

#===============================================================================
# 
#===============================================================================

@operator(instructionSet)
def getRegister (machine):
    """ Push the contents of register (data stack top) onto the machine's data 
        stack."""
    a = machine.dataStack.pop()
    machine.dataStack.push(machine.registers[a % len(machine.registers)])

@operator(instructionSet)
def setRegister (machine):
    """ Pop the top two elements of the data stack and put the value of (top-1) 
        into register (top). """
    a,b = machine.dataStack.pop2()
    machine.registers[a % len(machine.registers)] = b


#===============================================================================
# 
#===============================================================================

def makeRegSetter(n, cost=COST):
    """ Create an Operator for setting the value of a specific register to the 
        top value of the machine's data stack.
    """
    def _setRegister(machine, register):
        machine.registers[register] = machine.dataStack.pop()
        return True
    
    op = lambda machine: _setRegister(machine, n)
    setattr(op, 'cost', cost)
    setattr(op, 'isConditional', False)
    setattr(op, 'isOperator', True)
    setattr(op, 'isTerminator', False)
    setattr(op, 'isLiteral', False)
    setattr(op, 'opname', "setRegister%d" % n)
    return op


def makeRegGetter(n, cost=COST):
    """ Create an Operator for getting the value of a specific register and 
        pushing it onto the machine's data stack.
    """
    def _getRegister(machine, register):
        machine.dataStack.push(machine.registers[register])
        return True

    op = lambda machine: _getRegister(machine, n)
    setattr(op, 'cost', cost)
    setattr(op, 'isConditional', False)
    setattr(op, 'isOperator', True)
    setattr(op, 'isTerminator', False)
    setattr(op, 'isLiteral', False)
    setattr(op, 'opname', "getRegister%d" % n)
    return op


def createRegisterOps(numRegs, getCost=COST, setCost=COST, 
                      instructions=instructionSet):
    """ Create a set of register getting/setting Operators and add them to the 
        InstructionSet.
        
        @param numRegs: The number of registers to create.
        @keyword getCost: The default cost of a register retrieval operator.
        @keyword setCost: The default cost of a register setting operator.
        @keyword instructionSet: The `InstructionSet` to which to add the 
            register operators.
    """
    for t, cost in ((makeRegSetter, setCost), (makeRegGetter, getCost)):
        for i in xrange(numRegs):
            op = t(i, cost)
            instructions[op.opname] = op
            
#===============================================================================
# 
#===============================================================================

createRegisterOps(NUM_REGISTERS, getCost=COST, setCost=COST, 
                  instructionSet=instructionSet)

