"""
This contains all of the compiler errors and warnings
"""

class ShispWarn(Exception):
    pass

class ShispError(Exception):
    pass

class ParserError(ShispError):
    pass
