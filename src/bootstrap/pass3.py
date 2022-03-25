"""
For the third pass of the parser

This handles expansion of all metamacros (let and defun)
"""

from shisp_ast import AST, Node, Expr, Symbol, ReturnNode
from ast_data import Scope
import shisp_builtins as builtin

def search_children(children: list[Node]):
    for child in children:
        match child:
            case ReturnNode(_):
                search_children(child.children)
            case Expr(_):
                search_children(child.children)
            case Symbol(data=builtin.Let.name):
                new_node = builtin.Let.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
            case Symbol(data=builtin.Defun.name):
                new_node = builtin.Defun.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
            case Symbol(data=builtin.Depun.name):
                new_node = builtin.Depun.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
            case Symbol(data=builtin.Quote.name):
                new_node = builtin.Quote.meta_eval(child.parent)
                child.parent.replace(new_node)
            case Symbol(data=builtin.Shell_Literal.name):
                new_node = builtin.Shell_Literal.meta_eval(child.parent)
                child.parent.replace(new_node)
            case Symbol(data=builtin.QuasiQuote.name):
                new_node = builtin.QuasiQuote.meta_eval(child.parent)
                child.parent.replace(new_node)

def resolve_metamacros(ast: AST) -> AST:
    base_node = ast.base_node
    base_node.scope = Scope()
    search_children(base_node.children)
    return ast
