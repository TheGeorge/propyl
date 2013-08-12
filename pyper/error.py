# errors
class Error(Exception): pass
class TransitionError(Error): pass

class PreConditionNotMet(Error): pass
class PostConditionNotMet(Error): pass
