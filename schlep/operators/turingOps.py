"""
Operators for a Turing machine variant of SCHLEP machine. The variant has
two stacks which essentially form the 'tape' of a Turing machine. Only one
of the two stacks is 'active' at a time.
"""

from schlep.instructionset import InstructionSet, operator

instructionSet = InstructionSet(name=__name__)


@operator(instructionSet)
def toggleStacks (machine):
    """ Switch which stack is the 'active' data stack. """
    machine.stackToggle()
    return True


@operator(instructionSet)
def switchStack (machine):
    """ Switch the 'active' data stack to a specific stack, specified
        by the top element of the current stack (even or odd).
    """
    machine.changeStack(machine.dataStack.pop())
    return True


@operator(instructionSet)
def shiftStacks (machine):
    """ Move a value from one stack to the other. """
    machine.dataStack.push(machine.secondaryStack.pop())
    return True


@operator(instructionSet)
def activeStackNum (machine):
    """ Push the 'active' data stack's number onto the stack. """
    machine.dataStack.push(machine.activeStackNum)
    return True
