"""
For the second pass of the parser.

The second pass simplifies the AST greately.
"""

from shisp_ast import AST, Node, Comment, Expr, Number, MacroCall, Space, Atom, Symbol, String
from ast_data import Scope


def squash_comment(comment: Comment) -> Comment:
    """
    Squashes a comment into a singular node)
    """
    def get_end(data: tuple[int, int] | int) -> int:
        match data:
            case (start, end):
                return end
            case _:
                return data

    last_node = comment.children[-1]
    rows = (comment.row, get_end(last_node.row))
    columns = (comment.column, get_end(last_node.column))
    data = ''
    for child in comment.children:
        data = '{}{}'.format(data, child.data)
    
    comment.children.clear()
    return Comment(rows, columns, children=[], parent=None, data=data)


def squash_list(old_list: Expr) -> Expr:
    new_list = Expr(old_list.row, old_list.column, children=[], parent=None)

    for child in old_list.children:
        if (new_child := squash_node(child)) is not None:
            new_list.add_child(new_child)

    return new_list


def squash_atom(atom: Atom) -> Atom:
    return Atom(atom.row, atom.column, [], None, atom.data)

def squash_symbol(sym: Symbol) -> Symbol:
    return Symbol(sym.row, sym.column, [], None, sym.data)


def squash_node(node: Node):
    match node:
        case Comment(_):
            return squash_comment(node)
        case Number(_):
            return Number(node.row, node.column, [], None, node.data)
        case Expr(_):
            return squash_list(node)
        case Symbol(_):
            return squash_symbol(node)
        case Space(_):
            return None
        case String(_):
            return node
    raise SyntaxError("Unknown Node {}!".format(node))


def squash_ast(ast: AST) -> AST:
    ast.base_node = squash_node(ast.base_node)
    ast.base_node.scope = Scope()
    return ast
