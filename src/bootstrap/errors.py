"""
This contains all of the compiler errors and warnings
"""

from typing import Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class ShispError():
    context: Optional["Node"]
    output: str

@dataclass
class ShispWarn():
    pass

@dataclass(frozen=True)
class ParserError(ShispError):
    pass

@dataclass(frozen=True)
class CompilerError(ShispError):
    pass

class AbortParse(Exception):
    pass
