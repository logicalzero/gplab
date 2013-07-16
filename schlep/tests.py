""" 
Tests for the SCHLEP machine and its components. 

This currently contains only timing tests to be run 'manually'. It should and
will contain unit tests eventually.
"""

import time

from schlep import Program, Environment
from schlep import defaultInstructionSet
from schlep.operators import testOps

# Add the test operators (interactive reading/printing, etc.) to the default
# InstructionSet.
testInstructions = defaultInstructionSet + testOps.instructionSet

# A test program that can run autonomously (no reading/printing)
timeTestProgram = Program("10 dup 1 whileUnequal dup 1 subtract dup 1 end " \
                          "stackSize 1 whileUnequal multiply stackSize 1 end " \
                          "end", instructionSet=testInstructions)

testProgram = Program("input dup 1 whileUnequal dup 1 subtract dup 1 end " \
                      "stackSize 1 whileUnequal multiply stackSize 1 end " \
                      "output end", instructionSet=testInstructions)

def makeTestMachine(program=testProgram):
    """ Create a SCHLEP machine for the given Program. The Program can then
        be run one instruction at a time via vstep().
     """
    e = Environment()
    return e.createMachine(program, runForever=False)


def timeTest(repeat=1000, program=timeTestProgram):
    """ Run multiple iterations of a program, calculating the time taken,
        the number of instructions executed, and the average time per 
        instruction.
    """
    e = Environment()
    m = e.createMachine(program, runForever=False)
    count = 0
    totalTime = 0
    for i in xrange(repeat):
        i # Hide the 'unused variable' warning in PyLint/Eclipse
        t0 = time.time()
        m.reset()
        while m.running:
            m.step()
            count += 1
        totalTime += time.time() - t0
    return {'Iterations': repeat, 
            'Total Time': totalTime, 
            "Instructions Executed": count, 
            "Instructions per Second": (1/totalTime) * count}


def profile(repeat=1000, program=timeTestProgram):
    """ Run multiple iterations of a program, calculating the average times
        taken by each of its operators.
    """
    e = Environment()
    m = e.createMachine(program, runForever=False)
    count = 0
    times = {}
    for i in xrange(repeat):
        i # Hide the 'unused variable' warning in PyLint/Eclipse
        m.reset()
        while m.running:
            t0 = time.time()
            opName = m.program[m.currentPointer].opname
            m.step()
            tt = time.time() - t0
            oldTime = times.setdefault(opName, tt)
            times[opName] = (oldTime + tt) / 2
            count += 1
    return times

    
# First timing test (11/29): 84351.7 instructions per second
# After 'compiling' (11/29): 181206.4