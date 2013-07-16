"""
Contains basic stack-manipulation operators.
"""

from schlep.instructionset import InstructionSet, operator

instructionSet = InstructionSet(name=__name__)


@operator(instructionSet)
def pop(machine):
    """Removes (and discards) the top element from the stack."""
    machine.dataStack.pop()
    return True


@operator(instructionSet)
def dup(machine):
    """Duplicates the top element of the stack."""
    machine.dataStack.push(machine.dataStack.peek())
    return True
    

@operator(instructionSet)
def dup2(machine):
    """Duplicates the top two elements of the stack."""
    ## TODO: Optimize. This is about as bad as it can get.
    items = machine.dataStack.peek2()
    machine.dataStack.push(items[0])
    machine.dataStack.push(items[1])
    return True


@operator(instructionSet)
def swap(machine):
    """Swaps the top two elements of the stack."""
    ## TODO: Optimize. This is about as bad as it can get.
    a = machine.dataStack.pop()
    b = machine.dataStack.pop()
    machine.dataStack.push(a)
    machine.dataStack.push(b)
    return True
    

@operator(instructionSet)
def shuffle(machine):
    """Puts the third-from-top element on the top of the stack."""
    ## TODO: Optimize. This is about as bad as it can get.
    a,b = machine.dataStack.pop2()
    c = machine.dataStack.pop()
    machine.dataStack.push(b)
    machine.dataStack.push(a)
    machine.dataStack.push(c)
    return True


@operator(instructionSet)
def clear(machine):
    """Removes all contents of the stack."""
    machine.dataStack.clear()
    return True


@operator(instructionSet)
def stackSize(machine):
    """Pushes the current stack size onto the stack. The total does not include the pushed number."""
    machine.dataStack.push(len(machine.dataStack))
    return True

