"""
This contains all of the compiler errors and warnings
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ShispError():
    context: "Node"

@dataclass(frozen=True)
class ParserError(ShispError):
    pass

@dataclass(frozen=True)
class CompilerError(ShispError):
    pass

@dataclass(frozen=True)
class NewLine_InStr(ParserError):
    pass
