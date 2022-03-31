"""
This handles the next pass, which goes over the newly built AST.

We're specifically just ensuring certain syntatic sugar is handled
properly.
"""

import shisp_ast.ast as sast
import shisp_ast.data_nodes as ast_data

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

    if isinstance(next_node, sast.SingleQuote):
        return [c for c in handle_quote(next_node) if c is not node]

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

def handle_qquote(node: sast.Backtick) -> list:
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

    if isinstance(next_node, sast.Backtick):
        return [c for c in handle_qquote(next_node) if c is not node]

    last_row = handle_rc(next_node.row)
    last_col = handle_rc(next_node.column)

    quote_Expr = sast.Expr((node.row, last_row), (node.column, last_col), [], None)
    quote_sym = sast.Symbol(node.row, node.column, [], None, data='quasiquote')
    quote_Expr.add_child(quote_sym)
    quote_Expr.add_child(next_node)

    n_index = children.index(node)
    children.insert(n_index, quote_Expr)
    children.remove(node)
    children.remove(next_node)
    next_node.parent = quote_Expr
    combine_qquote_node(next_node)
    return children


def handle_unquote_splice(node: sast.At) -> list:
    def handle_rc(rc: int | tuple[int, int]) -> int:
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

    match next_node:
        case sast.At(_):
            return [c for c in handle_unquote_splice(next_node) if c is not node]

    last_row = handle_rc(next_node.row)
    last_col = handle_rc(next_node.column)

    quote_Expr = sast.Expr((node.row, last_row), (node.column, last_col), [], None)
    quote_sym = sast.Symbol(node.row, node.column, [], None, data='unquote-splice')
    quote_Expr.add_child(quote_sym)
    quote_Expr.add_child(next_node)

    n_index = children.index(node)
    children.insert(n_index, quote_Expr)
    children.remove(node)
    children.remove(next_node)
    next_node.parent = quote_Expr
    combine_node(next_node)
    return children

def handle_unquote(node: sast.Comma) -> list:
    def handle_rc(rc: int | tuple[int, int]) -> int:
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

    match next_node:
        case sast.Comma(_):
            return [c for c in handle_unquote(next_node) if c is not node]
        case sast.At(_):
            return [c for c in handle_unquote_splice(next_node) if c is not node]

    last_row = handle_rc(next_node.row)
    last_col = handle_rc(next_node.column)

    quote_Expr = sast.Expr((node.row, last_row), (node.column, last_col), [], None)
    quote_sym = sast.Symbol(node.row, node.column, [], None, data='unquote')
    quote_Expr.add_child(quote_sym)
    quote_Expr.add_child(next_node)

    n_index = children.index(node)
    children.insert(n_index, quote_Expr)
    children.remove(node)
    children.remove(next_node)
    next_node.parent = quote_Expr
    combine_node(next_node)
    return children

def handle_qquote_expr(node: sast.Expr) -> bool:
    for child in node.children[:]:
        recall = combine_qquote_node(child)
        if recall and recall != node.children:
            node.children = recall
            handle_qquote_expr(node)
            return False

def handle_expr(node: sast.Expr) -> bool:
    for child in node.children[:]:
        recall = combine_node(child)
        if recall and recall != node.children:
            node.children = recall
            handle_expr(node)
            return False

def combine_qquote_node(node: sast.Node) -> bool | list:
    match node:
        case sast.Expr(_):
            return handle_qquote_expr(node)
        case sast.Comma(_):
            return handle_unquote(node)
        case _:
            return False

def combine_node(node: sast.Node) -> bool | list:
    match node:
        case sast.Expr(_) if node.children[0] != 'shell-literal':
            return handle_expr(node)
        case sast.SingleQuote(_):
            return handle_quote(node)
        case sast.Backtick(_):
            return handle_qquote(node)
        case sast.Comma(_):
            return handle_unquote(node)
        case _:
            return False


def combine_ast(ast: sast.AST) -> sast.AST:
    combine_node(ast.base_node)
    ast.base_node.scope = ast_data.Scope()
    return ast
