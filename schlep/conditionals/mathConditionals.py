"""Basic mathematical tests: equality, quantity, et cetera."""

from schlep.instructionset import InstructionSet, conditional

instructionSet = InstructionSet(name=__name__)

@conditional(instructionSet)
def ifEqual(machine):
    """Destructively compares the top two elements of the stack for equality."""
    a,b = machine.dataStack.pop2()
    return (a == b)


@conditional(instructionSet)
def ifUnequal(machine):
    """Destructively compares the top two elements of the stack for inequality."""
    a,b = machine.dataStack.pop2()
    return (a != b)    


@conditional(instructionSet)
def ifGreaterThan(machine):
    """Destructively compares the top two elements of the stack: stack[top] > stack[top-1]."""
    a,b = machine.dataStack.pop2()
    return (a > b)


@conditional(instructionSet)
def ifLessThan(machine):
    """Destructively compares the top two elements of the stack: stack[top] < stack[top-1]."""
    a,b = machine.dataStack.pop2()
    return (a < b)


@conditional(instructionSet)
def ifZero(machine):
    return machine.dataStack.pop() == 0


@conditional(instructionSet)
def ifNotZero(machine):
    return machine.dataStack.pop() != 0


@conditional(instructionSet)
def ifEven(machine):
    return (machine.dataStack.pop() % 2) == 0


@conditional(instructionSet)
def ifOdd(machine):
    return not (ifEven(machine))


@conditional(instructionSet)
def whileEqual(machine):
    """Destructively compares the top two elements of the stack: stack[top] == stack[top-1].
    The machine's current function pointer gets pushed on the function pointer stack."""
    if (ifEqual(machine)):
        machine.pushFP()
        return True
    else:
        return False


@conditional(instructionSet)
def whileUnequal(machine):
    """Destructively compares the top two elements of the stack: stack[top] != stack[top-1].
    The machine's current function pointer gets pushed on the function pointer stack."""
    if (ifUnequal(machine)):
        machine.pushFP()
        return True
    else:
        return False


@conditional(instructionSet)
def whileGreaterThan(machine):
    """Destructively compares the top two elements of the stack: stack[top] >stack[top-1].
    The machine's current function pointer gets pushed on the function pointer stack."""
    if (ifGreaterThan(machine)):
        machine.pushFP()
        return True
    else:
        return False


@conditional(instructionSet)
def whileLessThan(machine):
    """Destructively compares the top two elements of the stack: stack[top] < stack[top-1].
    The machine's current function pointer gets pushed on the function pointer stack."""
    if (ifLessThan(machine)):
        machine.pushFP()
        return True
    else:
        return False

###############################################################################        

def getInstructions(instructions):
    """Adds the instructions defined in this module to a master dictionary used by the SCHLEP machine."""
    for i in instructionSet:
        instructions[i] = instructionSet[i]
        
