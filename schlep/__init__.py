#                  _     _                 Stack
#         ___  ___| |__ | | ___ _ __       Constructing
#        / __|/ __| '_ \| |/ _ \ '_ \      High-level
#        \__ \ (__| | | | |  __/ |_) |     Language for
#        |___/\___|_| |_|_|\___| .__/      Evolving
#                              |_|         Programs

"""
Stack Constructing High-level Language for Evolving Programs.

@var instructionSet: The list of all valid SCHLEP instructions.

"""

# TODO: The current machine uses integers as data, which works nicely 
# because they can be incorporated directly into the program. The current 
# system could be used as fixed-point fractional numbers (normalized values,
# et cetera), but other sorts of data would require an indirect storage 
# system of some sort. This isn't quite as elegant, as it will require an 
# extra step and any string of bits is no longer necessarily a valid program.

from schlep.instructionset import InstructionSet

from schlep.conditionals import stackConditionals
from schlep.conditionals import mathConditionals
from schlep.operators import mathOps
from schlep.operators import stackOps
from schlep.operators import testOps
from schlep.operators import terminators

#from schlep.instructionset import isConditional, isTerminator

from schlep.machines import Machine

from numbers import Number
from random import choice, random, randrange
from sha import sha
import sys
from uuid import uuid1

from xml.dom import minidom


###############################################################################        
###############################################################################        

# The working number of bits in an integer, as used by the mutation function.
# Not necessarily the actual number of bits in a Python integer.
integerBits = 32

maxint = pow(2, integerBits-1)-1
minint = -(maxint+1)

# literalOffset: Integer literals are stored in programs as negative numbers.
# This offset returns it to the proper range.
literalOffset = -maxint


###############################################################################        
###############################################################################        

# Instruction Set Loading stuff.
defaultInstructionSet = InstructionSet()
defaultInstructionSet.extend(mathConditionals.instructionSet)
defaultInstructionSet.extend(mathOps.instructionSet)
defaultInstructionSet.extend(stackConditionals.instructionSet)
defaultInstructionSet.extend(stackOps.instructionSet)
defaultInstructionSet.extend(terminators.instructionSet)

#instructionSet.add(advancedMathOps.instructionSet)
#instructionSet.add(bitwiseOps.instructionSet)


###############################################################################        
###############################################################################        

class Program(object):
    """
    A single SCHLEP program. It can be accessed like an array and will return
    a reference to a SCHLEP instruction (to be executed on its containing 
    Machine).
    """
        
    def __init__(self, code, instructionSet=defaultInstructionSet, id=None, 
                 parents=None):
        """ Create a new program containing the provided code. The code is 
            passed as either a string of whitespace-delimited instruction 
            names and numeric literals or as an array of indices into the 
            instruction set. When the code is provided as a string, all the
            instructions must be present in the given instruction set.
            
            @param code: The program, either as source code or a list of 
                indices into the instruction set.
            @param instructionSet: The instruction set used by the program
            @type instructionSet: `schlep.instructionset.InstructionSet`
            @keyword id: a unique ID for this program. Should only be
                provided when loading a program, not creating a new one.
            @keyword parents: A list of the UUIDs of the programs used
                to create this one via mating or mutation.
        """
        # code is an array if indices into the instructionSet.
        # instructionSet is an array of function references (in conditionals 
        # and operators modules)
        if isinstance(code, str):
            self.indicies = []
            self.code = []
            for t in code.split():
                if all([c in "0123456789-." for c in t]):
                    v = int(t) + literalOffset
                    self.indicies.append(v)
                else:
                    self.indicies.append(instructionSet.index(t))
        elif isinstance(code, list):
            self.indicies = code
        else:
            raise(TypeError, "code must be either an array or a string")
        self.length = len(self.indicies)
        self.instructionSet = instructionSet
        self.jumpTable = {}
        self.fitness = 0
        
        self.id = id if id is not None else str(uuid1())
        self.parents = parents

        self.compile()
        self._hash = None


    def __str__(self):
        """ Generates human-readable source code from a Program."""
        return ' '.join([x.opname for x in self.code])
    
    
    def __repr__(self):
        return "<%s id:%s>" % (self.__class__.__name__, self.id)
    
    
    def __len__(self):
        return self.length

    
    def __hash__(self):
        if self._hash is None:
            self._hash = hash(str(self))
        return self._hash
    
    
    def __eq__(self, other):
        return hash(self) == hash(other)
    
    
    def __getitem__(self, idx):
        """ Retrieve an instruction by index. The operation is 'safe:'
            out-of-range values return `None`.

            @param idx: The index of the instruction (0 to length-1)
         """
        if idx < 0 or idx > self.length:
            return None
        return self.code[idx]


    def __add__(self, other):
        """
        """
        newProgram = Program(self.indices, self.instructionSet,
                             parents=[self.id, other.id])
        newProgram.append(other)
        return newProgram
        
        
        
    #===========================================================================
    # 
    #===========================================================================
    
    def compile(self):
        """ Prepare a Program for execution.
        """
        self._hash = None
        self.fitness = 0
        self.code = []
        for i in self.indicies:
            if i < 0:
                self.code.append(self._makeLiteral(i - literalOffset))
            else:
                self.code.append(self.instructionSet.getByIndex(i))
                
        # Fill out the 'jump table' for faster processing of conditionals
        self.jumpTable = {}
        for i in xrange(len(self.indicies)-1):
            if self.code[i].isConditional:
                self.jumpTable[i] = self._getElse(i)
        
        
    def _makeLiteral(self, val):
        """ Generate a function that just pushes a literal value. 
        """
        # It's assumed that 'val' is the actual, literal value, not offset.
        # TODO: Possibly cache the lambda to avoid duplicates
        f = lambda(machine): machine.dataStack.push(val)
        setattr(f, 'isConditional', False)
        setattr(f, 'isOperator', False)
        setattr(f, 'isTerminator', False)
        setattr(f, 'isLiteral', True)
        setattr(f, 'opname', str(val))
        return f

        
    def append(self, item):
        """ Append another program to the current program.
        
            @param item: The program to append
        """
        if item.instructionSet == self.instructionSet:
            # They use the same instruction set; just merge.
            # Preserve the actual indices in each program.
            self.indicies += self.indicies + item.indices
        else:
            # Different instruction sets; combine sets and programs
            newSource = "%s %s" % (self, item)
            self.instructionSet.extend(item.instructionSet)
            p = self.compile(newSource, self.instructionSet)
            self.indicies = p.indicies
        self.compile()

    
    def _getElse(self,idx):
        """ Retrieves the index of a conditional's 'else' clause by crawling 
            the code. This is run once during the program's initial setup to
            build the jump table.
            
            @param idx: The index into the program
        """
        depth = 0
        for i in xrange(idx+1, self.length):
            inst = self[i]
            if inst.isConditional:
                depth += 1
            elif inst.isTerminator:
                if depth == 0:
                    return i+1
                else:
                    depth -= 1
        return 0
    
    
    def getElse(self, idx):
        """ Retrieves the index of a conditional's 'else' clause.
        
            @param idx: The index of the conditional.
        """
        # Uses the jump table computed at 'compile' time.
        return self.jumpTable[idx]
    
        
    def toXml(self):
        """ Export this program as XML. This is just the program itself, not
            its InstructionSet.
        """
        el = minidom.Element("Program")
        el.setAttribute("id", self.id)
        if self.parents is not None:
            el.setAttribute("parents", " ".join(self.parents))
        el.createTextNode(str(self))
        return el
    
    
    @classmethod
    def fromXml(cls, el, instructionSet):
        """ Import a program from an XML element.
        """
        if el.firstChild != None and el.firstChild.nodeType == el.TEXT_NODE:
            return Program(el.firstChild.wholeText.strip(), 
                           instructionSet=instructionSet)
        # TODO: Raise some sort of exception
        return None
        
    
    
    #===========================================================================
    # GP functions 
    #===========================================================================

    def mate(self, program):
        """ Uses crossover to combine this program with another, producing 
            two new programs. The originals are not modified.

            @param program: The 'mate' program
            @return: A `tuple` containing two new `Program` objects
        """
        # Choose a random splice point in each program and find the end of
        # each branch.
        startA = int(random()*(len(self) - 1))
        startB = int(random()*(len(program) - 1))
        endA = self._getElse(startA)
        endB = program._getElse(startB)
        if self.instructionSet == program.instructionSet:
            # Mating: identical instruction sets. Just combine the code via 
            # crossover (swap clippings)
            newCode1 = self.indicies[0:startA] + \
                        program.indicies[startB:endB] + \
                        self.indicies[endA:-1]
            newCode2 = program.indicies[0:startB] + \
                        self.indicies[startA:endA] + \
                        program.indicies[endB:-1]
            return (Program(newCode1,self.instructionSet), 
                    Program(newCode2, self.instructionSet))
        else:
            # Mating: differing instruction sets. Merge the sets and 
            # recompile new new programs with it.
            sourceA = str(self).split()
            sourceB = str(program).split()
            newCode1 = ' '.join(sourceA[0:startA] + \
                                sourceB[startB:endB] + \
                                sourceA[endA:-1])
            newCode2 = ' '.join(sourceB[0:startB] + \
                                sourceA[startA:endA] + \
                                sourceB[endB:-1])
            newSet = self.instructionSet + program.instructionSet
            return (Program(newCode1, newSet, parents=[self.id, program.id]), 
                    Program(newCode2, newSet, parents=[self.id, program.id]))
        
        
    def mutate(self, probability, amount):
        """ Returns a duplicate program with randomly twiddled bits.

            @param probability: (normalized float) The probability that an 
                instruction will mutate.
            @param amount: (integer) The maximum number of bits to twiddle 
                per instruction.
        """
        newCode = []
        for i in self.indicies:
            newIdx = i
            for j in xrange(amount):
                j # Hide the 'unused variable' warning
                if random() < probability:
                    newIdx = i ^ 2 ** int(random() * integerBits)
                newCode.append(newIdx)
        return Program(newCode, self.instructionSet, parents=[self.id])


    #===========================================================================
    # 
    #===========================================================================
    
    @classmethod
    def random(cls, maxLength, instructionSet=defaultInstructionSet):
        """ Generate a random SCHLEP program.
    
            @param maxLength: The new program's maximum number of instructions.
            @param instructionSet: The `InstructionSet` to be used by the 
                new program.
            @return: A new SCHLEP `Program`.
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
                r -= literalOffset
            source.append(r)
    
        return Program(source, instructionSet=instructionSet)
    
    
    @classmethod
    def random2 (cls, instructionSet=defaultInstructionSet, maxLength=10,
                 literalMin=minint, literalMax=maxint, 
                 probabilities=(30,30,20,20)):
        """ Generate a random program with control over the probability of each 
            instruction type.
        
            @param maxLength: The new program's maximum number of instructions.
            @param instructionSet: The `InstructionSet` to be used by the 
                new program.
            @param probabilities: (tuple) The relative probability of literals, 
                operators, conditionals and terminators in a program. The four 
                numbers can have any total sum; percentages are generated from 
                the total.
            @return: A new SCHLEP `Program`.
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
    
        for i in xrange(depth):
            i # Hide the 'unused variable' warning
            source.append(choice(instructionSet.terminators()).name)
             
        return Program(" ".join(source), instructionSet=instructionSet)
    

###############################################################################        
###############################################################################        

class Environment:
    """
    A container and execution environment for one or more Machines.
    """
    
    def __init__(self, machine=Machine):
        """ @param machine: The class of machine to 
        """
        self.machineConstructor = machine
        self.machines = []
    
    
    def createMachine(self, program, runForever=True, clearData=False):
        """ Add a new SCHLEP machine to the environment, executing the 
            specified Program. This is the preferred way to create machines,
            as opposed to instantiating one directly.

            @param program: The new machine's program
            @param runForever: If `True` (default), the program starts over 
                when it reaches the end.
            @param clearData: If `True`, the stack is emptied when the 
                program restarts. `False` is the default.
            @return: The new machine.
            @rtype: `Machine`
        """
        newMachine = self.machineConstructor(self, program, 
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
        for i in xrange(len(self.machines)):
            print "Program %d (%s):" % (i, self.machines[i].id)
            self.machines[i].vstep()

