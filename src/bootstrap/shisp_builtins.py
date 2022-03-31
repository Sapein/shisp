"""
This handles builtin values in Shisp

This includes 'meta-macros'.
"""


from functools import reduce
from dataclasses import dataclass
from typing import Optional


from shisp_ast.ast import Node, MacroCall, Expr, Symbol, ReturnNode, Comment, Atom
from shisp_ast.data_nodes import Builtin, Variable, Function, Scope, Func_Argument, PureFunction, Macro


@dataclass
class Let(Builtin):
    """
    This defines the built-in meta-macro, 'let' for Shisp.

    Let defines a variable and takes the following form:
        (let varname value)

    Let binds the variable to the nearest scope.
    """
    name = 'let'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        This validates the syntax for the the Metamacro.
        """
        return len(ast.children) == 3 and isinstance(ast.children[1], Symbol)


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 

        
        The ast node is the immediate parent of the let symbol.
        """

        def add_var(node: Node, variable: Variable):
            match node:
                case Expr(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        raise SyntaxError("root is not Expr!")

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1]
                value = ast.children[2]
                new_variable = Variable(name.data, value)
                add_var(ast.parent, new_variable)
                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, name, [value])
            else:
                raise SyntaxError(("let only takes three arguments and name can't be Expr\n"
                                   "Usage: `(let {name} {value})`\n"
                                   "TODO: Better Error message"))
        else:
            return ast


@dataclass
class Defun(Builtin):
    """
    This defines the built-in meta-macro defun, which defines functions
    at the closest scope.

    The form for defun is as follows:
        (defun func_name (arglist) body...)
    """
    name = 'defun'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        This validates the syntax for the the Metamacro.
        """
        return len(ast.children) >= 4 and isinstance(ast.children[1], Symbol) and \
                isinstance(ast.children[2], Expr)



    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 

        
        The ast node is the immediate parent of the defun symbol.
        """
        def add_var(node: Node, variable: Variable):
            match node:
                case Expr(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        raise SyntaxError("root is not Expr!")

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1].data
                arglist = ast.children[2]
                body = ast.children[3:]
                last_node = None
                for node in body:
                    if isinstance(node, Comment):
                        continue
                    last_node = node
                rnode = ReturnNode(last_node.row, last_node.column,
                                   [last_node], last_node.parent)
                body[body.index(last_node)] = rnode
                last_node.parent = rnode.parent
                body = Expr((body[0].row, body[-1].row), (body[0].column, body[-1].column),
                                body, ast.parent, scope=Scope())
                for child in body.children:
                    child.parent = body
                for node in arglist.children:
                    body.scope.add_variable(Func_Argument(node.data))
                func = Function(body.scope, body, arglist)
                new_variable = Variable(name, func)
                add_var(ast.parent, new_variable)
                macro_call =  MacroCall(ast.row, ast.column, ast.children[1:], 
                                       None, cls, cls.name, arglist, [body])
                body.parent = macro_call
                return macro_call

            else:
                raise SyntaxError(("Defun used improperly!\n"
                                   "Usage: `(defun {name} (args) (body))`\n"
                                   "Can not use String as name!\n"
                                   "TODO: Better Error message"))
        else:
            return ast


@dataclass
class Depun(Builtin):
    """
    This defines the built-in meta-macro depun, which defines pure-functions
    at the closest scope. Pure-functions *can not* modify global state for
    the rest of the program, only for itself and all functions it calls.

    The form for depun is as follows:
        (depun func_name (arglist) body...)
    """
    name = 'depun'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        This validates the syntax for the the Metamacro.
        """
        return len(ast.children) >= 4 and isinstance(ast.children[1], Symbol) and \
                isinstance(ast.children[2], Expr)



    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        The ast node is the immediate parent of the defun symbol.
        """

        def add_var(node: Node, variable: Variable):
            match node:
                case Expr(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        raise SyntaxError("root is not Expr!")

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1]
                name_data = ast.children[1].escape_data()
                arglist = ast.children[2]
                body = ast.children[3:]
                last_node = None
                for node in body:
                    if isinstance(node, Comment):
                        continue
                    last_node = node
                rnode = ReturnNode(last_node.row, last_node.column,
                                   [last_node], None)
                body[body.index(last_node)] = rnode
                last_node.parent = rnode
                body = Expr((body[0].row, body[-1].row), (body[0].column, body[-1].column),
                                body, ast.parent, scope=Scope())
                for child in body.children:
                    child.parent = body
                for node in arglist.children:
                    body.scope.add_variable(Func_Argument(node.data))
                func = PureFunction(body.scope, body, arglist)
                new_variable = Variable(name_data, func)
                add_var(ast.parent, new_variable)
                macro_call =  MacroCall(ast.row, ast.column, [name, arglist, body],
                                       None, cls, cls.name, arglist, [body])
                body.parent = macro_call
                return macro_call

            else:
                raise SyntaxError(("Depun used improperly!\n"
                                   "Usage: `(depun {name} (args) (body))`\n"
                                   "Can not use String as name!\n"
                                   "TODO: Better Error message"))
        else:
            return ast


@dataclass
class Shell_Literal(Builtin):
    """
    This defines the built-in meta-macro shell-literal which does not define
    anything, but is a form of 'quoting'. 

    Anything within the expression after shell-literal is then let unevaluated
    and is passed directly to the shell at compile time. If quoted or quasiquoted
    it will be treated as a regular form until it is evaluated or compiled.

    The form for shell-literal is as follows:
        (shell-literal literals...)
    """
    name = 'shell-literal'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Validates the syntax for the metamacro.
        """
        return len(ast.children) >= 2 and reduce(lambda x, y: x and y, 
                                                 [isinstance(c, Atom) for c in ast.children])


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'shell-literal' symbol.
        """
        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                literals = ast.children[1:]

                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, [], literals)
            else:
                raise SyntaxError(("shell-literal takes at least two arguments, and arguments must be atoms!\n"
                                   "Usage: `(shell-literals literal...)`\n"
                                   "TODO: Better Error message"))
        else:
            return ast


@dataclass
class Quote(Builtin):
    """
    This defines the built-in meta-macro 'quote'.

    The next Atom or Expr after the quote is then passed literally to the program.
    It remains this way until evaluated. 

    The forms for quote is as follows:
        (quote literal)
        'literal
    """
    name = 'quote'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Checks if the syntax is called properly or not.
        """
        return len(ast.children) == 2 


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'quote' symbol.
        """
        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                literals = ast.children[1:]

                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, [], literals)
            else:
                raise SyntaxError(("quote takes at least two arguments, and arguments must be atoms!\n"
                                   "Usage: `(quote literal...)`\n"
                                   "TODO: Better Error message"))
        else:
            return ast

@dataclass
class QuasiQuote(Builtin):
    """
    This defines the built-in meta-macro 'quasiquote'.

    The next Atom or Expr after the quasi-quote is then returned literally to the program.
    It remains this way until evaluated. Items within a quasiquote that are unquoted or
    unquote-spliced are evaluated *prior* to returning the literal, after which it acts
    as if it were quoted.

    The forms for quote is as follows:
        (quasiquote literal)
        `literal
    """
    name = 'quasiquote'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Validates the snytax for the metamacro
        """
        return len(ast.children) == 2 


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'quasi-quote'' symbol.
        """
        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                literals = ast.children[1:]

                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, [], literals)
            else:
                raise SyntaxError(("quasi-quote takes at least two arguments\n"
                                   "Usage: `(quasi-quote literal...)`\n"
                                   "TODO: Better Error message"))
        else:
            return ast

@dataclass
class Unquote(Builtin):
    """
    This defines the built-in meta-macro 'unquote'.

    The next atom or Expr after the unquote is evaluted and then returned as if it wasn't there.
    IF the Unquote is within a quasiquoted Expression then the result will be returned and put
    into the quoted Expression.

    The forms for quote is as follows:
        (unquote literal)
        ,literal
    """
    name = 'unquote'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Validates if the syntax for the meta-macro is correct.
        """
        return len(ast.children) == 2 


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'unquote' symbol.
        """
        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, [], ast.children[1])
            else:
                raise SyntaxError(("unquote takes at least two arguments, and arguments must be atoms!\n"
                                   "Usage: `(unquote literal...)`\n"
                                   "TODO: Better Error message"))
        else:
            return ast

@dataclass
class Unquote_Splice(Builtin):
    """
    This defines the built-in meta-macro 'unquote-splice'.

    The next Atom or Expr after the unquote-splice is evaluated, and the result is then subsituted
    into the list in the spot where the unquote-splice occurred..

    The forms for quote is as follows:
        (unquote-splice literal)
        ,@literal
    """
    name = 'unquote-splice'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Validates if the syntax for the meta-macro is correct.
        """
        return len(ast.children) == 2 


    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'. 
        
        the 'ast' is the immediate parent of the 'unquote-splice' symbol.
        """
        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                return MacroCall(ast.row, ast.column, ast.children[1:], 
                                 None, cls, cls.name, [], ast.children[1])
            else:
                raise SyntaxError(("unquote-splice takes at least two arguments, and arguments must be atoms!\n"
                                   "Usage: `(unquote-splice literal...)`\n"
                                   "TODO: Better Error message"))
        else:
            return ast



@dataclass
class Demac(Builtin):
    """
    This defines the built-in meta-macro 'demac'.

    A Macro is defined at the next highest scope, much like a function. The macro is
    expanded at compile-time and does not, necessarily, get compiled to Shell Code.
    
    What the macro returns is then inserted in place of the macro call.

    The form for defmac is as follows:
        (defmac macroname (arglist) body...)
    """
    name = 'demac'


    @staticmethod
    def valid_syntax(ast: Node) -> bool:
        """
        Checks if the syntax is called properly or not.
        """
        return len(ast.children) >= 4 and isinstance(ast.children[1], Symbol) and \
                isinstance(ast.children[2], Expr)



    @classmethod
    def meta_eval(cls, ast: Node) -> MacroCall:
        """
        This evaluates the 'metamacro'.

        the 'ast' is the immediate parent of the 'demac' symbol.
        """

        def add_var(node: Node, variable: Variable):
            match node:
                case Expr(_):
                    try:
                        node.scope.add_variable(variable)
                    except AttributeError:
                        add_var(node.parent, variable)
                case Node(_):
                    if node.parent is not None:
                        add_var(node.parent)
                    else:
                        err = ("The root node is not an Expr (as it should be)!\n"
                               "If you managed to find this, this is a compiler bug.\n"
                               "Please report it to the maintainers!"
                              )
                        raise SyntaxError(err)

        if cls.is_call(ast):
            if cls.valid_syntax(ast):
                name = ast.children[1].data
                arglist = ast.children[2]
                body = ast.children[3:]
                last_node = None
                for node in body:
                    if isinstance(node, Comment):
                        continue
                    last_node = node
                rnode = ReturnNode(last_node.row, last_node.column,
                                   [last_node], last_node.parent)
                body[body.index(last_node)] = rnode
                last_node.parent = rnode.parent
                body = Expr((body[0].row, body[-1].row), (body[0].column, body[-1].column),
                                body, ast.parent, scope=Scope())
                for child in body.children:
                    child.parent = body
                for node in arglist.children:
                    body.scope.add_variable(Func_Argument(node.data))
                func = Macro(body.scope, body, arglist)
                new_variable = Variable(name, func)
                add_var(ast.parent, new_variable)
                macro_call =  MacroCall(ast.row, ast.column, ast.children[1:],
                                       None, cls, cls.name, arglist, [body])
                body.parent = macro_call
                return macro_call

            else:
                raise SyntaxError(("Demac used improperly!\n"
                                   "Usage: `(demac {name} (args) (body))`\n"
                                   "Can not use String as name!\n"
                                   "TODO: Better Error message"))
        else:
            return ast
