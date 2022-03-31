"""
Holds data nodes for the ast
"""

from dataclasses import dataclass
from typing import Any, Optional

from shisp_ast.ast import Node

@dataclass
class Scope():
    variables: dict = None
    def __init__(self, *args, variables=None, **kwargs):
        if variables is None:
            variables = {}
        self.variables = variables
        super().__init__(*args, **kwargs)

    def add_variable(self, variable: "Variable"):
        self.variables[variable.name] = variable


@dataclass
class Variable():
    name: str
    value: Any

    def __str__(self, *args, **kwargs):

        return ('Name:  {name}\n'
                'Value: {value}\n'
               ).format(name=self.name, value=self.value)


@dataclass
class Builtin(Variable):
    name: str

    @classmethod
    def is_call(cls, ast: Node) -> bool:
        """
        Checks if this should be evaluated as a call
        or if it should just be treated as the 'value'
        of the symbol.
        """
        return ast.children[0].data == cls.name

    def meta_eval(self, *args, **kwargs):
        raise NotImplementedError


@dataclass
class Function():
    scope: Scope
    body: Node
    args: Optional[list[Node]] = None

    def __str__(self, *args, **kwargs):
        return self.__class__.__name__


@dataclass
class PureFunction(Function):
    pass


@dataclass
class Func_Argument(Variable):
    value: Any = None


@dataclass
class Macro(Function):
    pass
