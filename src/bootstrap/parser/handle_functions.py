"""
Handles replacing all variable references
and function calls where necessary with the proper node.
"""

from shisp_ast.ast import AST, Node, Symbol, VariableRef, FunctionCall, MacroCall, Expr
from shisp_ast.data_nodes import Variable, Function, PureFunction, Macro

def check_node(child: Node, *, qq=False):
    match child:
        case VariableRef(_):
            if (child.parent.children[0] is child and
                isinstance(child.data.value, PureFunction)):
                call = FunctionCall.from_node(child)
                call.is_pure = True
                child.replace(call)
            if (child.parent.children[0] is child and
                isinstance(child.data.value, Macro)):
                call = FunctionCall.from_node(child)
                call.is_macro = True
                child.replace(call)
            elif (child.parent.children[0] is child and
                isinstance(child.data.value, Function)):
                call = FunctionCall.from_node(child)
                child.replace(call)
        case MacroCall(_):
            check_children(child.body, qq)
        case Expr(_):
            check_children(child.children, qq)

def check_children(nodes: list[Node], *, qq=False):
    for child in nodes:
        match child:
            case VariableRef(_) if not qq:
                is_call = child.parent.children[0] is child
                is_call = is_call or (isinstance(child.parent, MacroCall) and
                                      child.parent.macro_name == 'let')
                if (is_call and
                    isinstance(child.data.value, PureFunction)):
                    call = FunctionCall.from_node(child)
                    call.is_pure = True
                    child.replace(call)
                elif is_call and isinstance(child.data.value, Function):
                    call = FunctionCall.from_node(child)
                    child.replace(call)
            case (MacroCall(macro_name="shell-literal") | MacroCall(macro_name='quote')) if not qq:
                pass
            case MacroCall(macro_name='unquote') | MacroCall(macro_name='unquote-splice'):
                check_node(child.body)
            case MacroCall(macro_name='quasiquote') if not qq:
                check_node(child.body, qq=True)
            case MacroCall(_) if not qq:
                check_children(child.body, qq=qq)
            case Expr(_):
                check_children(child.children, qq=qq)

def replace_references(ast: AST) -> AST:
    base_node = ast.base_node
    check_children(base_node.children)
    return ast
