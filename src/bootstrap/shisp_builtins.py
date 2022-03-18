"""
This handles the coding for shisp-builtins for compilation
purposes
"""

from scoping import Builtin, Variable, Function, check_children
from parser import List, Scope, Comment, MacroCall, EndList
from dataclasses import dataclass
from compiler import handle_list


@dataclass
class Let(Builtin):
    """
    This defines a basic little builtin for 
    let to allow for variable definition.
    """
    def find_scope(self, node):
        match node.parent:
            case List(_):
                return node.parent.scope
            case Comment(_):
                return None
            case Node(_):
                return node.parent

    def emit(self, macro: MacroCall) -> str:
        return "{name}={val}".format(name=macro.args[0],
                                     val=macro.body.data)

    def meta_emit(self, node) -> str:
        return MacroCall(node.row, node.column, node.children,
                  node.parent, self, "let", [node.parent.children[2].data],
                  node.parent.children[4])

    def meta_eval(self, node, scopes=None):
        """
        Evaluate when parsing. 
        Takes in the node that is used with let.
        """
        #(let {NAME} {BODY})
        name = node.parent.children[2].data
        body = node.parent.children[4]
        var = Variable(node.row, node.column, None, None, name, [body])
        scope_p = node.parent.parent
        while True:
            scope_p = self.find_scope(node.parent)
            if isinstance(scope_p, Scope):
                scope_p.add_variable(var)
                break
            elif isinstance(scope_p, Comment):
                break


@dataclass
class Defun(Builtin):
    name = 'defun'
    def find_scope(self, node):
        match node.parent:
            case List(_):
                return node.parent.scope
            case Comment(_):
                return None
            case Node(_):
                return node.parent

    def emit(self, macro: MacroCall) -> str:
        arglist = ''
        for i, arg in enumerate(macro.args[1].children, 1):
            if isinstance(arg, EndList):
                break
            arglist = ('{}{name}="${{{n}}}"\n'
                      ).format(arglist,
                               fn=macro.args[0],
                               name=arg.data,
                               n=str(i))

        body = ''
        for child in macro.body.children:
            match child:
                case List(_):
                    body = '{}  {}\n'.format(body, handle_list(child))

        return ("{name}() {{\n"
                "{arglist}"
                "{body}\n"
                "}}\n").format(name=macro.args[0],
                              arglist=arglist,
                              body=body
                             )

    def meta_emit(self, node) -> str:
        return MacroCall(node.row, node.column, node.children,
                  node.parent, self, "defun", [node.parent.children[2].data, node.parent.children[4]],
                  node.parent.children[6])

    def meta_eval(self, node, scopes=None):
        #(defun name (arglist) (body))
        name = node.parent.children[2].data
        arglist = node.parent.children[4]
        body = node.parent.children[6]
        func = Function(node.row, node.column, body, None, arglist)
        Function.scope=Scope(0,0)
        Function.scope.variables = {k.data:None for k in arglist.children}
        var = Variable(node.row, node.column, None, None, name, func)
        scope_p = node.parent.parent
        while True:
            scope_p = self.find_scope(node.parent)
            if isinstance(scope_p, Scope):
                scope_p.add_variable(var)
                break
            elif isinstance(scope_p, Comment):
                break
        check_children(body, [body.scope, *scopes])

class depun:
    name = 'depun'

class read:
    name = 'read'

class eval:
    name = 'eval'

class _print:
    name = 'print'
