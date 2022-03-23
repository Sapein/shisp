"""
This handles the coding for shisp-builtins for compilation
purposes
"""


from dataclasses import dataclass
from typing import Optional


from shisp_ast import Node, MacroCall, ListNode, Symbol
from ast_data import Builtin, Variable, Function, Scope, Func_Argument


@dataclass
class Let(Builtin):
    """
    This defines a basic little builtin for 
    let to allow for variable definition.
    """
    name = 'let'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Checks if the syntax is called properly or not.
        """
        return len(ast.children) == 3 and isinstance(ast.children[1], Symbol)


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'let' symbol.
        """

        def add_var(node: Node, variable: Variable):
            match node:
                case ListNode(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        raise SyntaxError("root is not ListNode!")

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1]
                value = ast.children[2]
                new_variable = Variable(name.data, value)
                add_var(ast.parent, new_variable)
                return MacroCall(ast.row, ast.column, ast.children, 
                                 None, cls, cls.name, name, value)
            else:
                raise SyntaxError(("let only takes three arguments and name can't be ListNode\n"
                                   "Usage: `(let {name} {value})`\n"
                                   "TODO: Better Error message"))
        else:
            return ast


@dataclass
class Defun(Builtin):
    name = 'defun'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Checks if the syntax is called properly or not.
        """
        return len(ast.children) == 4 and isinstance(ast.children[1], Symbol) and \
                isinstance(ast.children[2], ListNode) and isinstance(ast.children[3], ListNode)



    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'let' symbol.
        """

        def add_var(node: Node, variable: Variable):
            match node:
                case ListNode(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        raise SyntaxError("root is not ListNode!")

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1].data
                arglist = ast.children[2]
                body = ast.children[3]
                body.scope = Scope()
                for node in arglist.children:
                    body.scope.add_variable(Func_Argument(node.data))
                func = Function(body.scope, body, arglist)
                new_variable = Variable(name, func)
                add_var(ast.parent, new_variable)
                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, arglist, body)
            else:
                raise SyntaxError(("Defun used improperly!\n"
                                   "Usage: `(defun {name} (args) (body))`\n"
                                   "Can not use String as name!\n"
                                   "TODO: Better Error message"))
        else:
            return ast


