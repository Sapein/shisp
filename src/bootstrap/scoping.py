"""
Scoping
"""


from parser import BaseNode, AST, Atom, List, Scope, Number, String
from typing import Any, Callable
from dataclasses import dataclass


@dataclass
class Variable(BaseNode):
    name: str
    value: Any

    def __str__(self, *args, **kwargs):

        return ('Name:  {name}\n'
                'Value: {value}\n'
               ).format(name=self.name, value=self.value)


@dataclass
class Function(BaseNode):
    args = None

@dataclass
class Builtin(Variable):
    name: str
    def meta_eval(self, *args, **kwargs):
        raise NotImplementedError

import shisp_builtins

def add_globals(ast: AST):
    global_scope = ast.base_node.scope
    global_scope.add_variable(shisp_builtins.Let(0,0, name="let", value=None))
    return ast

def add_variables(ast: AST):
    def check_variable(name, scope, child):
        match scope.variables[name]:
            case Builtin(name=name):
                scope.variables[name].meta_eval(child)
                return True
            case Variable(name=name, value=Function(_)):
                return True
            case Variable(name=name):
                return True
        return False

    def check_children(node, scopes: list[Scope]):
        for child in node.children:
            match child:
                case List(_):
                    scopes.insert(0, child.scope)
                    check_children(child, scopes)
                case Number(_) | String(_):
                    return
                case Atom(_):
                    name = child.data
                    _scope = None
                    for scope in scopes:
                        if name in scope.variables:
                            _scope = scope
                            break
                    else:
                        raise NameError("Variable not defined!")
                    if check_variable(name, _scope, child):
                        return

    base_node = ast.base_node
    check_children(base_node, [base_node.scope])
    return ast
