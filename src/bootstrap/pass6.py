"""
Handles replacing all variable references
and function calls where necessary with the proper node.
"""

from shisp_ast import AST, Node, Symbol, VariableRef, FunctionCall, MacroCall, ListNode
from ast_data import Variable, Function

def check_children(node: Node):
    for child in node.children:
        match child:
            case VariableRef(_):
                if (child.parent.children[0] is child and
                    isinstance(child.data.value, Function)):
                    call = FunctionCall.from_node(child)
                    child.replace(call)
            case MacroCall(_):
                check_children(child.body)
            case ListNode(_):
                check_children(child)

def replace_references(ast: AST) -> AST:
    base_node = ast.base_node
    check_children(base_node)
    return ast
