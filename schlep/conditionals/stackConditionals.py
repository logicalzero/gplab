"""
Basic stack-testing conditionals.
"""

from schlep.instructionset import InstructionSet, conditional

instructionSet = InstructionSet(name=__name__)



@conditional(instructionSet)
def ifStackEmpty (machine):
    """Returns True if there is no data in the stack."""
    return (len(machine.dataStack) == 0)


@conditional(instructionSet)
def ifStackNotEmpty(machine):
    """Return True if there is data present in the stack."""
    return (len(machine.dataStack) != 0)


@conditional(instructionSet)
def whileStackEmpty(machine):
    """ Repeat the next branch of code until there is data in the stack.
    """
    if (ifStackEmpty(machine)):
        machine.pushFP()
        return True
    else:
        return False


@conditional(instructionSet)
def untilStackEmpty(machine):
    """ Repeat the next branch of code until there is no data in the stack.
        Counterpart to `whileStackEmpty`.
    """
    if (ifStackNotEmpty(machine)):
        machine.pushFP()
        return True
    else:
        return False
