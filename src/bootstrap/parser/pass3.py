"""
For the second pass of the parser.

The second pass simplifies the AST greately.
"""

from shisp_ast import AST, Node, Comment, Expr, Number, MacroCall, Space, Atom, Symbol, String
from ast_data import Scope


def squash_comment(comment: Comment) -> Comment:
    return Comment(comment.row, comment.column, [], None, comment.data)


def squash_list(old_list: Expr) -> Expr:
    new_list = Expr(old_list.row, old_list.column, children=[], parent=None)

    for child in old_list.children:
        if (new_child := squash_node(child)) is not None:
            new_list.add_child(new_child)

    return new_list


def squash_atom(atom: Atom) -> Atom:
    a = Atom.from_node(atom, False)
    return a

def squash_symbol(sym: Symbol) -> Symbol:
    return Symbol.from_node(sym, False)


def squash_node(node: Node):
    match node:
        case Space(_):
            return None
        case Comment(_):
            return squash_comment(node)
        case Number(_):
            return Number(node.row, node.column, [], None, node.data)
        case Expr(_):
            return squash_list(node)
        case Symbol(_):
            return Symbol(node.row, node.column, [], None, node.data)
        case String(_):
            return String(node.row, node.column, [], None, data=node.data)
        case Atom(_):
            return Atom(node.row, node.column, [], None, data=atom.data)

    print(node)
    raise SyntaxError("Unknown Node")


def squash_ast(ast: AST) -> AST:
    ast.base_node = squash_node(ast.base_node)
    ast.base_node.scope = Scope()
    return ast
