"""
For the third pass of the parser

This handles expansion of all metamacros (let and defun)
"""

from shisp_ast import AST, Node, Expr, Symbol, ReturnNode
from ast_data import Scope
import shisp_builtins as builtin

def search_children(children: list[Node], *, qq: bool = False):
    for child in children:
        match child:
            case ReturnNode(_) if not qq:
                search_children(child.children, qq=qq)

            case Expr(_):
                search_children(child.children, qq=qq)

            case Symbol(data=builtin.Let.name) if not qq:
                new_node = builtin.Let.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)

            case Symbol(data=builtin.Defun.name) if not qq:
                new_node = builtin.Defun.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)
            case Symbol(data=builtin.Depun.name) if not qq:
                new_node = builtin.Depun.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)

            case Symbol(data=builtin.Demac.name) if not qq:
                new_node = builtin.Demac.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children(new_node.body)

            case Symbol(data=builtin.Quote.name) if not qq:
                new_node = builtin.Quote.meta_eval(child.parent)
                child.parent.replace(new_node)
            case Symbol(data=builtin.Shell_Literal.name) if not qq:
                new_node = builtin.Shell_Literal.meta_eval(child.parent)
                child.parent.replace(new_node)
            case Symbol(data=builtin.QuasiQuote.name) if not qq:
                new_node = builtin.QuasiQuote.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children([new_node.body], qq=True)

            case Symbol(data=builtin.Unquote.name):
                new_node = builtin.Unquote.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children([new_body.body], qq=False) 
            case Symbol(data=builtin.Unquote_Splice.name):
                new_node = builtin.Unquote_Splice.meta_eval(child.parent)
                child.parent.replace(new_node)
                search_children([new_body.body], qq=False) 

def resolve_metamacros(ast: AST) -> AST:
    base_node = ast.base_node
    base_node.scope = Scope()
    search_children(base_node.children)
    return ast
