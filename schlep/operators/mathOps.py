"""
Basic mathematical operators, suitable for use by an integer-based machine.
"""

from schlep.instructionset import operator, InstructionSet

instructionSet = InstructionSet(name=__name__)


@operator(instructionSet)
def add(machine):
    """ Pops the top two elements of the stack and pushes the sum. """
    a, b = machine.dataStack.pop2()
    machine.dataStack.push(b + a)
    return True


@operator(instructionSet)
def subtract(machine):
    """ Pops the top two elements of the stack and pushes the difference. """
    a, b = machine.dataStack.pop2()
    machine.dataStack.push(b - a)
    return True


@operator(instructionSet)
def multiply(machine):
    """ Pops the top two elements of the stack and pushes the quotient. """
    a, b = machine.dataStack.pop2()
    machine.dataStack.push(b * a)
    return True


@operator(instructionSet)
def divide(machine):
    """ Pops the top two elements of the stack and pushes the product. """
    a, b = machine.dataStack.pop2()
    if a != 0:
        machine.dataStack.push(b / a)
    else:
        machine.dataStack.push(0)
    return True
    

@operator(instructionSet, name="min")
def min_(machine):
    """ Pops the top two elements of the stack and pushes the lesser of the two. """
    a, b = machine.dataStack.pop2()
    if a < b:
        machine.dataStack.push(a)
    else:
        machine.dataStack.push(b)
    return True
    

@operator(instructionSet, name="max")
def max_(machine):
    """ Pops the top two elements of the stack and pushes the greater of the two. """
    a, b = machine.dataStack.pop2()
    if a > b:
        machine.dataStack.push(a)
    else:
        machine.dataStack.push(b)
    return True
        

@operator(instructionSet, name="abs")
def abs_(machine):
    """ Pops the top element of the stack and push its absolute value. """
    machine.dataStack.push(abs(machine.dataStack.pop()))
    return True


@operator(instructionSet)
def negate(machine):
    """ Multiplies the stack's topmost element by -1. """
    machine.dataStack.push(-machine.dataStack.pop())
    return True


@operator(instructionSet)
def inc(machine):
    """ Increments the data stack's topmost element by 1. """
    machine.dataStack.push(machine.dataStack.pop()+1)
    return True
    

@operator(instructionSet)
def dec(machine):
    """ Decrements the data stack's topmost element by 1. """
    machine.dataStack.push(machine.dataStack.pop()-1)
    return True


@operator(instructionSet)
def mod(machine):
    """ Pops the top two elements of the stack and pushes the remainder of stack[top-1]/stack[top]. """
    a, b = machine.dataStack.pop2()
    if b == 0:
        machine.dataStack.push(0)
    else:
        machine.dataStack.push(b % a)
    return True


@operator(instructionSet)
def square(machine):
    """ Pops the top element of the stack and pushes it squared (x^2). """
    machine.dataStack.push(machine.dataStack.pop() ** 2)
    return True
