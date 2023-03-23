from random import choice, random, randrange
import struct
from typing import Callable, Optional, Union
from uuid import uuid1
import warnings
from xml.dom import minidom

from instructionset import InstructionSet
from program import Program


def crossover(program1, program2, start1, start2):
    """ Generate two new programs via crossover to combine two existing
        programs, swapping 'cut' branches. The originals are not modified.

        This is generally intended to be called by other generation
        functions, which will produce starting indices using their own
        schemes, as opposed to being called directly.

        :param program1: The first program.
        :param program2: The second program.
        :param start1: The index of the 'cut' in `program1`.
        :param start2: The index of the 'cut' in `program2`.
        :return: A `tuple` containing two new `Program` objects
    """
    # Choose a random splice point in each program and find the end of
    # each branch.
    end1 = program1._getElse(start1)
    end2 = program2._getElse(start2)
    if program1.instructionSet != program2.instructionSet:
        raise ValueError('Programs must share the same instruction set.')

    # Mating: identical instruction sets. Just combine the code via
    # crossover (swap clippings)
    newCode1 = (program1.indices[0:start1]
                + program2.indices[start2:end2]
                + program1.indices[end1:-1])
    newCode2 = (program2.indices[0:start2]
                + program1.indices[start1:end1]
                + program2.indices[end2:-1])
    programClass = type(program1)
    return (programClass(newCode1, instructionSet=program1.instructionSet, parents=(program1, program2)),
            programClass(newCode2, instructionSet=program1.instructionSet, parents=(program1, program2)))


def mate(program1, program2):
    start1 = int(random() * (len(program1) - 1))
    start2 = int(random() * (len(program2) - 1))
    return crossover(program1, program2, start1, start2)


def mutate(program, probability: float, amount: int) -> Program:
    """ Returns a duplicate program with randomly twiddled bits.

        :param program: The Program to mutate.
        :param probability: (normalized float) The probability that an
            instruction will mutate.
        :param amount: (integer) The maximum number of bits to twiddle
            per instruction.
    """
    newCode = []
    for i in program.indices:
        newIdx = i
        for _j in range(amount):
            if random() < probability:
                newIdx = i ^ 2 ** int(random() * program.instructionSet.instructionSize * 8)
            newCode.append(newIdx)
    return Program(newCode, program.instructionSet, parents=[program.id])



def makeRandom(maxLength, instructionSet):
    """ Generate a random SCHLEP program.

        :param maxLength: The new program's maximum number of instructions.
        :param instructionSet: The `InstructionSet` to be used by the
            new program.
        :return: A new SCHLEP `Program`.
    """
    # TODO: This.
    # If I just generate an array of random numbers, I can't control the
    # frequency of end statements. The ratio of terminators to other
    # instructionSet is extremely low.
    # Maybe 'end' should not be an instruction after all.
    depth = 1
    source = []

    while depth > 0 and len(source) < maxLength:
        # TODO: Add literal numbers, too.
        r = int((random() * (maxint - 2) * 2) - maxint)
        if r >= 0:
            inst = instructionSet.getByIndex(r)
            if inst.isTerminator:
                depth -= 1
            elif inst.isConditional:
                depth += 1
        else:
            r -= instructionSet.literalOffset
        source.append(r)

    return Program(source, instructionSet)

def random2(instructionSet=None, maxLength=10,
            literalMin=minint, literalMax=maxint,
            probabilities=(30, 30, 20, 20)):
    """ Generate a random program with control over the probability of each
        instruction type.

        :param maxLength: The new program's maximum number of instructions.
        :param instructionSet: The `InstructionSet` to be used by the
            new program.
        :param literalMin: The minimum value for randomly-generated
            literal values.
        :param literalMax: The maximum value for randomly-generated
            literal values.
        :param probabilities: (tuple) The relative probability of literals,
            operators, conditionals and terminators in a program. The four
            numbers can have any total sum; percentages are generated from
            the total.
        :return: A new SCHLEP `Program`.
    """
    # Normalize probabilities.
    probTotal = float(sum(probabilities))
    probs = []
    lastProb = 0.0
    for p in probabilities:
        thisProb = (lastProb + (p / probTotal))
        probs.append(thisProb)
        lastProb = thisProb

    depth = 1
    source = []

    while depth > 0 and len(source) < maxLength:
        r = random()
        if r <= probs[0]:
            # literal
            source.append(str(randrange(literalMin, literalMax)))
        elif r <= probs[1]:
            # operator
            source.append(choice(instructionSet.operators()).name)
        elif r <= probs[2]:
            # conditional
            source.append(choice(instructionSet.conditionals()).name)
            depth += 1
        elif depth > 1:
            # terminator
            source.append(choice(instructionSet.terminators()).name)
            depth -= 1

    for _i in range(depth):
        source.append(choice(instructionSet.terminators()).name)

    return Program(" ".join(source), instructionSet=instructionSet)
