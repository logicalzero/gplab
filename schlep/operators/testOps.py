"""
Operators for testing purposes.
"""

from schlep.instructionset import InstructionSet, operator

instructionSet = InstructionSet(name=__name__)


@operator(instructionSet, name="input")
def input_(machine):
    """Prompt the user to enter a number, then push that number onto the stack."""
    x = int(raw_input("Enter a number:"))
    machine.dataStack.push(x)
    return True


@operator(instructionSet)
def output(machine):
    """Print the topmost element of the stack."""
    item = machine.dataStack.peek()
    print "Top item in data stack:", item
    return True


@operator(instructionSet)
def outputStack(machine):
    """Print the entire stack to the console."""
    print "Stack contents:", machine.dataStack.data
    return True
    