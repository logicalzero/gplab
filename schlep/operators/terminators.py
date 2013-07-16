"""
Contains the 'end' operator.
"""

from schlep.instructionset import InstructionSet, terminator

instructionSet = InstructionSet(name=__name__)


@terminator(instructionSet)
def end(machine):
    machine.popFP()
    
    
