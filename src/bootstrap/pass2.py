"""
Handles the second pass of the Parser.


This pass handles combining specific tokens together for squashing.
"""

import shisp_ast as sast
import ast_data

def handle_quote(node: sast.SingleQuote) -> list:
    def handle_rc(rc: int | tuple[int, int]) -> int | tuple[int, int]:
        match rc:
            case (a, b):
                return b
            case b:
                return b
    match node.parent:
        case sast.String(_):
            return False
        case sast.Comment(_):
            return False

    children = [c for c in node.parent.children]
    next_node = children[children.index(node) + 1]
    last_row = handle_rc(next_node.row)
    last_col = handle_rc(next_node.column)

    quote_Expr = sast.Expr((node.row, last_row), (node.column, last_col), [], None)
    quote_sym = sast.Symbol(node.row, node.column, [], None, data='quote')
    quote_Expr.add_child(quote_sym)
    quote_Expr.add_child(next_node)

    n_index = children.index(node)
    children.insert(n_index, quote_Expr)
    children.remove(node)
    children.remove(next_node)
    next_node.parent = quote_Expr
    return children


def handle_expr(node: sast.Expr) -> bool:
    for child in node.children[:]:
        recall = combine_node(child)
        if recall and recall != node.children:
            node.children = recall
            handle_expr(node)
            return False
        

def combine_node(node: sast.Node) -> bool | list:
    match node:
        case sast.Expr(_) if node.children[0] != 'shell-literal':
            return handle_expr(node)
        case sast.SingleQuote(_):
            return handle_quote(node)
        case _:
            return False


def combine_ast(ast: sast.AST) -> sast.AST:
    combine_node(ast.base_node)
    ast.base_node.scope = ast_data.Scope()
    return ast
