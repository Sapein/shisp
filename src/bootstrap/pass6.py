"""
Handles replacing all variable references
and function calls where necessary with the proper node.
"""

from shisp_ast import AST, Node, Symbol, VariableRef, FunctionCall, MacroCall, Expr
from ast_data import Variable, Function

def check_node(node: Node):
    match child:
        case VariableRef(_):
            if (child.parent.children[0] is child and
                isinstance(child.data.value, Function)):
                call = FunctionCall.from_node(child)
                child.replace(call)
        case MacroCall(_):
            check_children(child.body)
        case Expr(_):
            check_children(child)

def check_children(nodes: list[Node]):
    for child in nodes:
        match child:
            case VariableRef(_):
                print(child)
                is_call = child.parent.children[0] is child
                is_call = is_call or (isinstance(child.parent, MacroCall) and
                                      child.parent.macro_name == 'let')
                if (is_call and
                    isinstance(child.data.value, Function)):
                    call = FunctionCall.from_node(child)
                    child.replace(call)
            case MacroCall(macro_name="shell-literal"):
                pass
            case MacroCall(_):
                check_children(child.body)
            case Expr(_):
                check_children(child.children)

def replace_references(ast: AST) -> AST:
    base_node = ast.base_node
    check_children(base_node.children)
    return ast
