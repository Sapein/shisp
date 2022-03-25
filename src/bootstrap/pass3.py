"""
For the third pass of the parser

This handles expansion of all metamacros (let and defun)
"""

from shisp_ast import AST, Node, Expr, Symbol
from ast_data import Scope
from shisp_builtins import Let, Defun

def search_children(children: list[Node]):
    for child in children:
        match child:
            case Expr(_):
                search_children(child.children)
            case Symbol(data='let'):
                new_node = Let.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
                return
            case Symbol(data='defun'):
                new_node = Defun.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
                pass

def resolve_metamacros(ast: AST) -> AST:
    base_node = ast.base_node
    base_node.scope = Scope()
    search_children(base_node.children)
    return ast
