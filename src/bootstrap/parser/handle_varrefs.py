"""
For the fourth pass of the parser.

This checks all variables after expansion.
"""

from typing import Optional

from shisp_ast.ast import Expr, Node, Symbol, MacroCall, VariableRef, ReturnNode
from shisp_ast.data_nodes import *
import shisp_builtins as sbuilt


def check_scope(node: Node, name: str) -> tuple[bool, Optional[Variable]]:
    """
    Checks if a variable is in scope.
    If not returns false.
    """
    try:
        return name in node.scope.variables, node.scope.variables[name]
    except (AttributeError, KeyError):
        return False, None


def check_var_in_scope(node: Node, name: str) -> tuple[bool, Optional[Variable]]:
    in_scope, var = check_scope(node, name)
    if in_scope:
        return True, var
    else:
        if node.parent is None:
            return False, None
        else:
            return check_var_in_scope(node.parent, name)


def check_node(child: Node):
    match child:
        case ReturnNode(_):
            check_node(child.children[0])
        case Symbol(_):
            in_scope, var = check_var_in_scope(child.parent, child.escape_data())
            if not in_scope:
                raise SyntaxError(("Variable {} is undefined!\n"
                                   "TODO: Better Error"
                                  ).format(child.data))
            var_ref = VariableRef.from_node(child)
            var_ref.data = var
            child.replace(var_ref)
        case (MacroCall(macro_name="shell-literal") | MacroCall(macro_name='quote') |
        MacroCall(macro_name="quasiquote")):
            pass
        case MacroCall(_):
            check_node(child.body[0])
        case Expr(_):
            check_node_children(child)


def check_node_children(node: Node):
    """
    Checks nodes for variables
    """
    for child in node.children:
        match child:
            case Symbol(_) | MacroCall(_) | ReturnNode(_):
                check_node(child)
            case Expr(_):
                check_node_children(child)


def check_variables(ast):
    """
    Checks variable scopes
    """
    base_node = ast.base_node
    base_node.scope.add_variable(sbuilt.Let)
    base_node.scope.add_variable(sbuilt.Defun)
    base_node.scope.add_variable(sbuilt.Depun)
    base_node.scope.add_variable(sbuilt.Shell_Literal)
    base_node.scope.add_variable(sbuilt.Quote)
    base_node.scope.add_variable(sbuilt.QuasiQuote)
    base_node.scope.add_variable(sbuilt.Unquote)
    base_node.scope.add_variable(sbuilt.Unquote_Splice)
    check_node_children(base_node)
    return ast
