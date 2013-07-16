# schlep.operators

#__all__ = ['terminators', 'stackOps', 'mathOps', 'advancedMathOps', 'bitwiseOps', 'testOps']
'''
class GenericOperator ():
    cost = 1
    isOperator = True
    isConditional = False
    isTerminator = False


def isTerminator(func):
    """ Returns True if the instruction at the specified index is an 'end' 
        statement.
    """
    # If the function does not have the isTerminator attribute, it is derived
    # from the module's name.
    try:
        return func.isTerminator
    except:
        func.isTerminator = func.__module__.find('terminators') > -1
        if func.isTerminator:
            func.isConditional = False
            func.isOperator = False
        return func.isTerminator

'''