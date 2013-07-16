from schlep.instructionset import InstructionSet, operator

instructionSet = InstructionSet(name=__name__)


@operator(instructionSet)
def bitAnd (machine):
    """Pops the top two stack elements and pushes the results of their bitwise AND."""
    a,b = machine.dataStack.pop2()
    machine.dataStack.push(a & b)
    return True


@operator(instructionSet)
def bitOr (machine):
    """Pops the top two stack elements and pushes the results of their bitwise OR."""
    a,b = machine.dataStack.pop2()
    machine.dataStack.push(a | b)
    return True


@operator(instructionSet)
def bitXor (machine):
    """Pops the top two stack elements and pushes the results of their bitwise XOR."""
    a,b = machine.dataStack.pop2()
    machine.dataStack.push(a ^ b)
    return True


@operator(instructionSet)
def bitShiftLeft (machine):
    machine.dataStack.push(machine.dataStack.pop() << 2)
    return True


@operator(instructionSet)
def bitShiftRight (machine):
    machine.dataStack.push(machine.dataStack.pop() >> 2)
    return True
