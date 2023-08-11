"""
Environment: A container in which one or more Machines run.
"""

from typing import Callable, Optional, Union
from .machines import Machine
from .program import Program

#############################################################################
#############################################################################


class Environment:
    """
    A container and execution environment for one or more Machines.
    """

    def __init__(self, machine: Union[type, Callable[..., Machine]] = Machine):
        """ A container and execution environment for one or more Machines.

            :param machine: A subclass of `Machine`, or callable object that
                generates a `Machine` subclass instance.
        """
        self.machineConstructor = machine
        self.machines = []


    def createMachine(self,
                      program: Program,
                      runForever: bool = True,
                      clearData: bool = False) -> Machine:
        """ Add a new SCHLEP machine to the environment, executing the
            specified Program. This is the preferred way to create machines,
            as opposed to instantiating one directly.

            :param program: The new machine's program.
            :param runForever: If `True` (default), the program starts over
                when it reaches the end.
            :param clearData: If `True`, the stack is emptied when the
                program restarts. `False` is the default.
            :return: The new machine.
        """
        newMachine = self.machineConstructor(self,
                                             program,
                                             runForever=runForever,
                                             clearData=clearData)
        self.machines.append(newMachine)
        return newMachine


    def step(self, callback: Optional[Callable] = None):
        """ Execute one instruction on all virtual machines in the
            Environment.
        """
        for n, m in enumerate(self.machines):
            if callback:
                callback(n, m)
            m.step()


    def vstep(self):
        """ Execute one instruction on all virtual machines in 'visual' mode.
            For testing/debugging purposes.
        """
        def vstepCallback(idx, machine):
            print(f"Program {idx} ({machine.id}):")
            print("\tData Stack:", machine.dataStack)
            print("\tNext instruction:", machine.program[machine.currentPointer].opname)
            print("\tPtr. Stack:", machine.pointerStack, "current:", machine.currentPointer)

        self.step(vstepCallback)
