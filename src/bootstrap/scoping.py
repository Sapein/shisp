"""
Scoping
"""


from dataclasses import dataclass
from typing import Any, Callable

 
from ast_data import Scope
from parser import BaseNode, AST, Atom, List, Scope, Number, String, MacroCall


def add_globals(ast: AST):
    global_scope = ast.base_node.scope
    global_scope.add_variable(shisp_builtins.Let(0,0, name="let", value=None, children=None, parent=None))
    global_scope.add_variable(shisp_builtins.Defun(0,0, name='defun', value=None, children=None, parent=None))
    return ast

def check_variable(name, scope, child, scopes=None) -> tuple[bool,bool]:
    success = False
    node = scope.variables[name]
    match node:
        case Builtin(name=name):
            response = node.meta_eval(child, scopes=scopes)
            new_node, newchild = node.meta_emit(child)
            child.replace(new_node)
            if response is not None:
                try:
                    scopes, child_eval = response
                    if child_eval:
                        check_children(newchild, scopes)
                except TypeError:
                    pass
            return success, True
        case Variable(name=name, value=Function(_)):
            return success, True
        case Variable(name=name):
            return success, True

def check_children(node, scopes: list[Scope]):
    for child in node.children:
        match child:
            case Builtin(name=name):
                response = node.meta_eval(child, scopes=scopes)
                new_node, newchild = node.meta_emit(child)
                child.replace(new_node)
                if response is not None:
                    try:
                        scopes, child_eval = response
                        if child_eval:
                            check_children(newchild, scopes)
                    except TypeError:
                        pass
            case List(_):
                scopes.insert(0, child.scope)
                check_children(child, scopes)
            case Number(_) | String(_):
                return
            case Atom(_):
                #TODO Put in stuff here
                name = child.data
                _scope = None
                for scope in scopes:
                    if name in scope.variables:
                        _scope = scope
                        break
                else:
                    continue
                success, _ = check_variable(name, _scope, child, scopes)
                if success:
                    return
