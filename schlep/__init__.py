#                  _     _                 Stack
#         ___  ___| |__ | | ___ _ __       Constructing
#        / __|/ __| '_ \| |/ _ \ '_ \      High-level
#        \__ \ (__| | | | |  __/ |_) |     Language for
#        |___/\___|_| |_|_|\___| .__/      Evolving
#                              |_|         Programs

"""
Stack Constructing High-level Language for Evolving Programs.

"""

# TODO: The current machine uses integers as data, which works nicely 
#  because they can be incorporated directly into the program. The current
#  system could be used as fixed-point fractional numbers (normalized values,
#  et cetera), but other sorts of data would require an indirect storage
#  system of some sort. This isn't quite as elegant, as it will require an
#  extra step and any string of bits is no longer necessarily a valid program.

import struct
from typing import Callable, Optional, Union
import warnings

from schlep.instructionset import InstructionSet

from schlep.conditionals import stackConditionals
from schlep.conditionals import mathConditionals
from schlep.operators import mathOps
from schlep.operators import stackOps
from schlep.operators import testOps
from schlep.operators import terminators
from schlep.machines import Machine

from schlep.program import Program

#############################################################################
#############################################################################

# The working number of bits in an integer, as used by the mutation function.
# Not necessarily the actual number of bits in a Python integer.
integerBits = 32

# A program is really a set of indices into the instruction set. Negative
# indices are treated as integer literals, which are multiplied by -1 and
# offset by half the maximum integer value.
maxint = pow(2, integerBits - 2) - 1
minint = -(maxint + 1)

# literalOffset: Integer literals are stored in programs as negative numbers.
# This offset returns it to the proper range.
literalOffset = -maxint

#############################################################################
#############################################################################

# Instruction Set Loading stuff.
defaultInstructionSet = InstructionSet()
defaultInstructionSet.extend(mathConditionals.instructionSet)
defaultInstructionSet.extend(mathOps.instructionSet)
defaultInstructionSet.extend(stackConditionals.instructionSet)
defaultInstructionSet.extend(stackOps.instructionSet)
defaultInstructionSet.extend(terminators.instructionSet)


# defaultInstructionSet.add(advancedMathOps.instructionSet)
# defaultInstructionSet.add(bitwiseOps.instructionSet)


#############################################################################
#############################################################################


class Environment:
    """
    A container and execution environment for one or more Machines.
    """

    def __init__(self, machine=Machine):
        """ :param machine: The class of machine to 
        """
        self.machineConstructor = machine
        self.machines = []

    def createMachine(self, program, runForever=True, clearData=False):
        """ Add a new SCHLEP machine to the environment, executing the 
            specified Program. This is the preferred way to create machines,
            as opposed to instantiating one directly.

            :param program: The new machine's program
            :param runForever: If `True` (default), the program starts over 
                when it reaches the end.
            :param clearData: If `True`, the stack is emptied when the 
                program restarts. `False` is the default.
            :return: The new machine.
            @rtype: `Machine`
        """
        newMachine = self.machineConstructor(self,
                                             program,
                                             runForever=runForever,
                                             clearData=clearData)
        self.machines.append(newMachine)
        return newMachine

    def step(self):
        """ Execute one instruction on all virtual machines.
        """
        for m in self.machines:
            m.step()

    def vstep(self):
        """ Execute one instruction on all virtual machines in 'visual' mode.
            For testing/debugging purposes.
        """
        for i in range(len(self.machines)):
            print(f"Program {i} ({self.machines[i].id}):")
            self.machines[i].vstep()
