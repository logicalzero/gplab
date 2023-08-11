import struct
from typing import Callable, Union
from uuid import uuid1
import warnings

from schlep.instructionset import InstructionSet


class Program(object):
    """
    A single SCHLEP program. It can be accessed like an array and will return
    a reference to a SCHLEP instruction (to be executed on its containing
    Machine).
    """

    def __init__(self,
                 src: Union[str, list[int]],
                 instructionSet: InstructionSet,
                 id=None,
                 parents: Union[list, tuple, None] = None):
        """ Create a new program containing the provided code. The code is
            passed as either a string of whitespace-delimited instruction
            names and numeric literals or as an array of indices into the
            instruction set. When the code is provided as a string, all the
            instructions must be present in the given instruction set.

            :param src: The program, either as source code or a list of
                indices into the instruction set.
            :param instructionSet: The instruction set used by the program
            :type instructionSet: `schlep.instructionset.InstructionSet`
            :param id: a unique ID for this program. Should only be
                provided when loading a program, not creating a new one.
            :param parents: A list of the UUIDs of the programs used
                to create this one via mating or mutation.
        """
        # code is an array of indices into the instructionSet.
        # instructionSet is an array of function references (in conditionals
        # and operators modules)
        self.instructionSet = instructionSet
        self.id = id if id is not None else str(uuid1())
        self.parents = parents

        self.indices = []
        self.code = []
        self.jumpTable = {}
        self.fitness = 0
        self._hash = None

        if isinstance(src, str):
            for t in src.split():
                if all(c in "0123456789-." for c in t):
                    v = int(t) + instructionSet.literalOffset
                    self.indices.append(v)
                else:
                    self.indices.append(instructionSet.index(t))
        elif isinstance(src, list):
            self.indices = src
        else:
            raise TypeError("code must be either an array or a string")

        self.compile()
        self.length = len(self.code)

    def __str__(self) -> str:
        """ Generates human-readable source code from a Program."""
        return ' '.join([x.opname for x in self.code])

    def __repr__(self) -> str:
        return f"<{type(self).__name__} id:{self.id}>"

    def __len__(self) -> int:
        return len(self.indices)

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash(str(self))
        return self._hash

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __getitem__(self, idx):
        """ Retrieve an instruction by index. The operation is 'safe:'
            out-of-range values return `None`.

            :param idx: The index of the instruction (0 to length-1)
         """
        if idx < 0 or idx >= self.length:
            return None
        return self.code[idx]

    def __add__(self, other):
        """
        """
        newProgram = Program(self.indices, self.instructionSet,
                             parents=[self.id, other.id])
        newProgram.extend(other)
        return newProgram

    # =======================================================================
    #
    # =======================================================================

    def compile(self):
        """ Prepare a Program for execution.
        """
        self._hash = None
        self.fitness = 0
        self.code = []
        for i in self.indices:
            if i < 0:
                self.code.append(self._makeLiteral(i - self.instructionSet.literalOffset))
            else:
                self.code.append(self.instructionSet.getByIndex(i))

        # Fill out the 'jump table' for faster processing of conditionals
        self.jumpTable.clear()
        for i in range(len(self.indices) - 1):
            if self.code[i].isConditional:
                self.jumpTable[i] = self._getElse(i)

    @staticmethod
    def _makeLiteral(val: Union[int, float]) -> Callable:
        """ Generate a function that just pushes a literal value.
        """

        # It's assumed that 'val' is the actual, literal value, not offset.
        # TODO: Possibly cache the lambda to avoid duplicates
        def _literal(machine):
            machine.dataStack.push(val)

        setattr(_literal, 'isConditional', False)
        setattr(_literal, 'isOperator', False)
        setattr(_literal, 'isTerminator', False)
        setattr(_literal, 'isLiteral', True)
        setattr(_literal, 'opname', str(val))
        return _literal

    def extend(self, program):
        """ Append another program to the current program.

            :param program: The program to append
        """
        if not isinstance(program, Program):
            raise TypeError("extend() requires another Program, not {}".format(type(program)))
        if program.instructionSet != self.instructionSet:
            raise ValueError("Cannot combine programs with different instruction sets")

        self.indices.extend(program.indices)
        self._hash = None
        self.compile()

    def _getElse(self, idx: int) -> int:
        """ Retrieves the index of a conditional's 'else' clause by crawling
            the code. This is run once during the program's initial setup to
            build the jump table.

            :param idx: The index into the program
        """
        depth = 0
        for i in range(idx + 1, self.length):
            inst = self[i]
            if inst.isConditional:
                depth += 1
            elif inst.isTerminator:
                if depth == 0:
                    return i + 1
                else:
                    depth -= 1
        return self.length

    def getElse(self, idx: int) -> int:
        """ Retrieves the index of a conditional's 'else' clause.

            :param idx: The index of the conditional.
        """
        # Uses the jump table computed at 'compile' time.
        try:
            return self.jumpTable[idx]
        except KeyError:
            return self.jumpTable.setdefault(self._getElse(idx))

    def toXml(self):
        """ Export this program as XML. This is just the program itself, not
            its InstructionSet.
        """
        raise NotImplementedError(f"TODO: reimplement {type(self).__name__}.toXml()")


    @classmethod
    def fromXml(cls, el, instructionSet: InstructionSet):
        """ Import a program from an XML element.
        """
        raise NotImplementedError(f"TODO: reimplement {cls.__name__}.toXml()")


    @classmethod
    def fromBinary(cls,
                   data: Union[bytes, bytearray],
                   instructionSet: InstructionSet,
                   **kwargs) -> "Program":
        """ Create a new Program from a packed structure of binary data.
        """
        size = instructionSet.instructionSize
        fmt = {1: "=B",
               2: "=H",
               4: "=I",
               8: "=Q"}[size]

        remainder = len(data) % size
        if remainder:
            data = data[:-remainder]
            warnings.warn(f"Length of data not divisible by {size}; truncating {remainder}")

        indices = [chunk[0] for chunk in struct.iter_unpack(fmt, data)]
        return cls(indices, instructionSet=instructionSet, **kwargs)

    def toBinary(self) -> bytes:
        """ Generate a packed binary string version of this program.
        """
        size = self.instructionSet.instructionSize
        formatter = {1: "=B",
                     2: "=H",
                     4: "=I",
                     8: "=Q"}[size]

        data = bytearray(len(self.indices) * size)
        struct.pack_into(formatter, data, 0, self.indices)
        return data
